from __future__ import annotations

import hashlib
import hmac
import os
import secrets

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette import status

from app.db import session_scope
from app.db_models import UserRow


_basic_auth = HTTPBasic()


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


def ensure_default_users() -> None:
    admin_pwd = os.environ.get("CONTRACT_ADMIN_PASSWORD")
    mod_pwd = os.environ.get("CONTRACT_MOD_PASSWORD")

    if not admin_pwd:
        admin_pwd = "admin123"
    if not mod_pwd:
        mod_pwd = "mod123"

    with session_scope() as db:
        has_any = db.query(UserRow).first() is not None
        if has_any:
            return

        admin_salt = secrets.token_bytes(16).hex()
        mod_salt = secrets.token_bytes(16).hex()

        db.add(
            UserRow(
                username="admin",
                role="admin",
                password_salt=admin_salt,
                password_hash=_hash_password(admin_pwd, salt_hex=admin_salt),
            )
        )
        db.add(
            UserRow(
                username="mod",
                role="mod",
                password_salt=mod_salt,
                password_hash=_hash_password(mod_pwd, salt_hex=mod_salt),
            )
        )


def get_current_user(credentials: HTTPBasicCredentials = Depends(_basic_auth)) -> UserRow:
    with session_scope() as db:
        user = db.query(UserRow).filter(UserRow.username == credentials.username).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )

    if not _verify_password(
        credentials.password,
        salt_hex=user.password_salt,
        expected_hash_hex=user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )

    return user


def require_role(*allowed_roles: str):
    def _dep(user: UserRow = Depends(get_current_user)) -> UserRow:
        if user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user

    return _dep
