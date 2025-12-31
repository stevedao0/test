from __future__ import annotations

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.auth import verify_username_password
from app.utils import get_breadcrumbs


router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request, error: str | None = None, message: str | None = None, next: str | None = None):
    templates = request.app.state.templates
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "title": "Đăng nhập",
            "error": error,
            "message": message,
            "next": next or "",
            "breadcrumbs": get_breadcrumbs(request.url.path),
        },
    )


@router.post("/login")
def login_submit(
    request: Request,
    username: str = Form(""),
    password: str = Form(""),
    next: str = Form(""),
):
    try:
        uname = (username or "").strip().lower()
        if not uname or not password:
            raise ValueError("Vui lòng nhập username và mật khẩu")

        user = verify_username_password(username=uname, password=password)
        if user is None:
            raise ValueError("Sai username hoặc mật khẩu")

        request.session["username"] = user.username

        target = (next or "").strip()
        if target and target.startswith("/") and not target.startswith("//"):
            return RedirectResponse(url=target, status_code=303)
        return RedirectResponse(url="/dashboard", status_code=303)
    except Exception as e:
        msg = f"{type(e).__name__}: {e}" if str(e) else f"{type(e).__name__}"
        q_next = (next or "").strip()
        url = f"/login?error={msg}"
        if q_next:
            url += f"&next={q_next}"
        return RedirectResponse(url=url, status_code=303)


@router.get("/logout")
def logout(request: Request):
    try:
        request.session.clear()
    except Exception:
        pass
    return RedirectResponse(url="/login?message=Đã đăng xuất", status_code=303)
