from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse

from app.auth import require_permission
from app.config import STORAGE_DIR, STORAGE_EXCEL_DIR
from app.db_models import UserRow
from app.db_ops import _db_get_contract_row, _db_update_contract_fields
from app.services.safety import audit_log, safe_replace_bytes
from app.utils import get_breadcrumbs


router = APIRouter()


@router.get("/catalogue/upload", response_class=HTMLResponse)
def catalogue_upload_form(
    request: Request,
    year: int | None = None,
    contract_no: str | None = None,
    annex_no: str | None = None,
    error: str | None = None,
    message: str | None = None,
    user: UserRow = Depends(require_permission("catalogue.upload")),
):
    templates = request.app.state.templates

    y = year or _year_from_contract_no(contract_no or "")
    return templates.TemplateResponse(
        "catalogue_upload.html",
        {
            "request": request,
            "title": "Upload danh mục Excel",
            "year": y,
            "contract_no": contract_no or "",
            "annex_no": annex_no or "",
            "error": error,
            "message": message,
            "breadcrumbs": get_breadcrumbs(request.url.path),
        },
    )


@router.post("/catalogue/upload")
async def catalogue_upload_submit(
    request: Request,
    year: int = Form(...),
    contract_no: str = Form(...),
    annex_no: str = Form(""),
    next: str = Form(""),
    catalogue_file: UploadFile = File(...),
    user: UserRow = Depends(require_permission("catalogue.upload")),
):
    backups_dir = STORAGE_DIR / "backups"
    logs_dir = STORAGE_DIR / "logs"

    try:
        if not catalogue_file.filename or not catalogue_file.filename.lower().endswith(".xlsx"):
            raise ValueError("File danh mục phải là .xlsx")

        target_annex_no = annex_no.strip() or None
        if _db_get_contract_row(year=year, contract_no=contract_no, annex_no=target_annex_no) is None:
            raise ValueError("Không tìm thấy hợp đồng/phụ lục để cập nhật catalogue_path")

        data = await catalogue_file.read()
        if data is None or len(data) == 0:
            raise ValueError("File upload rỗng")
        if len(data) > 25 * 1024 * 1024:
            raise ValueError("File upload quá lớn (tối đa 25MB)")

        out_dir = STORAGE_EXCEL_DIR / str(year)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / Path(catalogue_file.filename).name
        safe_replace_bytes(out_path, data, backup_dir=backups_dir / "files")

        success = _db_update_contract_fields(
            year=year,
            contract_no=contract_no,
            annex_no=target_annex_no,
            updated={"catalogue_path": str(out_path)},
        )
        if not success:
            raise ValueError("Không tìm thấy hợp đồng/phụ lục để cập nhật catalogue_path")

        audit_log(
            log_dir=logs_dir,
            event={
                "action": "catalogue.upload",
                "ip": getattr(getattr(request, "client", None), "host", None),
                "year": year,
                "contract_no": contract_no,
                "annex_no": target_annex_no,
                "file": out_path.name,
                "bytes": len(data),
                "actor": user.username,
            },
        )

        redirect_to = (next or "").strip() or f"/catalogue/upload?year={year}&contract_no={contract_no}&annex_no={annex_no}"
        sep = "&" if "?" in redirect_to else "?"
        return RedirectResponse(url=f"{redirect_to}{sep}message=Đã upload danh mục và cập nhật dữ liệu", status_code=303)
    except Exception as e:
        msg = f"{type(e).__name__}: {e}" if str(e) else f"{type(e).__name__}"
        redirect_to = (next or "").strip() or f"/catalogue/upload?year={year}&contract_no={contract_no}&annex_no={annex_no}"
        sep = "&" if "?" in redirect_to else "?"
        return RedirectResponse(url=f"{redirect_to}{sep}error={msg}", status_code=303)


def _year_from_contract_no(contract_no: str) -> int:
    parts = (contract_no or "").split("/")
    if len(parts) >= 2 and parts[1].isdigit():
        return int(parts[1])
    from datetime import date

    return date.today().year
