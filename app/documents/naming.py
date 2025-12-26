from __future__ import annotations

import re
import unicodedata
from datetime import datetime


def slug_filename_part(s: str) -> str:
    s = (s or "").strip()
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.replace("đ", "d").replace("Đ", "D")
    s = re.sub(r"[^0-9A-Za-z\s._-]", "", s)
    s = re.sub(r"\s+", "-", s).strip("-._ ")
    return s


def build_docx_filename(*, year: int, so_hop_dong_4: str, linh_vuc: str, kenh_ten: str, so_phu_luc: str | None = None) -> str:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")

    linh_vuc_part = "SCTT" if (linh_vuc or "").strip().lower() == "sao chép trực tuyến" else slug_filename_part(linh_vuc)

    parts: list[str] = [
        timestamp,
        slug_filename_part(str(year)),
        slug_filename_part(so_hop_dong_4),
    ]

    so_phu_luc = (so_phu_luc or "").strip()
    if so_phu_luc:
        parts.append(f"PL{slug_filename_part(so_phu_luc)}")

    if linh_vuc_part:
        parts.append(slug_filename_part(linh_vuc_part))

    kenh_part = slug_filename_part(kenh_ten)
    if kenh_part:
        parts.append(kenh_part)

    base = "_".join(p for p in parts if p)
    base = base[:180].rstrip("._- ")
    return f"{base}.docx" if base else f"{timestamp}_{year}_{so_hop_dong_4}.docx"
