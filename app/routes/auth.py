from __future__ import annotations

from fastapi import APIRouter, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.auth import (
    login_user,
    logout_user,
    signup_user,
    get_current_user,
    SESSION_KEY,
    REFRESH_KEY,
)

router = APIRouter(prefix="/auth", tags=["auth"])

templates = Jinja2Templates(directory="app/web_templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = None, message: str = None):
    user = await get_current_user(request)
    if user:
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "title": "Dang nhap",
            "error": error,
            "message": message,
        },
    )


@router.post("/login")
async def login_submit(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
):
    result = await login_user(email, password)

    if not result["success"]:
        return RedirectResponse(
            url=f"/auth/login?error={result['error']}",
            status_code=303,
        )

    redirect = RedirectResponse(url="/", status_code=303)
    redirect.set_cookie(
        key=SESSION_KEY,
        value=result["access_token"],
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )
    redirect.set_cookie(
        key=REFRESH_KEY,
        value=result["refresh_token"],
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 30,
    )
    return redirect


@router.get("/logout")
async def logout(request: Request):
    token = request.cookies.get(SESSION_KEY)
    if token:
        await logout_user(token)

    redirect = RedirectResponse(url="/auth/login", status_code=303)
    redirect.delete_cookie(SESSION_KEY)
    redirect.delete_cookie(REFRESH_KEY)
    return redirect


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, error: str = None):
    user = await get_current_user(request)
    if user:
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "title": "Dang ky",
            "error": error,
        },
    )


@router.post("/register")
async def register_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    full_name: str = Form(""),
):
    if password != password_confirm:
        return RedirectResponse(
            url="/auth/register?error=Mat khau khong khop",
            status_code=303,
        )

    if len(password) < 6:
        return RedirectResponse(
            url="/auth/register?error=Mat khau phai co it nhat 6 ky tu",
            status_code=303,
        )

    result = await signup_user(email, password, full_name)

    if not result["success"]:
        return RedirectResponse(
            url=f"/auth/register?error={result['error']}",
            status_code=303,
        )

    return RedirectResponse(
        url="/auth/login?message=Dang ky thanh cong. Vui long dang nhap.",
        status_code=303,
    )
