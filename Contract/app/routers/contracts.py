from __future__ import annotations

from datetime import date
from io import BytesIO
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette import status

from app.auth import require_role
from app.context import FIELD_CODE, FIELD_NAME, REGION_CODE
from app.db_models import UserRow
from app.db_ops import _db_delete_contract_record, _db_get_contract_row, _db_update_contract_fields, _db_upsert_contract_record, _rows_from_db
from app.documents.naming import build_docx_filename
from app.services.docx_renderer import date_parts, render_contract_docx
from app.services.excel_store import export_catalogue_excel
from app.services.safety import audit_log, safe_move_to_backup
from app.config import CATALOGUE_TEMPLATE_PATH, DOCX_TEMPLATE_PATH, STORAGE_DIR, STORAGE_DOCX_DIR, STORAGE_EXCEL_DIR
from app.utils import (
    clean_opt as _clean_opt,
    format_money_number,
    get_breadcrumbs,
    money_to_vietnamese_words,
    normalize_money_to_int,
    normalize_multi_emails,
    normalize_multi_phones,
    normalize_youtube_channel_input,
)


router = APIRouter()

_BACKUPS_DIR = STORAGE_DIR / "backups"
_LOGS_DIR = STORAGE_DIR / "logs"


@router.get("/contracts/new")
def contract_form() -> RedirectResponse:
    return RedirectResponse(url="/documents/new?doc_type=contract")


@router.get("/api/contracts")
def api_contracts_list(year: int | None = None, q: str | None = None):
    y = year or date.today().year
    rows = _rows_from_db(year=y)
    contracts = [r for r in rows if not r.get("annex_no")]
    if q:
        ql = q.lower()
        contracts = [
            c
            for c in contracts
            if ql in (c.get("contract_no") or "").lower() or ql in (c.get("kenh_ten") or "").lower()
        ]
    result = []
    for c in contracts:
        result.append(
            {
                "contract_no": c.get("contract_no"),
                "kenh_ten": c.get("kenh_ten"),
                "don_vi_ten": c.get("don_vi_ten"),
                "kenh_id": c.get("kenh_id"),
            }
        )
    return JSONResponse({"contracts": result})


@router.get("/contracts", response_class=HTMLResponse)
def contracts_list(
    request: Request,
    response: Response,
    year: int | None = None,
    download: str | None = None,
    download2: str | None = None,
):
    templates = request.app.state.templates

    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    y = year or date.today().year
    rows = _rows_from_db(year=y)
    contracts = [r for r in rows if not r.get("annex_no")]

    catalogue_filter = (request.query_params.get("catalogue") or "all").strip().lower()
    if catalogue_filter in ("yes", "has", "1", "true"):
        contracts = [r for r in contracts if r.get("catalogue_path")]
    elif catalogue_filter in ("no", "none", "0", "false"):
        contracts = [r for r in contracts if not r.get("catalogue_path")]

    annexes = [r for r in rows if r.get("annex_no")]
    for r in contracts:
        contract_no = r.get("contract_no")
        r["annex_count"] = len([a for a in annexes if a.get("contract_no") == contract_no])

        p = Path(r.get("docx_path") or "")
        r["download_url"] = f"/download/{y}/{p.name}" if p.exists() else None

        cp = Path(r.get("catalogue_path") or "")
        r["catalogue_download_url"] = f"/download_excel/{y}/{cp.name}" if cp.exists() else None

    stats = {
        "total_contracts": len(contracts),
        "total_value": sum(int(r.get("so_tien_value") or 0) for r in contracts),
        "contracts_with_annexes": len({a.get("contract_no") for a in annexes if a.get("contract_no")}),
    }

    return templates.TemplateResponse(
        "contracts_list.html",
        {
            "request": request,
            "title": "Danh sách hợp đồng",
            "year": y,
            "rows": contracts,
            "stats": stats,
            "download": download,
            "download2": download2,
            "catalogue_filter": catalogue_filter,
            "breadcrumbs": get_breadcrumbs(request.url.path),
        },
    )


@router.post("/contracts")
def create_contract(
    request: Request,
    ngay_lap_hop_dong: str = Form(...),
    so_hop_dong_4: str = Form(...),
    linh_vuc: str = Form(FIELD_NAME),
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
    try:
        channel_id, channel_link = normalize_youtube_channel_input(kenh_id)
        linh_vuc_value = _clean_opt(linh_vuc) or FIELD_NAME

        pre_vat_value: Optional[int] = None
        vat_percent_value: Optional[float] = None
        vat_value: Optional[int] = None
        total_value: Optional[int] = None

        if _clean_opt(so_tien_chua_GTGT):
            pre_vat_value = normalize_money_to_int(_clean_opt(so_tien_chua_GTGT))
            pct_raw = _clean_opt(thue_percent) or "10"
            vat_percent_value = float(pct_raw.replace(",", "."))
            vat_value = int(round(pre_vat_value * vat_percent_value / 100.0))
            total_value = pre_vat_value + vat_value

        contract_date = date.fromisoformat(ngay_lap_hop_dong)
        year = contract_date.year
        contract_no = f"{so_hop_dong_4}/{year}/{REGION_CODE}/{FIELD_CODE}"

        if _db_get_contract_row(year=year, contract_no=contract_no, annex_no=None) is not None:
            raise ValueError("Số hợp đồng đã tồn tại")

        out_docx_dir = STORAGE_DOCX_DIR / str(year)
        out_docx_dir.mkdir(parents=True, exist_ok=True)
        filename = build_docx_filename(
            year=year,
            so_hop_dong_4=so_hop_dong_4,
            so_phu_luc=None,
            linh_vuc=linh_vuc_value,
            kenh_ten=_clean_opt(kenh_ten),
        )
        out_docx_path = out_docx_dir / filename
        if out_docx_path.exists():
            stem = out_docx_path.stem
            out_docx_path = out_docx_dir / f"{stem}_{date.today().strftime('%Y%m%d')}.docx"

        context = {
            "contract_no": contract_no,
            "so_hop_dong": contract_no,
            "linh_vuc": linh_vuc_value,
            **date_parts(contract_date),
            "don_vi_ten": _clean_opt(don_vi_ten),
            "don_vi_dia_chi": _clean_opt(don_vi_dia_chi),
            "don_vi_dien_thoai": normalize_multi_phones(don_vi_dien_thoai),
            "don_vi_nguoi_dai_dien": _clean_opt(don_vi_nguoi_dai_dien),
            "don_vi_chuc_vu": _clean_opt(don_vi_chuc_vu) or "Giám đốc",
            "don_vi_mst": _clean_opt(don_vi_mst),
            "don_vi_email": normalize_multi_emails(don_vi_email),
            "so_CCCD": _clean_opt(so_CCCD),
            "ngay_cap_CCCD": _clean_opt(ngay_cap_CCCD),
            "kenh_ten": _clean_opt(kenh_ten),
            "kenh_id": channel_id,
            "link_kenh": channel_link,
            "nguoi_thuc_hien_email": normalize_multi_emails(nguoi_thuc_hien_email),
            "so_tien_chua_GTGT": format_money_number(pre_vat_value) if pre_vat_value else "",
            "thue_GTGT": format_money_number(vat_value) if vat_value else "",
            "so_tien": format_money_number(total_value) if total_value else "",
            "so_tien_bang_chu": money_to_vietnamese_words(total_value) if total_value else "",
            "thue_percent": str(int(vat_percent_value)) if vat_percent_value else "10",
        }

        render_contract_docx(template_path=DOCX_TEMPLATE_PATH, output_path=out_docx_path, context=context)

        out_excel_dir = STORAGE_EXCEL_DIR / str(year)
        out_excel_dir.mkdir(parents=True, exist_ok=True)
        out_catalogue_path = out_excel_dir / out_docx_path.with_suffix(".xlsx").name
        export_catalogue_excel(
            template_path=CATALOGUE_TEMPLATE_PATH,
            output_path=out_catalogue_path,
            context=dict(context),
            sheet_name="Final",
        )

        _db_upsert_contract_record(
            record={
                "contract_no": contract_no,
                "contract_year": year,
                "annex_no": None,
                "ngay_lap_hop_dong": contract_date,
                "linh_vuc": linh_vuc_value,
                "region_code": REGION_CODE,
                "field_code": FIELD_CODE,
                "don_vi_ten": _clean_opt(don_vi_ten),
                "don_vi_dia_chi": _clean_opt(don_vi_dia_chi),
                "don_vi_dien_thoai": normalize_multi_phones(don_vi_dien_thoai),
                "don_vi_nguoi_dai_dien": _clean_opt(don_vi_nguoi_dai_dien),
                "don_vi_chuc_vu": _clean_opt(don_vi_chuc_vu) or "Giám đốc",
                "don_vi_mst": _clean_opt(don_vi_mst),
                "don_vi_email": normalize_multi_emails(don_vi_email),
                "so_CCCD": _clean_opt(so_CCCD),
                "ngay_cap_CCCD": _clean_opt(ngay_cap_CCCD),
                "kenh_ten": _clean_opt(kenh_ten),
                "kenh_id": channel_id,
                "nguoi_thuc_hien_email": normalize_multi_emails(nguoi_thuc_hien_email),
                "so_tien_chua_GTGT_value": pre_vat_value,
                "so_tien_chua_GTGT_text": format_money_number(pre_vat_value) if pre_vat_value else "",
                "thue_percent": vat_percent_value,
                "thue_GTGT_value": vat_value,
                "thue_GTGT_text": format_money_number(vat_value) if vat_value else "",
                "so_tien_value": total_value,
                "so_tien_text": format_money_number(total_value) if total_value else "",
                "so_tien_bang_chu": money_to_vietnamese_words(total_value) if total_value else "",
                "docx_path": str(out_docx_path),
                "catalogue_path": str(out_catalogue_path),
            }
        )

        audit_log(
            log_dir=_LOGS_DIR,
            event={
                "action": "contracts.create",
                "ip": getattr(getattr(request, "client", None), "host", None),
                "year": year,
                "contract_no": contract_no,
                "actor": user.username,
            },
        )

        return RedirectResponse(
            url=(
                f"/contracts?year={year}"
                f"&download=/download/{year}/{out_docx_path.name}"
                f"&download2=/download_excel/{year}/{out_catalogue_path.name}"
            ),
            status_code=303,
        )
    except Exception as e:
        msg = f"{type(e).__name__}: {e}" if str(e) else f"{type(e).__name__}"
        return RedirectResponse(url=f"/documents/new?doc_type=contract&error={msg}", status_code=303)


@router.post("/contracts/{year}/update")
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
    try:
        pre_vat_value = None
        vat_value = None
        total_value = None
        vat_percent_value = None

        if _clean_opt(so_tien_chua_GTGT):
            pre_vat_value = normalize_money_to_int(_clean_opt(so_tien_chua_GTGT))
            pct_raw = _clean_opt(thue_percent) or "10"
            vat_percent_value = float(pct_raw.replace(",", "."))
            vat_value = int(round(pre_vat_value * vat_percent_value / 100.0))
            total_value = pre_vat_value + vat_value

        channel_id, _ = normalize_youtube_channel_input(kenh_id)

        updated_data = {
            "ngay_lap_hop_dong": date.fromisoformat(ngay_lap_hop_dong),
            "don_vi_ten": _clean_opt(don_vi_ten),
            "don_vi_dia_chi": _clean_opt(don_vi_dia_chi),
            "don_vi_dien_thoai": normalize_multi_phones(don_vi_dien_thoai),
            "don_vi_nguoi_dai_dien": _clean_opt(don_vi_nguoi_dai_dien),
            "don_vi_chuc_vu": _clean_opt(don_vi_chuc_vu),
            "don_vi_mst": _clean_opt(don_vi_mst),
            "don_vi_email": normalize_multi_emails(don_vi_email),
            "kenh_ten": _clean_opt(kenh_ten),
            "kenh_id": channel_id,
            "so_tien_chua_GTGT_value": pre_vat_value,
            "so_tien_chua_GTGT_text": format_money_number(pre_vat_value) if pre_vat_value else "",
            "thue_percent": vat_percent_value,
            "thue_GTGT_value": vat_value,
            "thue_GTGT_text": format_money_number(vat_value) if vat_value else "",
            "so_tien_value": total_value,
            "so_tien_text": format_money_number(total_value) if total_value else "",
            "so_tien_nhuan_but_value": total_value,
            "so_tien_nhuan_but_text": format_money_number(total_value) if total_value else "",
            "so_tien_bang_chu": money_to_vietnamese_words(total_value) if total_value else "",
        }

        success = _db_update_contract_fields(year=year, contract_no=contract_no, annex_no=None, updated=updated_data)

        if success:
            audit_log(
                log_dir=_LOGS_DIR,
                event={
                    "action": "contracts.update",
                    "ip": getattr(getattr(request, "client", None), "host", None),
                    "year": year,
                    "contract_no": contract_no,
                    "updated_keys": sorted([k for k in updated_data.keys()]),
                    "actor": user.username,
                },
            )

        if success:
            return RedirectResponse(url=f"/contracts?year={year}", status_code=303)
        return RedirectResponse(url=f"/contracts?year={year}&error=Update failed", status_code=303)

    except Exception as e:
        from urllib.parse import quote

        return RedirectResponse(url=f"/contracts/{year}/edit?contract_no={quote(contract_no)}&error={str(e)}", status_code=303)


@router.post("/contracts/{year}/delete")
def delete_contract(
    request: Request,
    year: int,
    contract_no: str,
    user: UserRow = Depends(require_role("admin", "mod")),
):
    try:
        row = _db_get_contract_row(year=year, contract_no=contract_no, annex_no=None)
        if row and row.docx_path:
            p = Path(row.docx_path)
            if p.exists():
                safe_move_to_backup(p, backup_dir=_BACKUPS_DIR / "deleted")
        if row and row.catalogue_path:
            p = Path(row.catalogue_path)
            if p.exists():
                safe_move_to_backup(p, backup_dir=_BACKUPS_DIR / "deleted")

        ok = _db_delete_contract_record(year=year, contract_no=contract_no, annex_no=None)
        if ok:
            audit_log(
                log_dir=_LOGS_DIR,
                event={
                    "action": "contracts.delete",
                    "ip": getattr(getattr(request, "client", None), "host", None),
                    "year": year,
                    "contract_no": contract_no,
                    "actor": user.username,
                },
            )
            return JSONResponse({"success": True})
        return JSONResponse({"success": False, "error": "Không tìm thấy hợp đồng"}, status_code=404)
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)
