from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile, Response
from starlette import status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import (
    STORAGE_DIR,
    STORAGE_EXCEL_DIR,
    UI_STATIC_DIR,
    UI_TEMPLATES_DIR,
    WEB_TEMPLATES_DIR,
)

from app.db import DB_PATH, engine
from app.db_models import Base, UserRow
from app.auth import ensure_default_users, require_role
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


app = FastAPI()


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
    return JSONResponse(
        {
            "year": y,
            "db_path": str(DB_PATH),
            "db_exists": _db_available(),
            "rows": len(rows),
            "contracts": len(contracts),
            "annexes": len(annexes),
            "sample": sample,
        }
    )


@app.get("/catalogue/upload", response_class=HTMLResponse)
def catalogue_upload_form(
    request: Request,
    year: int | None = None,
    contract_no: str | None = None,
    annex_no: str | None = None,
    error: str | None = None,
    message: str | None = None,
):
    raise HTTPException(status_code=status.HTTP_410_GONE, detail="Moved")


@app.post("/catalogue/upload")
async def catalogue_upload_submit(
    request: Request,
    year: int = Form(...),
    contract_no: str = Form(...),
    annex_no: str = Form(""),
    catalogue_file: UploadFile = File(...),
    user: UserRow = Depends(require_role("admin", "mod")),
):
    raise HTTPException(status_code=status.HTTP_410_GONE, detail="Moved")


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


@app.get("/contracts/new")
def contract_form() -> RedirectResponse:
    raise HTTPException(status_code=status.HTTP_410_GONE, detail="Moved")


@app.get("/annexes/new")
def annex_form() -> RedirectResponse:
    raise HTTPException(status_code=status.HTTP_410_GONE, detail="Moved")


@app.get("/api/contracts")
def api_contracts_list(year: int | None = None, q: str | None = None):
    raise HTTPException(status_code=status.HTTP_410_GONE, detail="Moved")


@app.get("/contracts", response_class=HTMLResponse)
def contracts_list(request: Request, response: Response, year: int | None = None, download: str | None = None, download2: str | None = None):
    raise HTTPException(status_code=status.HTTP_410_GONE, detail="Moved")


@app.get("/annexes", response_class=HTMLResponse)
def annexes_list(request: Request, response: Response, year: int | None = None, download: str | None = None):
    raise HTTPException(status_code=status.HTTP_410_GONE, detail="Moved")


@app.post("/contracts")
def create_contract(
    request: Request,
    ngay_lap_hop_dong: str = Form(...),
    so_hop_dong_4: str = Form(...),
    linh_vuc: str = Form("Sao chép trực tuyến"),
    don_vi_ten: str = Form(""),
    don_vi_dia_chi: str = Form(""),
    don_vi_dien_thoai: str = Form(""),
    don_vi_nguoi_dai_dien: str = Form(""),
    don_vi_chuc_vu: str = Form("Giám đốc"),
    don_vi_mst: str = Form(""),
    don_vi_email: str = Form(""),
    so_CCCD: str = Form(""),
    ngay_cap_CCCD: str = Form(""),
    nguoi_thuc_hien_email: str = Form(""),
    kenh_ten: str = Form(""),
    kenh_id: str = Form(""),
    so_tien_chua_GTGT: str = Form(""),
    thue_percent: str = Form(""),
    user: UserRow = Depends(require_role("admin", "mod")),
):
    raise HTTPException(status_code=status.HTTP_410_GONE, detail="Moved")


@app.post("/contracts/{year}/delete")
def delete_contract(request: Request, year: int, contract_no: str, user: UserRow = Depends(require_role("admin", "mod"))):
    raise HTTPException(status_code=status.HTTP_410_GONE, detail="Moved")


@app.post("/annexes/{year}/delete")
def delete_annex(request: Request, year: int, contract_no: str, annex_no: str, user: UserRow = Depends(require_role("admin", "mod"))):
    raise HTTPException(status_code=status.HTTP_410_GONE, detail="Moved")


@app.get("/admin/ops", response_class=HTMLResponse)
def admin_ops(request: Request, user: UserRow = Depends(require_role("admin"))):
    raise HTTPException(status_code=status.HTTP_410_GONE, detail="Moved")


@app.get("/admin/ops/download/{kind}/{path:path}")
def admin_ops_download(kind: str, path: str, user: UserRow = Depends(require_role("admin"))):
    raise HTTPException(status_code=status.HTTP_410_GONE, detail="Moved")


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


_templates_dir = _pick_templates_dir(UI_TEMPLATES_DIR, WEB_TEMPLATES_DIR)
_static_dir = _pick_static_dir(UI_STATIC_DIR, Path("app/static"))

app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")
templates = Jinja2Templates(directory=str(_templates_dir))
app.state.templates = templates

app.include_router(admin_router)
app.include_router(storage_router)
app.include_router(catalogue_router)
app.include_router(works_router)
app.include_router(documents_router)
app.include_router(contracts_router)
app.include_router(annexes_router)


@app.get("/works/import", response_class=HTMLResponse)
def works_import_form(request: Request, error: str | None = None, message: str | None = None):
    raise HTTPException(status_code=status.HTTP_410_GONE, detail="Moved")


@app.post("/works/import")
async def works_import_submit(
    request: Request,
    import_file: UploadFile = File(...),
    nguoi_thuc_hien: str = Form(""),
    user: UserRow = Depends(require_role("admin", "mod")),
):
    raise HTTPException(status_code=status.HTTP_410_GONE, detail="Moved")


@app.post("/contracts/{year}/update")
def update_contract(
    request: Request,
    year: int,
    contract_no: str = Form(...),
    ngay_lap_hop_dong: str = Form(...),
    don_vi_ten: str = Form(""),
    don_vi_dia_chi: str = Form(""),
    don_vi_dien_thoai: str = Form(""),
    don_vi_nguoi_dai_dien: str = Form(""),
    don_vi_chuc_vu: str = Form(""),
    don_vi_mst: str = Form(""),
    don_vi_email: str = Form(""),
    kenh_ten: str = Form(""),
    kenh_id: str = Form(""),
    so_tien_chua_GTGT: str = Form(""),
    thue_percent: str = Form("10"),
    user: UserRow = Depends(require_role("admin", "mod")),
):
    raise HTTPException(status_code=status.HTTP_410_GONE, detail="Moved")


@app.post("/annexes")
def create_annex(
    request: Request,
    contract_no: str = Form(...),
    annex_no: str = Form(""),
    ngay_ky_hop_dong: str = Form(""),
    ngay_ky_phu_luc: str = Form(...),
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
    kenh_ten: str = Form(""),
    kenh_id: str = Form(""),
    nguoi_thuc_hien_email: str = Form(""),
    so_tien_chua_GTGT: str = Form(""),
    thue_percent: str = Form("10"),
):
    raise HTTPException(status_code=status.HTTP_410_GONE, detail="Moved")


@app.get("/documents/new", response_class=HTMLResponse)
def document_form_unified(
    request: Request,
    doc_type: str | None = None,
    year: int | None = None,
    contract_no: str | None = None,
    error: str | None = None,
):
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
