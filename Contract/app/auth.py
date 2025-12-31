from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import base64

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBasic
from starlette import status

from app.db import session_scope
from app.db_models import UserPermissionRow, UserRow


_basic_auth = HTTPBasic()


PERMISSIONS: dict[str, list[str]] = {
    "Portal": [
        "portal.access",
    ],
    "Contracts": [
        "contracts.read",
        "contracts.create",
        "contracts.update",
        "contracts.delete",
    ],
    "Annexes": [
        "annexes.read",
        "annexes.create",
        "annexes.update",
        "annexes.delete",
    ],
    "Catalogue": [
        "catalogue.upload",
    ],
    "Works": [
        "works.read",
        "works.import",
    ],
    "Reports": [
        "reports.view",
        "reports.export",
    ],
    "Admin": [
        "admin.users.manage",
        "admin.system.manage",
        "admin.ops.view",
    ],
}


ROLE_DEFAULT_PERMISSIONS: dict[str, set[str]] = {
    "admin": {p for group in PERMISSIONS.values() for p in group},
    "mod": {
        "portal.access",
        "contracts.read",
        "contracts.create",
        "contracts.update",
        "contracts.delete",
        "annexes.read",
        "annexes.create",
        "annexes.update",
        "annexes.delete",
        "catalogue.upload",
        "works.read",
        "works.import",
        "reports.view",
        "reports.export",
        "admin.users.manage",
    },
    "user": {
        "portal.access",
        "contracts.read",
        "annexes.read",
        "catalogue.upload",
        "works.read",
        "works.import",
        "reports.view",
    },
}


def _hash_password(password: str, *, salt_hex: str, iterations: int = 200_000) -> str:
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt_hex),
        iterations,
    )
    return dk.hex()


def _verify_password(password: str, *, salt_hex: str, expected_hash_hex: str) -> bool:
    calc = _hash_password(password, salt_hex=salt_hex)
    return hmac.compare_digest(calc, expected_hash_hex)


def set_user_password(*, user: UserRow, password: str) -> None:
    salt = secrets.token_bytes(16).hex()
    user.password_salt = salt
    user.password_hash = _hash_password(password, salt_hex=salt)


def verify_user_password(*, user: UserRow, password: str) -> bool:
    return _verify_password(password, salt_hex=user.password_salt, expected_hash_hex=user.password_hash)


def verify_username_password(*, username: str, password: str) -> UserRow | None:
    uname = (username or "").strip().lower()
    if not uname or not password:
        return None

    with session_scope() as db:
        user = db.query(UserRow).filter(UserRow.username == uname).first()
    if user is None:
        return None
    if not verify_user_password(user=user, password=password):
        return None
    return user


def get_permissions_for_user(*, user: UserRow) -> set[str]:
    perms = set(ROLE_DEFAULT_PERMISSIONS.get(user.role, set()))

    with session_scope() as db:
        overrides = (
            db.query(UserPermissionRow)
            .filter(UserPermissionRow.username == user.username)
            .all()
        )

    for o in overrides:
        if o.allowed:
            perms.add(o.permission)
        else:
            perms.discard(o.permission)
    return perms


def has_permission(*, user: UserRow, permission: str) -> bool:
    p = (permission or "").strip()
    if not p:
        return False
    perms = get_permissions_for_user(user=user)
    return p in perms


def _upsert_system_user(*, username: str, role: str, password: str) -> None:
    with session_scope() as db:
        existing = db.query(UserRow).filter(UserRow.username == username).first()
        if existing is None:
            salt = secrets.token_bytes(16).hex()
            db.add(
                UserRow(
                    username=username,
                    role=role,
                    password_salt=salt,
                    password_hash=_hash_password(password, salt_hex=salt),
                )
            )
            return

        # Ensure role matches (system usernames are fixed)
        existing.role = role

        # Only set password from env on demand (avoid silently overwriting passwords)
        if password:
            set_user_password(user=existing, password=password)


def ensure_default_users() -> None:
    admin_pwd_env = os.environ.get("CONTRACT_ADMIN_PASSWORD")
    mod_pwd_env = os.environ.get("CONTRACT_MOD_PASSWORD")

    # When creating missing system users, use env password if provided, otherwise use default.
    # When system users already exist, only reset password if env password is explicitly provided.
    admin_pwd_for_create = admin_pwd_env or "Vcpmc@123"
    mod_pwd_for_create = mod_pwd_env or "mod123"

    with session_scope() as db:
        admin_user = db.query(UserRow).filter(UserRow.username == "admin").first()
        mod_user = db.query(UserRow).filter(UserRow.username == "mod").first()

        if admin_user is None:
            salt = secrets.token_bytes(16).hex()
            db.add(
                UserRow(
                    username="admin",
                    role="admin",
                    password_salt=salt,
                    password_hash=_hash_password(admin_pwd_for_create, salt_hex=salt),
                )
            )
        else:
            admin_user.role = "admin"
            if admin_pwd_env:
                set_user_password(user=admin_user, password=admin_pwd_env)

        if mod_user is None:
            salt = secrets.token_bytes(16).hex()
            db.add(
                UserRow(
                    username="mod",
                    role="mod",
                    password_salt=salt,
                    password_hash=_hash_password(mod_pwd_for_create, salt_hex=salt),
                )
            )
        else:
            mod_user.role = "mod"
            if mod_pwd_env:
                set_user_password(user=mod_user, password=mod_pwd_env)


def get_current_user(request: Request) -> UserRow:
    session_username = None
    try:
        session_username = (request.session.get("username") or "").strip().lower()  # type: ignore[attr-defined]
    except Exception:
        session_username = None

    if session_username:
        with session_scope() as db:
            user = db.query(UserRow).filter(UserRow.username == session_username).first()
        if user is not None:
            return user

    auth = (request.headers.get("authorization") or "").strip()
    if auth.lower().startswith("basic "):
        try:
            raw = base64.b64decode(auth.split(" ", 1)[1]).decode("utf-8")
            username, password = raw.split(":", 1)
        except Exception:
            username, password = "", ""
        user = verify_username_password(username=username, password=password)
        if user is not None:
            return user

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


def require_role(*allowed_roles: str):
    def _dep(user: UserRow = Depends(get_current_user)) -> UserRow:
        if user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user

    return _dep


def require_any_permission(*required: str):
    def _dep(user: UserRow = Depends(get_current_user)) -> UserRow:
        needed = [p.strip() for p in required if (p or "").strip()]
        if not needed:
            return user

        perms = get_permissions_for_user(user=user)
        ok = any(p in perms for p in needed)
        if not ok:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user

    return _dep


def require_permission(*required: str):
    def _dep(user: UserRow = Depends(get_current_user)) -> UserRow:
        needed = [p.strip() for p in required if (p or "").strip()]
        if not needed:
            return user

        perms = get_permissions_for_user(user=user)
        ok = all(p in perms for p in needed)
        if not ok:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user

    return _dep
