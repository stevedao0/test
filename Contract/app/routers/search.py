from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import or_

from app.auth import require_permission
from app.db import session_scope
from app.db_models import ContractRecordRow, UserRow, WorkRow
from app.utils import get_breadcrumbs


router = APIRouter()


def _norm(s: str | None) -> str:
    return (s or "").strip()


@router.get("/search", response_class=HTMLResponse)
def search_view(
    request: Request,
    q: str | None = None,
    scope: str | None = None,
    year: str | None = None,
    user: UserRow = Depends(require_permission("portal.access")),
):
    templates = request.app.state.templates

    query = _norm(q)
    sc = (_norm(scope) or "all").lower()

    year_int: int | None = None
    try:
        yraw = _norm(year)
        year_int = int(yraw) if yraw else None
    except Exception:
        year_int = None

    is_admin_mod = user.role in ("admin", "mod")
    owner_filter = None if is_admin_mod else user.username

    results: list[dict] = []

    if not query:
        return templates.TemplateResponse(
            "search.html",
            {
                "request": request,
                "title": "Tìm kiếm",
                "q": "",
                "scope": sc,
                "year": year_int or "",
                "is_admin_mod": is_admin_mod,
                "rows": results,
                "breadcrumbs": get_breadcrumbs(request.url.path),
            },
        )

    like = f"%{query}%"

    with session_scope() as db:
        if sc in ("all", "contracts", "annexes"):
            qc = db.query(ContractRecordRow)
            if year_int:
                qc = qc.filter(ContractRecordRow.contract_year == year_int)
            if owner_filter:
                qc = qc.filter(ContractRecordRow.nguoi_thuc_hien_email == owner_filter)

            qc = qc.filter(
                or_(
                    ContractRecordRow.contract_no.ilike(like),
                    ContractRecordRow.annex_no.ilike(like),
                    ContractRecordRow.kenh_ten.ilike(like),
                    ContractRecordRow.kenh_id.ilike(like),
                    ContractRecordRow.don_vi_ten.ilike(like),
                    ContractRecordRow.don_vi_email.ilike(like),
                    ContractRecordRow.nguoi_thuc_hien_email.ilike(like),
                )
            )

            rows = qc.order_by(ContractRecordRow.contract_year.desc()).limit(200).all()
            for r in rows:
                if sc == "contracts" and r.annex_no is not None:
                    continue
                if sc == "annexes" and r.annex_no is None:
                    continue

                results.append(
                    {
                        "kind": "annex" if r.annex_no else "contract",
                        "year": r.contract_year,
                        "contract_no": r.contract_no,
                        "annex_no": r.annex_no or "",
                        "kenh_ten": r.kenh_ten or "",
                        "don_vi_ten": r.don_vi_ten or "",
                        "nguoi_thuc_hien": r.nguoi_thuc_hien_email or "",
                        "url": f"/contracts?year={r.contract_year}",
                    }
                )

        if sc in ("all", "works"):
            qw = db.query(WorkRow)
            if year_int:
                qw = qw.filter(WorkRow.year == year_int)
            if owner_filter:
                qw = qw.filter(WorkRow.nguoi_thuc_hien == owner_filter)

            qw = qw.filter(
                or_(
                    WorkRow.contract_no.ilike(like),
                    WorkRow.annex_no.ilike(like),
                    WorkRow.ten_kenh.ilike(like),
                    WorkRow.id_channel.ilike(like),
                    WorkRow.id_work.ilike(like),
                    WorkRow.musical_work.ilike(like),
                    WorkRow.author.ilike(like),
                    WorkRow.composer.ilike(like),
                    WorkRow.lyricist.ilike(like),
                    WorkRow.id_link.ilike(like),
                    WorkRow.youtube_url.ilike(like),
                    WorkRow.nguoi_thuc_hien.ilike(like),
                )
            )

            rows = qw.order_by(WorkRow.year.desc(), WorkRow.id.desc()).limit(200).all()
            for r in rows:
                results.append(
                    {
                        "kind": "work",
                        "year": r.year,
                        "contract_no": r.contract_no,
                        "annex_no": r.annex_no or "",
                        "title": r.musical_work or "",
                        "id_work": r.id_work or "",
                        "id_link": r.id_link or "",
                        "nguoi_thuc_hien": r.nguoi_thuc_hien or "",
                        "url": f"/works/import",
                    }
                )

        if sc in ("all", "users") and is_admin_mod:
            qu = db.query(UserRow).filter(or_(UserRow.username.ilike(like), UserRow.role.ilike(like)))
            rows = qu.order_by(UserRow.role.asc(), UserRow.username.asc()).limit(200).all()
            for r in rows:
                results.append(
                    {
                        "kind": "user",
                        "username": r.username,
                        "role": r.role,
                        "created_at": r.created_at,
                        "url": "/admin/users",
                    }
                )

    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "title": "Tìm kiếm",
            "q": query,
            "scope": sc,
            "year": year_int or "",
            "is_admin_mod": is_admin_mod,
            "rows": results,
            "breadcrumbs": get_breadcrumbs(request.url.path),
        },
    )
