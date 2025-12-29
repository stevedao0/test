from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, Float, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ContractRecordRow(Base):
    __tablename__ = "contract_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    contract_no: Mapped[str] = mapped_column(String(128), nullable=False)
    contract_year: Mapped[int] = mapped_column(Integer, nullable=False)
    annex_no: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    ngay_lap_hop_dong: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    linh_vuc: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    region_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    field_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    don_vi_ten: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    don_vi_dia_chi: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    don_vi_dien_thoai: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    don_vi_nguoi_dai_dien: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    don_vi_chuc_vu: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    don_vi_mst: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    don_vi_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    so_cccd: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    ngay_cap_cccd: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    kenh_ten: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    kenh_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    nguoi_thuc_hien_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    so_tien_nhuan_but_value: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    so_tien_nhuan_but_text: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    so_tien_chua_gtgt_value: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    so_tien_chua_gtgt_text: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    thue_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    thue_gtgt_value: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    thue_gtgt_text: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    so_tien_value: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    so_tien_text: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    so_tien_bang_chu: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    docx_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    catalogue_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    imported_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint("contract_year", "contract_no", "annex_no", name="uq_contract_annex"),
        Index("ix_contract_year", "contract_year"),
        Index("ix_contract_no", "contract_no"),
        Index("ix_contract_year_contract_no", "contract_year", "contract_no"),
    )


class WorkRow(Base):
    __tablename__ = "works"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    year: Mapped[int] = mapped_column(Integer, nullable=False)
    contract_no: Mapped[str] = mapped_column(String(128), nullable=False)
    annex_no: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    ngay_ky_hop_dong: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    ngay_ky_phu_luc: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    nguoi_thuc_hien: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    ten_kenh: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    id_channel: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    link_kenh: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    stt: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    id_link: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    youtube_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    id_work: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    musical_work: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    author: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    composer: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    lyricist: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    time_range: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    duration: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    effective_date: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    expiration_date: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    usage_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    royalty_rate: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    imported_at: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    __table_args__ = (
        Index("ix_works_year", "year"),
        Index("ix_works_year_contract", "year", "contract_no"),
        Index("ix_works_id_link", "id_link"),
    )


class UserRow(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    password_salt: Mapped[str] = mapped_column(String(64), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
