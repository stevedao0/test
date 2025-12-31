from __future__ import annotations

import secrets

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.auth import _hash_password, get_current_user, require_any_permission, require_permission, set_user_password, verify_user_password
from app.db import session_scope
from app.db_models import UserRow
from app.utils import get_breadcrumbs


router = APIRouter()


def _is_vcpmc_email(username: str) -> bool:
    u = (username or "").strip().lower()
    return u.endswith("@vcpmc.org") and "@" in u


@router.get("/account/password", response_class=HTMLResponse)
def account_password_form(
    request: Request,
    error: str | None = None,
    message: str | None = None,
    user: UserRow = Depends(get_current_user),
):
    templates = request.app.state.templates
    return templates.TemplateResponse(
        "account_password.html",
        {
            "request": request,
            "title": "Đổi mật khẩu",
            "error": error,
            "message": message,
            "username": user.username,
            "role": user.role,
            "breadcrumbs": get_breadcrumbs(request.url.path),
        },
    )


@router.post("/account/password")
def account_password_submit(
    request: Request,
    old_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    user: UserRow = Depends(get_current_user),
):
    try:
        if not verify_user_password(user=user, password=old_password):
            raise ValueError("Mật khẩu hiện tại không đúng")

        if not new_password or len(new_password) < 6:
            raise ValueError("Mật khẩu mới phải có ít nhất 6 ký tự")

        if new_password != confirm_password:
            raise ValueError("Xác nhận mật khẩu không khớp")

        with session_scope() as db:
            db_user = db.query(UserRow).filter(UserRow.username == user.username).first()
            if db_user is None:
                raise ValueError("Không tìm thấy user")
            set_user_password(user=db_user, password=new_password)

        return RedirectResponse(url="/account/password?message=Đổi mật khẩu thành công", status_code=303)

    except Exception as e:
        msg = f"{type(e).__name__}: {e}" if str(e) else f"{type(e).__name__}"
        return RedirectResponse(url=f"/account/password?error={msg}", status_code=303)


@router.get("/admin/users", response_class=HTMLResponse)
def admin_users_list(
    request: Request,
    error: str | None = None,
    message: str | None = None,
    user: UserRow = Depends(require_permission("admin.users.manage")),
):
    templates = request.app.state.templates

    with session_scope() as db:
        users = db.query(UserRow).order_by(UserRow.role.asc(), UserRow.username.asc()).all()

    return templates.TemplateResponse(
        "admin_users.html",
        {
            "request": request,
            "title": "Quản lý tài khoản",
            "error": error,
            "message": message,
            "rows": users,
            "current_user": {"username": user.username, "role": user.role},
            "breadcrumbs": get_breadcrumbs(request.url.path),
        },
    )


@router.post("/admin/users")
def admin_users_create(
    request: Request,
    username: str = Form(...),
    password: str = Form(""),
    user: UserRow = Depends(require_permission("admin.users.manage")),
):
    try:
        uname = (username or "").strip().lower()
        if uname in ("admin", "mod"):
            raise ValueError("Không tạo username trùng admin/mod")
        if not _is_vcpmc_email(uname):
            raise ValueError("Username phải là email @vcpmc.org")

        pwd = (password or "").strip() or secrets.token_urlsafe(10)
        if len(pwd) < 6:
            raise ValueError("Mật khẩu phải có ít nhất 6 ký tự")

        with session_scope() as db:
            exists = db.query(UserRow).filter(UserRow.username == uname).first()
            if exists is not None:
                raise ValueError("User đã tồn tại")

            salt = secrets.token_bytes(16).hex()
            db.add(
                UserRow(
                    username=uname,
                    role="user",
                    password_salt=salt,
                    password_hash=_hash_password(pwd, salt_hex=salt),
                )
            )

        return RedirectResponse(
            url=f"/admin/users?message=Đã tạo user {uname} (mật khẩu: {pwd})",
            status_code=303,
        )

    except Exception as e:
        msg = f"{type(e).__name__}: {e}" if str(e) else f"{type(e).__name__}"
        return RedirectResponse(url=f"/admin/users?error={msg}", status_code=303)


@router.post("/admin/system_accounts/password")
def admin_set_system_password(
    request: Request,
    target_username: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    user: UserRow = Depends(require_permission("admin.system.manage")),
):
    try:
        target = (target_username or "").strip().lower()
        if target not in ("admin", "mod"):
            raise ValueError("Chỉ cho phép đổi mật khẩu admin/mod")

        if not new_password or len(new_password) < 6:
            raise ValueError("Mật khẩu phải có ít nhất 6 ký tự")
        if new_password != confirm_password:
            raise ValueError("Xác nhận mật khẩu không khớp")

        with session_scope() as db:
            db_user = db.query(UserRow).filter(UserRow.username == target).first()
            if db_user is None:
                raise ValueError("Không tìm thấy tài khoản")
            set_user_password(user=db_user, password=new_password)

        return RedirectResponse(url=f"/admin/users?message=Đã đổi mật khẩu cho {target}", status_code=303)

    except Exception as e:
        msg = f"{type(e).__name__}: {e}" if str(e) else f"{type(e).__name__}"
        return RedirectResponse(url=f"/admin/users?error={msg}", status_code=303)


@router.post("/admin/users/reset_password")
def admin_users_reset_password(
    request: Request,
    username: str = Form(...),
    new_password: str = Form(""),
    user: UserRow = Depends(require_permission("admin.users.manage")),
):
    try:
        uname = (username or "").strip().lower()
        if uname in ("admin", "mod"):
            raise ValueError("Không reset mật khẩu qua màn này cho admin/mod")
        if not _is_vcpmc_email(uname):
            raise ValueError("Username phải là email @vcpmc.org")

        pwd = (new_password or "").strip() or secrets.token_urlsafe(10)
        if len(pwd) < 6:
            raise ValueError("Mật khẩu phải có ít nhất 6 ký tự")

        with session_scope() as db:
            db_user = db.query(UserRow).filter(UserRow.username == uname).first()
            if db_user is None:
                raise ValueError("Không tìm thấy user")
            if db_user.role != "user":
                raise ValueError("Chỉ reset mật khẩu cho role user")
            set_user_password(user=db_user, password=pwd)

        return RedirectResponse(
            url=f"/admin/users?message=Đã reset mật khẩu cho {uname} (mật khẩu: {pwd})",
            status_code=303,
        )

    except Exception as e:
        msg = f"{type(e).__name__}: {e}" if str(e) else f"{type(e).__name__}"
        return RedirectResponse(url=f"/admin/users?error={msg}", status_code=303)
