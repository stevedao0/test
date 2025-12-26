from __future__ import annotations

import traceback
from datetime import date, datetime
from pathlib import Path
from typing import Optional
from urllib.parse import quote

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import (
    CATALOGUE_TEMPLATE_PATH,
    DOCX_TEMPLATE_PATH,
    REGION_CODE,
    FIELD_CODE,
    FIELD_NAME,
    STORAGE_DOCX_DIR,
    STORAGE_EXCEL_DIR,
)
from app.documents.naming import build_docx_filename
from app.models import ContractCreate, ContractRecord
from app.services.docx_renderer import date_parts, render_contract_docx
from app.services.excel_store import (
    append_contract_row,
    delete_contract_row,
    export_catalogue_excel,
    read_contracts,
    update_contract_row,
)
from app.utils.formatters import (
    clean_opt,
    format_money_number,
    format_money_vnd,
    money_to_vietnamese_words,
    normalize_money_to_int,
    normalize_multi_emails,
    normalize_multi_phones,
    normalize_youtube_channel_input,
    parse_so_hop_dong_4,
    serialize_for_json,
)

router = APIRouter()


def get_breadcrumbs(path: str):
    breadcrumbs = [{"label": "Trang chủ", "url": "/"}]

    if "/contracts" in path:
        breadcrumbs.append({"label": "Hợp đồng", "url": "/contracts"})
        if "/new" in path:
            breadcrumbs.append({"label": "Tạo mới", "url": None})
    elif "/annexes" in path:
        breadcrumbs.append({"label": "Phụ lục", "url": "/annexes"})
        if "/new" in path:
            breadcrumbs.append({"label": "Tạo mới", "url": None})

    return breadcrumbs


@router.get("/contracts/new", response_class=HTMLResponse)
def contract_form(request: Request, error: str | None = None):
    url = f"/documents/new?doc_type=contract"
    if error:
        url += f"&error={error}"
    return RedirectResponse(url=url)


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
):
    try:
        channel_id, channel_link = normalize_youtube_channel_input(kenh_id)

        linh_vuc_value = clean_opt(linh_vuc) or FIELD_NAME

        pre_vat_value: Optional[int] = None
        pre_vat_text = ""
        pre_vat_number = ""
        vat_percent_value: Optional[float] = None
        vat_value: Optional[int] = None
        vat_text = ""
        vat_number = ""
        total_value: Optional[int] = None
        total_text = ""
        total_number = ""
        total_words = ""

        if clean_opt(so_tien_chua_GTGT):
            pre_vat_value = normalize_money_to_int(clean_opt(so_tien_chua_GTGT))
            pre_vat_text = format_money_vnd(pre_vat_value)
            pre_vat_number = format_money_number(pre_vat_value)

            pct_raw = clean_opt(thue_percent) or "10"
            vat_percent_value = float(pct_raw.replace(",", "."))
            if vat_percent_value < 0:
                raise ValueError("Thuế GTGT không hợp lệ")

            vat_value = int(round(pre_vat_value * vat_percent_value / 100.0))
            vat_text = format_money_vnd(vat_value)
            vat_number = format_money_number(vat_value)

            total_value = pre_vat_value + vat_value
            total_text = format_money_vnd(total_value)
            total_number = format_money_number(total_value)
            total_words = money_to_vietnamese_words(total_value)

        payload = ContractCreate(
            ngay_lap_hop_dong=date.fromisoformat(ngay_lap_hop_dong),
            so_hop_dong_4=so_hop_dong_4,
            linh_vuc=linh_vuc_value,
            don_vi_ten=clean_opt(don_vi_ten),
            don_vi_dia_chi=clean_opt(don_vi_dia_chi),
            don_vi_dien_thoai=normalize_multi_phones(don_vi_dien_thoai),
            don_vi_nguoi_dai_dien=clean_opt(don_vi_nguoi_dai_dien),
            don_vi_chuc_vu=clean_opt(don_vi_chuc_vu) or "Giám đốc",
            don_vi_mst=clean_opt(don_vi_mst),
            don_vi_email=normalize_multi_emails(don_vi_email),
            so_CCCD=clean_opt(so_CCCD),
            ngay_cap_CCCD=clean_opt(ngay_cap_CCCD),
            nguoi_thuc_hien_email=normalize_multi_emails(nguoi_thuc_hien_email),
            kenh_ten=clean_opt(kenh_ten),
            kenh_id=channel_id,
            so_tien_chua_GTGT=clean_opt(so_tien_chua_GTGT) or None,
            thue_percent=clean_opt(thue_percent) or None,
        )

        year = payload.ngay_lap_hop_dong.year
        contract_no = f"{payload.so_hop_dong_4}/{year}/{REGION_CODE}/{FIELD_CODE}"

        money_value = total_value
        money_text = total_text

        out_docx_dir = STORAGE_DOCX_DIR / str(year)
        out_docx_dir.mkdir(parents=True, exist_ok=True)
        filename = build_docx_filename(
            year=year,
            so_hop_dong_4=payload.so_hop_dong_4,
            so_phu_luc=None,
            linh_vuc=linh_vuc_value,
            kenh_ten=payload.kenh_ten or "",
        )
        out_docx_path = out_docx_dir / filename
        if out_docx_path.exists():
            stem = out_docx_path.stem
            out_docx_path = out_docx_dir / f"{stem}_{date.today().strftime('%Y%m%d')}.docx"

        context = {
            "contract_no": contract_no,
            "so_hop_dong": contract_no,
            "linh_vuc": linh_vuc_value,
            **date_parts(payload.ngay_lap_hop_dong),
            "ngay_ky_hop_dong": f"{payload.ngay_lap_hop_dong.day:02d}",
            "ngay_ky_hop_dong_day_du": payload.ngay_lap_hop_dong.strftime("%d/%m/%Y"),
            "thang_ky_hop_dong": f"{payload.ngay_lap_hop_dong.month:02d}",
            "nam_ky_hop_dong": f"{payload.ngay_lap_hop_dong.year}",
            "don_vi_ten": payload.don_vi_ten,
            "don_vi_dia_chi": payload.don_vi_dia_chi,
            "don_vi_dien_thoai": payload.don_vi_dien_thoai,
            "don_vi_nguoi_dai_dien": payload.don_vi_nguoi_dai_dien,
            "don_vi_chuc_vu": payload.don_vi_chuc_vu,
            "don_vi_mst": payload.don_vi_mst,
            "don_vi_email": payload.don_vi_email,
            "so_CCCD": payload.so_CCCD or "",
            "ngay_cap_CCCD": payload.ngay_cap_CCCD or "",
            "kenh_ten": payload.kenh_ten,
            "kenh_id": payload.kenh_id,
            "nguoi_thuc_hien_email": payload.nguoi_thuc_hien_email or "",
            "so_tien_nhuan_but": total_number,
            "TEN_DON_VI": payload.don_vi_ten,
            "ten_don_vi": payload.don_vi_ten,
            "dia_chi": payload.don_vi_dia_chi,
            "so_dien_thoai": payload.don_vi_dien_thoai,
            "NGUOI_DAI_DIEN": payload.don_vi_nguoi_dai_dien,
            "nguoi_dai_dien": payload.don_vi_nguoi_dai_dien,
            "CHUC_VU": payload.don_vi_chuc_vu,
            "chuc_vu": payload.don_vi_chuc_vu,
            "ma_so_thue": payload.don_vi_mst,
            "email": payload.don_vi_email,
            "ten_kenh": payload.kenh_ten,
            "link_kenh": channel_link,
            "so_tien_chua_GTGT": pre_vat_number,
            "so_tien_GTGT": total_number,
            "thue_GTGT": vat_number,
            "so_tien": total_number,
            "so_tien_bang_chu": total_words,
            "thue_percent": str(int(vat_percent_value)) if vat_percent_value else "10",
        }

        render_contract_docx(
            template_path=DOCX_TEMPLATE_PATH,
            output_path=out_docx_path,
            context=context,
        )

        out_excel_dir = STORAGE_EXCEL_DIR / str(year)
        out_excel_dir.mkdir(parents=True, exist_ok=True)
        catalogue_name = out_docx_path.with_suffix(".xlsx").name
        out_catalogue_path = out_excel_dir / catalogue_name

        catalogue_context = dict(context)
        catalogue_context["so_hop_dong_day_du"] = contract_no
        catalogue_context["ngay_ky_hop_dong"] = payload.ngay_lap_hop_dong.strftime("%d/%m/%Y")
        export_catalogue_excel(
            template_path=CATALOGUE_TEMPLATE_PATH,
            output_path=out_catalogue_path,
            context=catalogue_context,
            sheet_name="Final",
        )

        excel_path = STORAGE_EXCEL_DIR / f"contracts_{year}.xlsx"
        record = ContractRecord(
            contract_no=contract_no,
            contract_year=year,
            ngay_lap_hop_dong=payload.ngay_lap_hop_dong,
            linh_vuc=linh_vuc_value,
            region_code=REGION_CODE,
            field_code=FIELD_CODE,
            don_vi_ten=payload.don_vi_ten,
            don_vi_dia_chi=payload.don_vi_dia_chi,
            don_vi_dien_thoai=payload.don_vi_dien_thoai,
            don_vi_nguoi_dai_dien=payload.don_vi_nguoi_dai_dien,
            don_vi_chuc_vu=payload.don_vi_chuc_vu,
            don_vi_mst=payload.don_vi_mst,
            don_vi_email=normalize_multi_emails(payload.don_vi_email),
            so_CCCD=payload.so_CCCD or "",
            ngay_cap_CCCD=payload.ngay_cap_CCCD or "",
            kenh_ten=payload.kenh_ten,
            kenh_id=payload.kenh_id,
            nguoi_thuc_hien_email=normalize_multi_emails(payload.nguoi_thuc_hien_email or ""),
            so_tien_nhuan_but_value=money_value,
            so_tien_nhuan_but_text=format_money_number(money_value) if money_value is not None else "",
            so_tien_chua_GTGT_value=pre_vat_value,
            so_tien_chua_GTGT_text=format_money_number(pre_vat_value) if pre_vat_value is not None else "",
            thue_percent=vat_percent_value,
            thue_GTGT_value=vat_value,
            thue_GTGT_text=format_money_number(vat_value) if vat_value is not None else "",
            so_tien_value=total_value,
            so_tien_text=format_money_number(total_value) if total_value is not None else "",
            so_tien_bang_chu=total_words,
            docx_path=str(out_docx_path),
        )
        append_contract_row(excel_path=excel_path, record=record)

        return RedirectResponse(
            url=(
                f"/contracts?year={year}"
                f"&download=/download/{year}/{out_docx_path.name}"
                f"&download2=/download_excel/{year}/{out_catalogue_path.name}"
            ),
            status_code=303,
        )

    except Exception as e:
        traceback.print_exc()
        msg = f"{type(e).__name__}: {e}" if str(e) else f"{type(e).__name__}"
        return RedirectResponse(url=f"/documents/new?doc_type=contract&error={msg}", status_code=303)


@router.get("/api/contracts")
def api_contracts_list(year: int | None = None, q: str | None = None):
    y = year or date.today().year
    excel_path = STORAGE_EXCEL_DIR / f"contracts_{y}.xlsx"
    rows = read_contracts(excel_path=excel_path)

    contracts = [r for r in rows if not r.get("annex_no")]

    if q:
        q_lower = q.lower()
        contracts = [
            c for c in contracts
            if q_lower in (c.get("contract_no") or "").lower()
            or q_lower in (c.get("kenh_ten") or "").lower()
        ]

    result = []
    for c in contracts:
        result.append({
            "contract_no": c.get("contract_no"),
            "kenh_ten": c.get("kenh_ten"),
            "don_vi_ten": c.get("don_vi_ten"),
            "kenh_id": c.get("kenh_id"),
        })

    return JSONResponse({"contracts": result})


@router.get("/contracts", response_class=HTMLResponse)
def contracts_list(request: Request, year: int | None = None, download: str | None = None, download2: str | None = None):
    templates_dir = Path("app/web_templates")
    templates = Jinja2Templates(directory=str(templates_dir))

    y = year or date.today().year
    excel_path = STORAGE_EXCEL_DIR / f"contracts_{y}.xlsx"

    rows = read_contracts(excel_path=excel_path)

    contracts = [r for r in rows if not r.get("annex_no")]

    total_contracts = len(contracts)
    total_value = 0
    for r in contracts:
        val = r.get("so_tien_value", 0)
        if val:
            try:
                if isinstance(val, str):
                    val = int(val.replace(",", "").replace(".", ""))
                total_value += int(val)
            except (ValueError, AttributeError):
                pass

    all_contract_nos = {r.get("contract_no") for r in contracts}
    annexes = [r for r in rows if r.get("annex_no")]
    contracts_with_annexes = len({r.get("contract_no") for r in annexes if r.get("contract_no") in all_contract_nos})

    for r in contracts:
        path = r.get("docx_path")
        if isinstance(path, str) and path.strip():
            p = Path(path)
            if p.exists():
                filename = p.name
                r["download_url"] = f"/download/{y}/{filename}"
            else:
                r["download_url"] = None
        else:
            r["download_url"] = None

        contract_no = r.get("contract_no")
        r["annex_count"] = len([a for a in annexes if a.get("contract_no") == contract_no])

    stats = {
        "total_contracts": total_contracts,
        "total_value": total_value,
        "contracts_with_annexes": contracts_with_annexes,
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
            "breadcrumbs": get_breadcrumbs(request.url.path),
        },
    )


@router.get("/contracts/{year}/detail")
def get_contract_detail(year: int, contract_no: str):
    excel_path = STORAGE_EXCEL_DIR / f"contracts_{year}.xlsx"
    rows = read_contracts(excel_path=excel_path)

    contract = None
    for r in rows:
        if r.get("contract_no") == contract_no and not r.get("annex_no"):
            contract = r
            break

    if not contract:
        return JSONResponse({"error": f"Không tìm thấy hợp đồng: {contract_no}"}, status_code=404)

    annexes = [r for r in rows if r.get("contract_no") == contract_no and r.get("annex_no")]

    if contract.get("ngay_lap_hop_dong"):
        val = contract["ngay_lap_hop_dong"]
        if isinstance(val, (date, datetime)):
            contract["ngay_lap_hop_dong_display"] = val.strftime("%d/%m/%Y")

    contract_serialized = serialize_for_json(contract)
    annexes_serialized = serialize_for_json(annexes)

    return JSONResponse({
        "contract": contract_serialized,
        "annexes": annexes_serialized,
    })


@router.get("/contracts/{year}/edit", response_class=HTMLResponse)
def edit_contract_form(request: Request, year: int, contract_no: str):
    templates_dir = Path("app/web_templates")
    templates = Jinja2Templates(directory=str(templates_dir))

    excel_path = STORAGE_EXCEL_DIR / f"contracts_{year}.xlsx"
    rows = read_contracts(excel_path=excel_path)

    contract = None
    for r in rows:
        if r.get("contract_no") == contract_no and not r.get("annex_no"):
            contract = r
            break

    if not contract:
        return RedirectResponse(url=f"/contracts?year={year}&error=Không tìm thấy hợp đồng", status_code=303)

    ngay_lap = contract.get("ngay_lap_hop_dong")
    if isinstance(ngay_lap, (date, datetime)):
        if isinstance(ngay_lap, datetime):
            ngay_lap = ngay_lap.date()
        contract["ngay_lap_hop_dong"] = ngay_lap.isoformat()

    so_hop_dong_4 = parse_so_hop_dong_4(contract_no)
    contract["so_hop_dong_4"] = so_hop_dong_4

    return templates.TemplateResponse(
        "contract_edit.html",
        {
            "request": request,
            "title": f"Chỉnh sửa hợp đồng {contract_no}",
            "contract": contract,
            "year": year,
            "breadcrumbs": get_breadcrumbs(request.url.path),
        },
    )


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
):
    try:
        excel_path = STORAGE_EXCEL_DIR / f"contracts_{year}.xlsx"

        pre_vat_value = None
        vat_value = None
        total_value = None
        vat_percent_value = None

        if clean_opt(so_tien_chua_GTGT):
            pre_vat_value = normalize_money_to_int(clean_opt(so_tien_chua_GTGT))
            pct_raw = clean_opt(thue_percent) or "10"
            vat_percent_value = float(pct_raw.replace(",", "."))
            vat_value = int(round(pre_vat_value * vat_percent_value / 100.0))
            total_value = pre_vat_value + vat_value

        channel_id, channel_link = normalize_youtube_channel_input(kenh_id)

        updated_data = {
            "ngay_lap_hop_dong": date.fromisoformat(ngay_lap_hop_dong),
            "don_vi_ten": clean_opt(don_vi_ten),
            "don_vi_dia_chi": clean_opt(don_vi_dia_chi),
            "don_vi_dien_thoai": normalize_multi_phones(don_vi_dien_thoai),
            "don_vi_nguoi_dai_dien": clean_opt(don_vi_nguoi_dai_dien),
            "don_vi_chuc_vu": clean_opt(don_vi_chuc_vu),
            "don_vi_mst": clean_opt(don_vi_mst),
            "don_vi_email": normalize_multi_emails(don_vi_email),
            "kenh_ten": clean_opt(kenh_ten),
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

        success = update_contract_row(
            excel_path=excel_path,
            contract_no=contract_no,
            annex_no=None,
            updated_data=updated_data
        )

        if success:
            return RedirectResponse(url=f"/contracts?year={year}", status_code=303)
        else:
            return RedirectResponse(url=f"/contracts?year={year}&error=Update failed", status_code=303)

    except Exception as e:
        return RedirectResponse(url=f"/contracts/{year}/edit?contract_no={quote(contract_no)}&error={str(e)}", status_code=303)


@router.post("/contracts/{year}/delete")
def delete_contract(year: int, contract_no: str):
    try:
        excel_path = STORAGE_EXCEL_DIR / f"contracts_{year}.xlsx"

        rows = read_contracts(excel_path=excel_path)
        for r in rows:
            if r.get("contract_no") == contract_no and not r.get("annex_no"):
                docx_path = r.get("docx_path")
                if docx_path and isinstance(docx_path, str):
                    p = Path(docx_path)
                    if p.exists():
                        p.unlink()
                break

        success = delete_contract_row(excel_path=excel_path, contract_no=contract_no, annex_no=None)

        if success:
            return JSONResponse({"success": True, "message": "Đã xóa hợp đồng"})
        else:
            return JSONResponse({"success": False, "error": "Không tìm thấy hợp đồng"}, status_code=404)

    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)
