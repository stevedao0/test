from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import (
    ANNEX_CATALOGUE_TEMPLATE_PATH,
    ANNEX_TEMPLATE_PATH,
    FIELD_NAME,
    FIELD_CODE,
    REGION_CODE,
    STORAGE_DOCX_DIR,
    STORAGE_EXCEL_DIR,
)
from app.documents.naming import build_docx_filename
from app.models import ContractRecord
from app.services.docx_renderer import render_contract_docx
from app.services.excel_store import (
    append_contract_row,
    delete_contract_row,
    export_catalogue_excel,
    read_contracts,
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


@router.get("/annexes", response_class=HTMLResponse)
def annexes_list(request: Request, year: int | None = None, download: str | None = None):
    templates_dir = Path("app/web_templates")
    templates = Jinja2Templates(directory=str(templates_dir))

    y = year or date.today().year
    excel_path = STORAGE_EXCEL_DIR / f"contracts_{y}.xlsx"

    rows = read_contracts(excel_path=excel_path)

    annexes = [r for r in rows if r.get("annex_no")]

    contracts = [r for r in rows if not r.get("annex_no")]
    contracts_map = {r.get("contract_no"): r for r in contracts}

    total_annexes = len(annexes)
    total_value = 0
    for r in annexes:
        val = r.get("so_tien_value", 0)
        if val:
            try:
                if isinstance(val, str):
                    val = int(val.replace(",", "").replace(".", ""))
                total_value += int(val)
            except (ValueError, AttributeError):
                pass

    contract_annex_counts = {}
    for a in annexes:
        contract_no = a.get("contract_no")
        if contract_no:
            contract_annex_counts[contract_no] = contract_annex_counts.get(contract_no, 0) + 1

    most_annexes_contract = None
    most_annexes_count = 0
    if contract_annex_counts:
        most_annexes_contract = max(contract_annex_counts, key=contract_annex_counts.get)
        most_annexes_count = contract_annex_counts[most_annexes_contract]

    for r in annexes:
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
        if contract_no in contracts_map:
            parent = contracts_map[contract_no]
            r["parent_contract"] = {
                "don_vi_ten": parent.get("don_vi_ten", ""),
                "kenh_ten": parent.get("kenh_ten", ""),
                "ngay_lap_hop_dong": parent.get("ngay_lap_hop_dong", ""),
            }
        else:
            r["parent_contract"] = None

    stats = {
        "total_annexes": total_annexes,
        "total_value": total_value,
        "most_annexes_contract": most_annexes_contract,
        "most_annexes_count": most_annexes_count,
        "unique_contracts": len(contract_annex_counts),
    }

    return templates.TemplateResponse(
        "annexes_list.html",
        {
            "request": request,
            "title": "Danh sách phụ lục",
            "year": y,
            "rows": annexes,
            "stats": stats,
            "download": download,
            "breadcrumbs": get_breadcrumbs(request.url.path),
        },
    )


@router.get("/annexes/new", response_class=HTMLResponse)
def annex_form(request: Request, year: int | None = None, contract_no: str | None = None, error: str | None = None):
    y = year or date.today().year
    url = f"/documents/new?doc_type=annex&year={y}"
    if contract_no:
        url += f"&contract_no={contract_no}"
    if error:
        url += f"&error={error}"
    return RedirectResponse(url=url)


@router.post("/annexes")
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
    try:
        so_phu_luc = annex_no.strip() or None

        year = None
        parts = contract_no.split("/")
        if len(parts) >= 2 and parts[1].isdigit():
            year = int(parts[1])
        else:
            year = date.today().year

        contracts = read_contracts(excel_path=STORAGE_EXCEL_DIR / f"contracts_{year}.xlsx")
        contract_row: dict | None = None
        for r in contracts:
            if r.get("contract_no") == contract_no:
                contract_row = r
                break

        if ngay_ky_hop_dong and ngay_ky_hop_dong.strip():
            contract_date = date.fromisoformat(ngay_ky_hop_dong)
        elif contract_row and contract_row.get("ngay_lap_hop_dong"):
            contract_date_value = contract_row["ngay_lap_hop_dong"]
            if isinstance(contract_date_value, date):
                if isinstance(contract_date_value, datetime):
                    contract_date = contract_date_value.date()
                else:
                    contract_date = contract_date_value
            elif isinstance(contract_date_value, str):
                contract_date = date.fromisoformat(contract_date_value)
            else:
                return RedirectResponse(url="/documents/new?doc_type=annex&error=Không tìm thấy ngày ký hợp đồng", status_code=303)
        else:
            return RedirectResponse(url="/documents/new?doc_type=annex&error=Vui lòng nhập ngày ký hợp đồng hoặc chọn hợp đồng có sẵn", status_code=303)

        contract_date_parts = {
            "ngay_ky_hop_dong": f"{contract_date.day:02d}",
            "thang_ky_hop_dong": f"{contract_date.month:02d}",
            "nam_ky_hop_dong": f"{contract_date.year}",
            "so_hop_dong_day_du": contract_no,
        }

        annex_date = date.fromisoformat(ngay_ky_phu_luc)
        annex_date_parts = {
            "ngay_ky_phu_luc": f"{annex_date.day:02d}",
            "thang_ky_phu_luc": f"{annex_date.month:02d}",
            "nam_ky_phu_luc": f"{annex_date.year}",
        }

        linh_vuc_value = clean_opt(linh_vuc) or (contract_row.get("linh_vuc") if contract_row else "") or FIELD_NAME
        don_vi_ten_value = clean_opt(don_vi_ten) or (contract_row.get("don_vi_ten") if contract_row else "") or ""
        don_vi_dia_chi_value = clean_opt(don_vi_dia_chi) or (contract_row.get("don_vi_dia_chi") if contract_row else "") or ""
        don_vi_dien_thoai_value = normalize_multi_phones(
            clean_opt(don_vi_dien_thoai) or (contract_row.get("don_vi_dien_thoai") if contract_row else "") or ""
        )
        don_vi_nguoi_dai_dien_value = clean_opt(don_vi_nguoi_dai_dien) or (contract_row.get("don_vi_nguoi_dai_dien") if contract_row else "") or ""
        don_vi_chuc_vu_value = clean_opt(don_vi_chuc_vu) or (contract_row.get("don_vi_chuc_vu") if contract_row else "") or "Giám đốc"
        don_vi_mst_value = clean_opt(don_vi_mst) or (contract_row.get("don_vi_mst") if contract_row else "") or ""
        don_vi_email_value = normalize_multi_emails(
            clean_opt(don_vi_email) or (contract_row.get("don_vi_email") if contract_row else "") or ""
        )
        kenh_ten_value = clean_opt(kenh_ten) or (contract_row.get("kenh_ten") if contract_row else "") or ""

        channel_id_value_raw = clean_opt(kenh_id) or (contract_row.get("kenh_id") if contract_row else "") or ""
        channel_id_value, channel_link_value = normalize_youtube_channel_input(channel_id_value_raw)

        pre_vat_value = 0
        vat_value = 0
        total_value = 0
        pre_vat_number = ""
        vat_number = ""
        total_number = ""
        total_words = ""

        if clean_opt(so_tien_chua_GTGT):
            pre_vat_value = normalize_money_to_int(clean_opt(so_tien_chua_GTGT))
            pre_vat_number = format_money_number(pre_vat_value)

            pct_raw = clean_opt(thue_percent) or "10"
            vat_percent_value = float(pct_raw.replace(",", "."))
            if vat_percent_value < 0:
                raise ValueError("Thuế GTGT không hợp lệ")

            vat_value = int(round(pre_vat_value * vat_percent_value / 100.0))
            vat_number = format_money_number(vat_value)

            total_value = pre_vat_value + vat_value
            total_number = format_money_number(total_value)
            total_words = money_to_vietnamese_words(total_value)

        context = {
            "contract_no": contract_no,
            "so_hop_dong": contract_no,
            "so_hop_dong_day_du": contract_no,
            "so_phu_luc": so_phu_luc or "",
            "linh_vuc": linh_vuc_value,
            **contract_date_parts,
            **annex_date_parts,
            "don_vi_ten": don_vi_ten_value,
            "don_vi_dia_chi": don_vi_dia_chi_value,
            "don_vi_dien_thoai": don_vi_dien_thoai_value,
            "don_vi_nguoi_dai_dien": don_vi_nguoi_dai_dien_value,
            "don_vi_chuc_vu": don_vi_chuc_vu_value,
            "don_vi_mst": don_vi_mst_value,
            "don_vi_email": don_vi_email_value,
            "so_CCCD": so_CCCD or "",
            "ngay_cap_CCCD": ngay_cap_CCCD or "",
            "kenh_ten": kenh_ten_value,
            "kenh_id": channel_id_value,
            "nguoi_thuc_hien_email": nguoi_thuc_hien_email or "",
            "so_tien_nhuan_but": total_number,
            "so_tien_chua_GTGT": pre_vat_number,
            "thue_GTGT": vat_number,
            "so_tien_GTGT": total_number,
            "so_tien": total_number,
            "so_tien_bang_chu": total_words,
            "thue_percent": str(int(vat_percent_value)) if vat_percent_value else "10",
            "TEN_DON_VI": don_vi_ten_value,
            "ten_don_vi": don_vi_ten_value,
            "dia_chi": don_vi_dia_chi_value,
            "so_dien_thoai": don_vi_dien_thoai_value,
            "NGUOI_DAI_DIEN": don_vi_nguoi_dai_dien_value,
            "nguoi_dai_dien": don_vi_nguoi_dai_dien_value,
            "CHUC_VU": don_vi_chuc_vu_value,
            "chuc_vu": don_vi_chuc_vu_value,
            "ma_so_thue": don_vi_mst_value,
            "email": don_vi_email_value,
            "ten_kenh": kenh_ten_value,
            "link_kenh": channel_link_value,
        }

        out_docx_dir = STORAGE_DOCX_DIR / str(year)
        out_docx_dir.mkdir(parents=True, exist_ok=True)
        filename = build_docx_filename(
            year=year,
            so_hop_dong_4=parse_so_hop_dong_4(contract_no),
            so_phu_luc=so_phu_luc,
            linh_vuc=linh_vuc_value,
            kenh_ten=kenh_ten_value,
        )
        out_docx_path = out_docx_dir / filename
        if out_docx_path.exists():
            stem = out_docx_path.stem
            out_docx_path = out_docx_dir / f"{stem}_{date.today().strftime('%Y%m%d')}.docx"

        render_contract_docx(template_path=ANNEX_TEMPLATE_PATH, output_path=out_docx_path, context=context)

        out_excel_dir = STORAGE_EXCEL_DIR / str(year)
        out_excel_dir.mkdir(parents=True, exist_ok=True)
        catalogue_name = out_docx_path.with_suffix(".xlsx").name
        out_catalogue_path = out_excel_dir / catalogue_name

        catalogue_context = dict(context)
        catalogue_context["so_hop_dong_day_du"] = contract_no
        catalogue_context["ngay_ky_hop_dong"] = contract_date.strftime("%d/%m/%Y")
        catalogue_context["ngay_ky_phu_luc"] = annex_date.strftime("%d/%m/%Y")
        export_catalogue_excel(
            template_path=ANNEX_CATALOGUE_TEMPLATE_PATH,
            output_path=out_catalogue_path,
            context=catalogue_context,
            sheet_name="Final",
        )

        contracts_excel_path = STORAGE_EXCEL_DIR / f"contracts_{year}.xlsx"

        vat_percent_final = None
        if clean_opt(so_tien_chua_GTGT):
            pct_raw = clean_opt(thue_percent) or "10"
            vat_percent_final = float(pct_raw.replace(",", "."))

        annex_record = ContractRecord(
            contract_no=contract_no,
            contract_year=year,
            annex_no=so_phu_luc,
            ngay_lap_hop_dong=annex_date,
            linh_vuc=linh_vuc_value,
            region_code=REGION_CODE,
            field_code=FIELD_CODE,
            don_vi_ten=don_vi_ten_value,
            don_vi_dia_chi=don_vi_dia_chi_value,
            don_vi_dien_thoai=don_vi_dien_thoai_value,
            don_vi_nguoi_dai_dien=don_vi_nguoi_dai_dien_value,
            don_vi_chuc_vu=don_vi_chuc_vu_value,
            don_vi_mst=don_vi_mst_value,
            don_vi_email=don_vi_email_value,
            kenh_ten=kenh_ten_value,
            kenh_id=channel_id_value,
            so_tien_nhuan_but_value=total_value if total_value else None,
            so_tien_nhuan_but_text=format_money_vnd(total_value) if total_value else None,
            so_tien_chua_GTGT_value=pre_vat_value if pre_vat_value else None,
            so_tien_chua_GTGT_text=format_money_vnd(pre_vat_value) if pre_vat_value else None,
            thue_percent=vat_percent_final,
            thue_GTGT_value=vat_value if vat_value else None,
            thue_GTGT_text=format_money_vnd(vat_value) if vat_value else None,
            so_tien_value=total_value if total_value else None,
            so_tien_text=format_money_vnd(total_value) if total_value else None,
            so_tien_bang_chu=total_words if total_words else None,
            docx_path=str(out_docx_path),
        )
        append_contract_row(excel_path=contracts_excel_path, record=annex_record)

        return RedirectResponse(
            url=(
                f"/contracts?year={year}"
                f"&download=/download/{year}/{out_docx_path.name}"
                f"&download2=/download_excel/{year}/{out_catalogue_path.name}"
            ),
            status_code=303,
        )
    except Exception as e:
        return RedirectResponse(url=f"/documents/new?doc_type=annex&error={str(e)}", status_code=303)


@router.post("/annexes/{year}/delete")
def delete_annex(year: int, contract_no: str, annex_no: str):
    try:
        excel_path = STORAGE_EXCEL_DIR / f"contracts_{year}.xlsx"

        rows = read_contracts(excel_path=excel_path)
        for r in rows:
            if r.get("contract_no") == contract_no and r.get("annex_no") == annex_no:
                docx_path = r.get("docx_path")
                if docx_path and isinstance(docx_path, str):
                    p = Path(docx_path)
                    if p.exists():
                        p.unlink()

                catalogue_path = r.get("catalogue_path")
                if catalogue_path and isinstance(catalogue_path, str):
                    p = Path(catalogue_path)
                    if p.exists():
                        p.unlink()
                break

        success = delete_contract_row(excel_path=excel_path, contract_no=contract_no, annex_no=annex_no)

        if success:
            return JSONResponse({"success": True, "message": f"Đã xóa phụ lục {annex_no}"})
        else:
            return JSONResponse({"success": False, "error": "Không tìm thấy phụ lục"}, status_code=404)

    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)
