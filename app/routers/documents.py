from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import FIELD_NAME, STORAGE_EXCEL_DIR
from app.services.excel_store import read_contracts

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


@router.get("/", response_class=HTMLResponse)
def home() -> RedirectResponse:
    return RedirectResponse(url="/documents/new")


@router.get("/documents/new", response_class=HTMLResponse)
def document_form_unified(
    request: Request,
    doc_type: str | None = None,
    year: int | None = None,
    contract_no: str | None = None,
    error: str | None = None,
):
    templates_dir = Path("app/web_templates")
    templates = Jinja2Templates(directory=str(templates_dir))

    y = year or date.today().year
    contracts = read_contracts(excel_path=STORAGE_EXCEL_DIR / f"contracts_{y}.xlsx")

    contracts = [r for r in contracts if not r.get("annex_no")]

    preview: dict = {}
    if contract_no and doc_type == "annex":
        for r in contracts:
            if r.get("contract_no") == contract_no:
                preview = r.copy()
                if "ngay_lap_hop_dong" in preview:
                    val = preview["ngay_lap_hop_dong"]
                    if isinstance(val, date):
                        if isinstance(val, datetime):
                            val = val.date()
                        preview["ngay_lap_hop_dong"] = val.isoformat()
                break

    return templates.TemplateResponse(
        "document_form.html",
        {
            "request": request,
            "title": "Tạo tài liệu",
            "error": error,
            "doc_type": doc_type or "contract",
            "contracts": contracts,
            "preview": preview,
            "year": y,
            "today": date.today().isoformat(),
            "selected_contract_no": contract_no or "",
            "breadcrumbs": get_breadcrumbs(request.url.path),
        },
    )


@router.post("/documents")
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
    from app.routers.contracts import create_contract
    from app.routers.annexes import create_annex

    if doc_type == "contract":
        return create_contract(
            request=request,
            ngay_lap_hop_dong=ngay_lap_hop_dong,
            so_hop_dong_4=so_hop_dong_4,
            linh_vuc=linh_vuc or FIELD_NAME,
            don_vi_ten=don_vi_ten,
            don_vi_dia_chi=don_vi_dia_chi,
            don_vi_dien_thoai=don_vi_dien_thoai,
            don_vi_nguoi_dai_dien=don_vi_nguoi_dai_dien,
            don_vi_chuc_vu=don_vi_chuc_vu,
            don_vi_mst=don_vi_mst,
            don_vi_email=don_vi_email,
            so_CCCD=so_CCCD,
            ngay_cap_CCCD=ngay_cap_CCCD,
            nguoi_thuc_hien_email=nguoi_thuc_hien_email,
            kenh_ten=kenh_ten,
            kenh_id=kenh_id,
            so_tien_chua_GTGT=so_tien_chua_GTGT,
            thue_percent=thue_percent,
        )
    elif doc_type == "annex":
        return create_annex(
            request=request,
            contract_no=contract_no,
            annex_no=annex_no,
            ngay_ky_hop_dong=ngay_ky_hop_dong,
            ngay_ky_phu_luc=ngay_ky_phu_luc,
            linh_vuc=linh_vuc,
            don_vi_ten=don_vi_ten,
            don_vi_dia_chi=don_vi_dia_chi,
            don_vi_dien_thoai=don_vi_dien_thoai,
            don_vi_nguoi_dai_dien=don_vi_nguoi_dai_dien,
            don_vi_chuc_vu=don_vi_chuc_vu,
            don_vi_mst=don_vi_mst,
            don_vi_email=don_vi_email,
            so_CCCD=so_CCCD,
            ngay_cap_CCCD=ngay_cap_CCCD,
            kenh_ten=kenh_ten,
            kenh_id=kenh_id,
            nguoi_thuc_hien_email=nguoi_thuc_hien_email,
            so_tien_chua_GTGT=so_tien_chua_GTGT,
            thue_percent=thue_percent,
        )
    else:
        return RedirectResponse(url="/documents/new?error=Invalid document type", status_code=303)
