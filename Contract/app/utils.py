from __future__ import annotations

import re


def clean_opt(v) -> str:
    if v is None:
        return ""
    return str(v).strip()


def normalize_multi_emails(s: str) -> str:
    raw = clean_opt(s)
    if not raw:
        return ""
    parts = re.split(r"[;,\s]+", raw)
    parts = [p.strip() for p in parts if p.strip()]
    return ";".join(dict.fromkeys(parts))


def normalize_multi_phones(s: str) -> str:
    raw = clean_opt(s)
    if not raw:
        return ""
    parts = re.split(r"[;,\s]+", raw)
    parts = [p.strip() for p in parts if p.strip()]
    return ";".join(dict.fromkeys(parts))


def normalize_money_to_int(s: str) -> int:
    raw = clean_opt(s)
    if not raw:
        return 0
    cleaned = raw.replace("VNĐ", "").replace("VND", "")
    cleaned = cleaned.replace(".", "").replace(",", "")
    cleaned = re.sub(r"\s+", "", cleaned)
    return int(cleaned)


def format_money_number(v: int | None) -> str:
    if v is None:
        return ""
    try:
        return f"{int(v):,}".replace(",", ".")
    except Exception:
        return ""


def format_money_vnd(v: int | None) -> str:
    n = format_money_number(v)
    return f"{n} VNĐ" if n else ""


def extract_channel_id(value) -> str:
    if value is None:
        return ""
    s = str(value).strip()
    if not s:
        return ""
    m = re.search(r"(UC[0-9A-Za-z_-]{10,})", s)
    if m:
        return m.group(1)
    return ""


def normalize_youtube_channel_input(value: str) -> tuple[str, str]:
    s = clean_opt(value)
    if not s:
        return "", ""
    if s.startswith("http://") or s.startswith("https://"):
        link = s
        cid = extract_channel_id(s)
        return cid or s, link
    cid = extract_channel_id(s) or s
    link = f"https://www.youtube.com/channel/{cid}" if cid.startswith("UC") else ""
    return cid, link


def money_to_vietnamese_words(v: int | None) -> str:
    if v is None:
        return ""
    try:
        return f"{format_money_number(int(v))} đồng"
    except Exception:
        return ""


def get_breadcrumbs(path: str):
    breadcrumbs = [{"label": "Trang chủ", "url": "/"}]

    if path.startswith("/contracts"):
        breadcrumbs.append({"label": "Hợp đồng", "url": "/contracts"})
        if "/new" in path:
            breadcrumbs.append({"label": "Tạo mới", "url": None})
    elif path.startswith("/annexes"):
        breadcrumbs.append({"label": "Phụ lục", "url": "/annexes"})
        if "/new" in path:
            breadcrumbs.append({"label": "Tạo mới", "url": None})
    elif path.startswith("/works/import"):
        breadcrumbs.append({"label": "Import tác phẩm", "url": "/works/import"})
    elif path.startswith("/catalogue/upload"):
        breadcrumbs.append({"label": "Upload danh mục", "url": "/catalogue/upload"})
    elif path.startswith("/admin/ops"):
        breadcrumbs.append({"label": "Admin Ops", "url": "/admin/ops"})

    return breadcrumbs
