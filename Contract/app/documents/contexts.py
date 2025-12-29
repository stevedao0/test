from __future__ import annotations

from app.services.docx_renderer import date_parts


def build_contract_context(*, base: dict, ngay_lap_hop_dong, ngay_ky_hop_dong: str) -> dict:
    ctx = dict(base)
    ctx.update(date_parts(ngay_lap_hop_dong))
    ctx["ngay_ky_hop_dong"] = ngay_ky_hop_dong
    return ctx
