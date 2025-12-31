from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.auth import PERMISSIONS, get_current_user, require_permission
from app.db import session_scope
from app.db_models import UserPermissionRow, UserRow
from app.utils import get_breadcrumbs


router = APIRouter()


@router.get("/admin/permissions", response_class=HTMLResponse)
def permissions_matrix(
    request: Request,
    error: str | None = None,
    message: str | None = None,
    user: UserRow = Depends(require_permission("admin.users.manage")),
):
    templates = request.app.state.templates

    with session_scope() as db:
        users = db.query(UserRow).order_by(UserRow.role.asc(), UserRow.username.asc()).all()
        overrides = db.query(UserPermissionRow).all()

    overrides_by_user: dict[str, dict[str, int]] = {}
    for o in overrides:
        overrides_by_user.setdefault(o.username, {})[o.permission] = 1 if o.allowed else 0

    return templates.TemplateResponse(
        "admin_permissions.html",
        {
            "request": request,
            "title": "Ma trận phân quyền",
            "error": error,
            "message": message,
            "users": users,
            "permission_groups": PERMISSIONS,
            "overrides": overrides_by_user,
            "current_user": {"username": user.username, "role": user.role},
            "breadcrumbs": get_breadcrumbs(request.url.path),
        },
    )


@router.post("/admin/permissions")
def permissions_save(
    request: Request,
    target_username: str = Form(...),
    perms_allow: list[str] = Form(default=[]),
    perms_deny: list[str] = Form(default=[]),
    user: UserRow = Depends(require_permission("admin.users.manage")),
):
    try:
        uname = (target_username or "").strip().lower()
        if not uname:
            raise ValueError("Thiếu username")

        allow_set = {p.strip() for p in (perms_allow or []) if (p or "").strip()}
        deny_set = {p.strip() for p in (perms_deny or []) if (p or "").strip()}

        if allow_set & deny_set:
            raise ValueError("Không thể vừa Allow vừa Deny cùng một permission")

        all_known = {p for group in PERMISSIONS.values() for p in group}
        for p in list(allow_set) + list(deny_set):
            if p not in all_known:
                raise ValueError(f"Permission không hợp lệ: {p}")

        with session_scope() as db:
            exists = db.query(UserRow).filter(UserRow.username == uname).first()
            if exists is None:
                raise ValueError("User không tồn tại")

            db.query(UserPermissionRow).filter(UserPermissionRow.username == uname).delete()

            for p in sorted(allow_set):
                db.add(UserPermissionRow(username=uname, permission=p, allowed=1))
            for p in sorted(deny_set):
                db.add(UserPermissionRow(username=uname, permission=p, allowed=0))

        return RedirectResponse(
            url=f"/admin/permissions?message=Đã lưu quyền cho {uname}",
            status_code=303,
        )

    except Exception as e:
        msg = f"{type(e).__name__}: {e}" if str(e) else f"{type(e).__name__}"
        return RedirectResponse(url=f"/admin/permissions?error={msg}", status_code=303)
