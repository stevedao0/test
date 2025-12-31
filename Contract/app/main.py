from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path
from urllib.parse import quote

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile, Response
from fastapi.encoders import jsonable_encoder
from starlette import status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import (
    STORAGE_DIR,
    STORAGE_EXCEL_DIR,
    UI_STATIC_DIR,
    UI_TEMPLATES_DIR,
    WEB_TEMPLATES_DIR,
)

from app.db import DB_PATH, engine
from app.db_models import Base, UserRow
from app.auth import ensure_default_users, get_current_user, get_permissions_for_user, require_role
from app.db_ops import (
    _db_available,
    _rows_from_db,
)

from app.routers.admin import router as admin_router
from app.routers.storage import router as storage_router
from app.routers.catalogue import router as catalogue_router
from app.routers.works import router as works_router
from app.routers.documents import router as documents_router
from app.routers.contracts import router as contracts_router
from app.routers.annexes import router as annexes_router
from app.routers.users import router as users_router
from app.routers.reports import router as reports_router
from app.routers.search import router as search_router
from app.routers.dashboard import router as dashboard_router
from app.routers.auth_pages import router as auth_pages_router
from app.routers.permissions import router as permissions_router
from app.routers.templates import router as templates_router


app = FastAPI()


@app.exception_handler(HTTPException)
async def _http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        accept = (request.headers.get("accept") or "").lower()
        sec_fetch_dest = (request.headers.get("sec-fetch-dest") or "").lower()
        wants_html = ("text/html" in accept) or (sec_fetch_dest == "document")
        if wants_html and not request.url.path.startswith("/login"):
            nxt = quote(str(request.url.path) + (f"?{request.url.query}" if request.url.query else ""), safe="/")
            return RedirectResponse(url=f"/login?next={nxt}", status_code=303)
        return JSONResponse({"success": False, "error": exc.detail or "Unauthorized"}, status_code=exc.status_code)

    accept = (request.headers.get("accept") or "").lower()
    sec_fetch_dest = (request.headers.get("sec-fetch-dest") or "").lower()
    wants_html = ("text/html" in accept) or (sec_fetch_dest == "document")
    if wants_html and exc.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_410_GONE):
        detail = exc.detail or ("Forbidden" if exc.status_code == status.HTTP_403_FORBIDDEN else "Gone")
        html = (
            "<!doctype html><html lang=\"vi\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
            f"<title>{exc.status_code}</title></head><body style=\"font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; padding: 24px;\">"
            f"<h1 style=\"margin:0 0 8px 0;\">{exc.status_code}</h1>"
            f"<p style=\"margin:0; color:#444;\">{detail}</p>"
            "</body></html>"
        )
        return HTMLResponse(content=html, status_code=exc.status_code)
    return JSONResponse({"success": False, "error": exc.detail}, status_code=exc.status_code)


@app.on_event("startup")
def _startup_db() -> None:
    # Ensure SQLite schema exists
    Base.metadata.create_all(bind=engine)
    ensure_default_users()


_BACKUPS_DIR = STORAGE_DIR / "backups"
_LOGS_DIR = STORAGE_DIR / "logs"


@app.get("/debug/contracts")
def debug_contracts(year: int | None = None):
    y = _pick_year(year)
    rows = _rows_from_db(year=y) if _db_available() else []
    contracts = [r for r in rows if not r.get("annex_no")]
    annexes = [r for r in rows if r.get("annex_no")]
    sample = contracts[0] if contracts else (rows[0] if rows else None)
    annex_sample = annexes[0] if annexes else None
    payload = {
        "year": y,
        "db_path": str(DB_PATH),
        "db_exists": _db_available(),
        "rows": len(rows),
        "contracts": len(contracts),
        "annexes": len(annexes),
        "sample": sample,
        "annex_sample": annex_sample,
    }
    return JSONResponse(jsonable_encoder(payload))


def _pick_year(year: int | None) -> int:
    if year:
        return year

    try:
        years: list[int] = []
        for p in STORAGE_EXCEL_DIR.glob("contracts_*.xlsx"):
            m = re.match(r"contracts_(\d{4})\.xlsx$", p.name)
            if m:
                years.append(int(m.group(1)))
        if years:
            return max(years)
    except Exception:
        pass

    return date.today().year


@app.get("/")
def home() -> RedirectResponse:
    return RedirectResponse(url="/documents/new")


def _pick_existing_dir(primary: Path, fallback: Path) -> Path:
    try:
        if primary.exists():
            # Consider it usable if it has any entries
            for _ in primary.iterdir():
                return primary
    except Exception:
        pass
    return fallback


def _pick_templates_dir(primary: Path, fallback: Path) -> Path:
    # Only pick the new UI templates dir once the essential templates are present.
    try:
        if primary.exists() and (primary / "document_form.html").exists():
            return primary
    except Exception:
        pass
    return fallback


def _pick_static_dir(primary: Path, fallback: Path) -> Path:
    # Only pick the new UI static dir once core assets are present.
    try:
        if primary.exists() and (primary / "css" / "main.css").exists():
            return primary
    except Exception:
        pass
    return fallback


_mau_ui_dir = UI_TEMPLATES_DIR.parent / "Mau UI"
_mau_templates_dir = _mau_ui_dir / "templates"
_mau_static_dir = _mau_ui_dir / "static"

_templates_dir = _pick_templates_dir(_mau_templates_dir, UI_TEMPLATES_DIR)
_static_dir = _pick_static_dir(_mau_static_dir, UI_STATIC_DIR)

app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")
templates = Jinja2Templates(directory=str(_templates_dir))
app.state.templates = templates


def _template_has_permission(request: Request, permission: str) -> bool:
    p = (permission or "").strip()
    if not p:
        return False
    try:
        cached = getattr(request.state, "_perms_cache", None)
        if cached is None:
            user = get_current_user(request)
            cached = get_permissions_for_user(user=user)
            request.state._perms_cache = cached
        return p in cached
    except Exception:
        return False


templates.env.globals["has_permission"] = _template_has_permission

class RequireLoginMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        public_prefixes = (
            "/static",
            "/login",
            "/logout",
        )
        public_exact = {
            "/favicon.ico",
        }

        if path in public_exact or any(path.startswith(p) for p in public_prefixes):
            return await call_next(request)

        username = (request.session.get("username") or "").strip()  # type: ignore[attr-defined]
        if username:
            return await call_next(request)

        accept = (request.headers.get("accept") or "").lower()
        wants_html = "text/html" in accept
        is_xhr = (request.headers.get("x-requested-with") or "").lower() == "xmlhttprequest"
        wants_json = ("application/json" in accept) or (not wants_html) or is_xhr

        if wants_json:
            return JSONResponse({"success": False, "error": "Unauthorized"}, status_code=status.HTTP_401_UNAUTHORIZED)

        nxt = quote(str(request.url.path) + (f"?{request.url.query}" if request.url.query else ""), safe="/")
        return RedirectResponse(url=f"/login?next={nxt}", status_code=303)

# NOTE: Starlette runs middlewares in reverse order of addition (last added runs first).
# We need SessionMiddleware to run BEFORE RequireLoginMiddleware so request.session is available.
app.add_middleware(RequireLoginMiddleware)
app.add_middleware(
    SessionMiddleware,
    secret_key=str(DB_PATH),
    same_site="lax",
)

app.include_router(admin_router)
app.include_router(storage_router)
app.include_router(auth_pages_router)
app.include_router(permissions_router)
app.include_router(templates_router)
app.include_router(catalogue_router)
app.include_router(works_router)
app.include_router(documents_router)
app.include_router(contracts_router)
app.include_router(annexes_router)
app.include_router(users_router)
app.include_router(reports_router)
app.include_router(search_router)
app.include_router(dashboard_router)


@app.get("/documents/new", response_class=HTMLResponse)
def new_document_form(request: Request, error: str | None = None, message: str | None = None, doc_type: str | None = None):
    raise HTTPException(status_code=status.HTTP_410_GONE, detail="Moved")


@app.post("/documents")
def create_document_unified(
    request: Request,
    doc_type: str = Form(...),
    ngay_lap_hop_dong: str = Form(""),
    so_hop_dong_4: str = Form(""),
    contract_no: str = Form(""),
    annex_no: str = Form(""),
    ngay_ky_hop_dong: str = Form(""),
    ngay_ky_phu_luc: str = Form(""),
    linh_vuc: str = Form(""),
    don_vi_ten: str = Form(""),
    don_vi_dia_chi: str = Form(""),
    don_vi_dien_thoai: str = Form(""),
    don_vi_nguoi_dai_dien: str = Form(""),
    don_vi_chuc_vu: str = Form(""),
    don_vi_mst: str = Form(""),
    don_vi_email: str = Form(""),
    so_CCCD: str = Form(""),
    ngay_cap_CCCD: str = Form(""),
    nguoi_thuc_hien_email: str = Form(""),
    kenh_ten: str = Form(""),
    kenh_id: str = Form(""),
    so_tien_chua_GTGT: str = Form(""),
    thue_percent: str = Form("10"),
):
    raise HTTPException(status_code=status.HTTP_410_GONE, detail="Moved")


@app.get("/storage/excel/download/{year}")
def download_contracts_excel(year: int):
    raise HTTPException(status_code=status.HTTP_410_GONE, detail="Moved")


@app.get("/storage/excel/works/download/{year}")
def download_works_excel(year: int):
    raise HTTPException(status_code=status.HTTP_410_GONE, detail="Moved")


@app.get("/storage/files/{year}")
def list_saved_files(year: int):
    raise HTTPException(status_code=status.HTTP_410_GONE, detail="Moved")


@app.get("/storage/docx/{year}/{filename}")
def download_docx_file(year: int, filename: str):
    raise HTTPException(status_code=status.HTTP_410_GONE, detail="Moved")


@app.get("/storage/excel/{year}/{filename}")
def download_excel_file(year: int, filename: str):
    raise HTTPException(status_code=status.HTTP_410_GONE, detail="Moved")
