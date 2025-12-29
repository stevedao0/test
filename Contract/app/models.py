from __future__ import annotations

from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class ContractCreate(BaseModel):
    ngay_lap_hop_dong: date
    so_hop_dong_4: str = Field(pattern=r"^\d{4}$")

    linh_vuc: Optional[str] = None

    don_vi_ten: Optional[str] = None
    don_vi_dia_chi: Optional[str] = None
    don_vi_dien_thoai: Optional[str] = None
    don_vi_nguoi_dai_dien: Optional[str] = None
    don_vi_chuc_vu: Optional[str] = "Giám đốc"
    don_vi_mst: Optional[str] = None
    don_vi_email: Optional[str] = None

    so_CCCD: Optional[str] = None
    ngay_cap_CCCD: Optional[str] = None

    kenh_ten: Optional[str] = None
    kenh_id: Optional[str] = None

    nguoi_thuc_hien_email: Optional[str] = None

    # Option B: pre-VAT amount and VAT percent
    so_tien_chua_GTGT: Optional[str] = None
    thue_percent: Optional[str] = None

    # Legacy field (kept for backward compatibility)
    so_tien_nhuan_but: Optional[str] = None  # keep original formatting, normalize later


class ContractRecord(BaseModel):
    contract_no: str
    contract_year: int
    annex_no: Optional[str] = None
    ngay_lap_hop_dong: date
    linh_vuc: str
    region_code: str
    field_code: str

    don_vi_ten: str
    don_vi_dia_chi: str
    don_vi_dien_thoai: str
    don_vi_nguoi_dai_dien: str
    don_vi_chuc_vu: str
    don_vi_mst: str
    don_vi_email: str

    so_CCCD: Optional[str] = None
    ngay_cap_CCCD: Optional[str] = None

    kenh_ten: str
    kenh_id: str

    nguoi_thuc_hien_email: Optional[str] = None

    so_tien_nhuan_but_value: Optional[int] = None
    so_tien_nhuan_but_text: Optional[str] = None

    # Option B breakdown
    so_tien_chua_GTGT_value: Optional[int] = None
    so_tien_chua_GTGT_text: Optional[str] = None
    thue_percent: Optional[float] = None
    thue_GTGT_value: Optional[int] = None
    thue_GTGT_text: Optional[str] = None
    so_tien_value: Optional[int] = None
    so_tien_text: Optional[str] = None
    so_tien_bang_chu: Optional[str] = None

    docx_path: str
    catalogue_path: Optional[str] = None
