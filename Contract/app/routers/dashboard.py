from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.auth import require_permission
from app.db import session_scope
from app.db_models import ContractRecordRow, UserRow, WorkRow
from app.utils import get_breadcrumbs


router = APIRouter()


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_view(request: Request, user: UserRow = Depends(require_permission("portal.access"))):
    templates = request.app.state.templates

    is_admin_mod = user.role in ("admin", "mod")
    owner_filter = None if is_admin_mod else user.username

    today = date.today()
    year = today.year

    with session_scope() as db:
        qc = db.query(ContractRecordRow).filter(ContractRecordRow.contract_year == year)
        if owner_filter:
            qc = qc.filter(ContractRecordRow.nguoi_thuc_hien_email == owner_filter)
        c_rows = qc.all()

        qw = db.query(WorkRow).filter(WorkRow.year == year)
        if owner_filter:
            qw = qw.filter(WorkRow.nguoi_thuc_hien == owner_filter)
        w_count = qw.count()

    contracts = [r for r in c_rows if r.annex_no is None]
    annexes = [r for r in c_rows if r.annex_no is not None]

    total_contract_value = sum(int(r.so_tien_value or 0) for r in contracts)
    total_annex_value = sum(int(r.so_tien_value or 0) for r in annexes)

    # Top channels by total_value (contracts only)
    by_channel: dict[str, int] = {}
    for r in contracts:
        key = (r.kenh_ten or r.kenh_id or "(unknown)").strip() or "(unknown)"
        by_channel[key] = by_channel.get(key, 0) + int(r.so_tien_value or 0)
    top_channels = sorted(by_channel.items(), key=lambda x: x[1], reverse=True)[:8]

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "title": "Dashboard",
            "year": year,
            "is_admin_mod": is_admin_mod,
            "owner": owner_filter or "",
            "stats": {
                "contracts_count": len(contracts),
                "annexes_count": len(annexes),
                "works_count": int(w_count or 0),
                "contracts_total_value": total_contract_value,
                "annexes_total_value": total_annex_value,
            },
            "top_channels": [
                {"kenh": k, "total_value": v} for (k, v) in top_channels
            ],
            "breadcrumbs": get_breadcrumbs(request.url.path),
        },
    )
