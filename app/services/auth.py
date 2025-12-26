from __future__ import annotations

from typing import Optional
from dataclasses import dataclass
from enum import Enum

from fastapi import Request, HTTPException, status
from gotrue.errors import AuthApiError

from app.core.supabase import get_supabase


class UserRole(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


@dataclass
class CurrentUser:
    id: str
    email: str
    full_name: Optional[str]
    role: UserRole
    is_active: bool


SESSION_KEY = "supabase_access_token"
REFRESH_KEY = "supabase_refresh_token"


async def signup_user(email: str, password: str, full_name: str = "") -> dict:
    supabase = get_supabase()
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {"full_name": full_name}
            }
        })
        if response.user:
            return {
                "success": True,
                "user_id": response.user.id,
                "email": response.user.email,
            }
        return {"success": False, "error": "Signup failed"}
    except AuthApiError as e:
        return {"success": False, "error": str(e)}


async def login_user(email: str, password: str) -> dict:
    supabase = get_supabase()
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if response.user and response.session:
            return {
                "success": True,
                "user_id": response.user.id,
                "email": response.user.email,
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
            }
        return {"success": False, "error": "Login failed"}
    except AuthApiError as e:
        error_msg = str(e)
        if "Invalid login credentials" in error_msg:
            return {"success": False, "error": "Email hoac mat khau khong dung"}
        return {"success": False, "error": error_msg}


async def logout_user(access_token: str) -> dict:
    supabase = get_supabase()
    try:
        supabase.auth.sign_out()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_current_user_from_token(access_token: str) -> Optional[CurrentUser]:
    if not access_token:
        return None

    supabase = get_supabase()
    try:
        user_response = supabase.auth.get_user(access_token)
        if not user_response or not user_response.user:
            return None

        user = user_response.user
        profile = supabase.table("profiles").select("*").eq("id", user.id).maybeSingle().execute()

        role = UserRole.VIEWER
        is_active = True
        full_name = ""

        if profile.data:
            role_str = profile.data.get("role", "viewer")
            role = UserRole(role_str)
            is_active = profile.data.get("is_active", True)
            full_name = profile.data.get("full_name", "")

        return CurrentUser(
            id=user.id,
            email=user.email or "",
            full_name=full_name,
            role=role,
            is_active=is_active,
        )
    except Exception:
        return None


def get_session_token(request: Request) -> Optional[str]:
    return request.cookies.get(SESSION_KEY)


async def get_current_user(request: Request) -> Optional[CurrentUser]:
    token = get_session_token(request)
    if not token:
        return None
    return await get_current_user_from_token(token)


async def require_auth(request: Request) -> CurrentUser:
    user = await get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    return user


async def require_role(request: Request, allowed_roles: list[UserRole]) -> CurrentUser:
    user = await require_auth(request)
    if user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    return user


async def require_editor(request: Request) -> CurrentUser:
    return await require_role(request, [UserRole.ADMIN, UserRole.EDITOR])


async def require_admin(request: Request) -> CurrentUser:
    return await require_role(request, [UserRole.ADMIN])


async def update_user_role(user_id: str, new_role: UserRole, admin_user: CurrentUser) -> dict:
    if admin_user.role != UserRole.ADMIN:
        return {"success": False, "error": "Only admins can change roles"}

    supabase = get_supabase()
    try:
        supabase.table("profiles").update({
            "role": new_role.value
        }).eq("id", user_id).execute()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def list_users(admin_user: CurrentUser) -> list[dict]:
    if admin_user.role != UserRole.ADMIN:
        return []

    supabase = get_supabase()
    try:
        response = supabase.table("profiles").select("*").execute()
        return response.data or []
    except Exception:
        return []


async def deactivate_user(user_id: str, admin_user: CurrentUser) -> dict:
    if admin_user.role != UserRole.ADMIN:
        return {"success": False, "error": "Only admins can deactivate users"}

    if user_id == admin_user.id:
        return {"success": False, "error": "Cannot deactivate yourself"}

    supabase = get_supabase()
    try:
        supabase.table("profiles").update({
            "is_active": False
        }).eq("id", user_id).execute()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
