from __future__ import annotations

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.services.auth import (
    get_current_user,
    require_admin,
    list_users,
    update_user_role,
    deactivate_user,
    UserRole,
)

router = APIRouter(prefix="/admin", tags=["admin"])

templates = Jinja2Templates(directory="app/web_templates")


@router.get("/users", response_class=HTMLResponse)
async def users_list(request: Request, error: str = None, message: str = None):
    try:
        current_user = await require_admin(request)
    except Exception:
        return RedirectResponse(url="/auth/login", status_code=303)

    users = await list_users(current_user)

    return templates.TemplateResponse(
        "admin_users.html",
        {
            "request": request,
            "title": "Quan ly nguoi dung",
            "users": users,
            "current_user": current_user,
            "error": error,
            "message": message,
            "roles": [r.value for r in UserRole],
        },
    )


@router.post("/users/{user_id}/role")
async def change_user_role(
    request: Request,
    user_id: str,
    role: str = Form(...),
):
    try:
        current_user = await require_admin(request)
    except Exception:
        return JSONResponse({"success": False, "error": "Unauthorized"}, status_code=401)

    try:
        new_role = UserRole(role)
    except ValueError:
        return JSONResponse({"success": False, "error": "Invalid role"}, status_code=400)

    result = await update_user_role(user_id, new_role, current_user)

    if result["success"]:
        return RedirectResponse(
            url="/admin/users?message=Da cap nhat quyen nguoi dung",
            status_code=303,
        )
    return RedirectResponse(
        url=f"/admin/users?error={result['error']}",
        status_code=303,
    )


@router.post("/users/{user_id}/deactivate")
async def deactivate_user_route(request: Request, user_id: str):
    try:
        current_user = await require_admin(request)
    except Exception:
        return JSONResponse({"success": False, "error": "Unauthorized"}, status_code=401)

    result = await deactivate_user(user_id, current_user)

    if result["success"]:
        return JSONResponse({"success": True, "message": "Da vo hieu hoa tai khoan"})
    return JSONResponse({"success": False, "error": result["error"]}, status_code=400)


@router.get("/audit-logs", response_class=HTMLResponse)
async def audit_logs(request: Request):
    try:
        current_user = await require_admin(request)
    except Exception:
        return RedirectResponse(url="/auth/login", status_code=303)

    from app.services.database import AuditLogDB
    logs = AuditLogDB.get_recent(limit=200)

    return templates.TemplateResponse(
        "admin_audit_logs.html",
        {
            "request": request,
            "title": "Nhat ky thay doi",
            "logs": logs,
            "current_user": current_user,
        },
    )
