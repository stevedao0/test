from __future__ import annotations

from datetime import date, datetime

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette import status

from app.auth import get_permissions_for_user, require_any_permission
from app.context import FIELD_NAME
from app.db_ops import _rows_from_db
from app.db_models import UserRow
from app.utils import get_breadcrumbs


router = APIRouter()


@router.get("/documents/new", response_class=HTMLResponse)
def document_form_unified(
    request: Request,
    doc_type: str | None = None,
    year: int | None = None,
    contract_no: str | None = None,
    error: str | None = None,
):
    templates = request.app.state.templates

    y = year or date.today().year
    contracts = _rows_from_db(year=y)

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
    user: UserRow = Depends(require_any_permission("contracts.create", "annexes.create")),
):
    from app.routers.annexes import create_annex
    from app.routers.contracts import _create_contract_impl
    templates = request.app.state.templates
    y = date.today().year

    perms = get_permissions_for_user(user=user)
    if doc_type == "contract":
        if "contracts.create" not in perms:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        try:
            return _create_contract_impl(
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
                user=user,
            )
        except Exception as e:
            contracts = _rows_from_db(year=y)
            contracts = [r for r in contracts if not r.get("annex_no")]
            preview = {
                "ngay_lap_hop_dong": ngay_lap_hop_dong,
                "so_hop_dong_4": so_hop_dong_4,
                "linh_vuc": linh_vuc or FIELD_NAME,
                "don_vi_ten": don_vi_ten,
                "don_vi_dia_chi": don_vi_dia_chi,
                "don_vi_dien_thoai": don_vi_dien_thoai,
                "don_vi_nguoi_dai_dien": don_vi_nguoi_dai_dien,
                "don_vi_chuc_vu": don_vi_chuc_vu,
                "don_vi_mst": don_vi_mst,
                "don_vi_email": don_vi_email,
                "so_CCCD": so_CCCD,
                "ngay_cap_CCCD": ngay_cap_CCCD,
                "nguoi_thuc_hien_email": nguoi_thuc_hien_email,
                "kenh_ten": kenh_ten,
                "kenh_id": kenh_id,
                "so_tien_chua_GTGT": so_tien_chua_GTGT,
                "thue_percent": thue_percent,
            }
            return templates.TemplateResponse(
                "document_form.html",
                {
                    "request": request,
                    "title": "Tạo tài liệu",
                    "error": str(e),
                    "doc_type": "contract",
                    "contracts": contracts,
                    "preview": preview,
                    "year": y,
                    "today": date.today().isoformat(),
                    "selected_contract_no": "",
                    "breadcrumbs": get_breadcrumbs(request.url.path),
                },
                status_code=400,
            )
    if doc_type == "annex":
        if "annexes.create" not in perms:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
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
            user=user,
        )

    return RedirectResponse(url="/documents/new?error=Invalid document type", status_code=303)
