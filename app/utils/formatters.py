from __future__ import annotations

import re
from datetime import date, datetime
from typing import Optional


def format_ddmmyyyy(v) -> str:
    if v is None:
        return ""

    if isinstance(v, datetime):
        return v.strftime("%d/%m/%Y")
    if isinstance(v, date):
        return v.strftime("%d/%m/%Y")
    s = str(v).strip()
    if not s:
        return ""

    normalized = s.replace("-", "/").replace(".", "/")

    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", normalized)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return f"{d:02d}/{mo:02d}/{y:04d}"

    return s


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


def extract_video_id(value) -> str:
    if value is None:
        return ""
    s = str(value).strip()
    if not s:
        return ""

    if s.startswith("="):
        m = re.search(r"watch\?v=([0-9A-Za-z_-]{6,})", s)
        if m:
            return m.group(1)
        m = re.search(r"HYPERLINK\(\"[^\"]*youtu(?:\.be/|be\.com/watch\?v=)([^\"&?#]+)", s, re.IGNORECASE)
        if m:
            return m.group(1)

    m = re.search(r"watch\?v=([0-9A-Za-z_-]{6,})", s)
    if m:
        return m.group(1)
    m = re.search(r"youtu\.be/([0-9A-Za-z_-]{6,})", s)
    if m:
        return m.group(1)

    if re.fullmatch(r"[0-9A-Za-z_-]{6,}", s):
        return s
    return ""


def normalize_hhmmss(s: str) -> str:
    t = (s or "").strip()
    if not t:
        return ""

    parts = [p.strip() for p in t.split(":")]
    if len(parts) == 2:
        hh = 0
        mm = int(parts[0])
        ss = int(parts[1])
    elif len(parts) == 3:
        hh = int(parts[0])
        mm = int(parts[1])
        ss = int(parts[2])
    else:
        raise ValueError("Thời lượng/thời gian phải theo định dạng hh:mm:ss hoặc mm:ss")

    if mm < 0 or mm >= 60 or ss < 0 or ss >= 60 or hh < 0:
        raise ValueError("Thời lượng/thời gian không hợp lệ")

    return f"{hh:02d}:{mm:02d}:{ss:02d}"


def normalize_time_range(s: str) -> str:
    t = (s or "").strip()
    if not t:
        return ""

    tt = t.replace("–", "-")
    parts = [p.strip() for p in tt.split("-")]
    if len(parts) != 2:
        raise ValueError("Thời gian phải theo định dạng hh:mm:ss - hh:mm:ss (hoặc mm:ss - mm:ss)")

    start = normalize_hhmmss(parts[0])
    end = normalize_hhmmss(parts[1])
    return f"{start} - {end}"


def clean_opt(s: Optional[str]) -> str:
    if s is None:
        return ""
    return s.strip()


def split_multi_values(s: str) -> list[str]:
    if not s:
        return []
    normalized = s.replace("\r\n", "\n").replace("\r", "\n")
    normalized = normalized.replace(",", ";").replace("\n", ";")
    parts = [p.strip() for p in normalized.split(";")]
    return [p for p in parts if p]


def normalize_multi_emails(s: str) -> str:
    parts = split_multi_values(clean_opt(s))
    if not parts:
        return ""
    return "; ".join(parts)


def normalize_multi_phones(s: str) -> str:
    parts = split_multi_values(clean_opt(s))
    if not parts:
        return ""

    out: list[str] = []
    for p in parts:
        compact = "".join([ch for ch in p if ch.isdigit()])
        if compact and len(compact) in (10, 11) and compact.startswith("0"):
            out.append(compact)
        else:
            out.append(" ".join(p.split()))
    return "; ".join(out)


def normalize_youtube_channel_input(raw: str) -> tuple[str, str]:
    s = (raw or "").strip()
    if not s:
        return "", ""

    m = re.search(r"(UC[0-9A-Za-z_-]{10,})", s)
    channel_id = m.group(1) if m else s
    if not channel_id.startswith("UC"):
        return channel_id, s

    return channel_id, f"https://www.youtube.com/channel/{channel_id}"


def normalize_money_to_int(s: str) -> int:
    raw = s.strip()
    raw = raw.replace("VNĐ", "").replace("VND", "").strip()
    digits = re.sub(r"[^0-9]", "", raw)
    if not digits:
        raise ValueError("Số tiền không hợp lệ")
    return int(digits)


def format_money_vnd(n: int) -> str:
    return f"{n:,} VNĐ".replace(",", ",")


def format_money_number(n: int) -> str:
    return f"{n:,}".replace(",", ",")


def vi_three_digits(n: int, *, full: bool) -> str:
    ones = [
        "không",
        "một",
        "hai",
        "ba",
        "bốn",
        "năm",
        "sáu",
        "bảy",
        "tám",
        "chín",
    ]

    tram = n // 100
    chuc = (n % 100) // 10
    donvi = n % 10

    parts: list[str] = []

    if tram > 0 or full:
        parts.append(f"{ones[tram]} trăm")

    if chuc == 0:
        if donvi != 0 and (tram > 0 or full):
            parts.append("lẻ")
    elif chuc == 1:
        parts.append("mười")
    else:
        parts.append(f"{ones[chuc]} mươi")

    if donvi == 0:
        return " ".join(parts).strip()
    if donvi == 1:
        if chuc >= 2:
            parts.append("mốt")
        else:
            parts.append("một")
        return " ".join(parts).strip()
    if donvi == 4:
        if chuc >= 2:
            parts.append("tư")
        else:
            parts.append("bốn")
        return " ".join(parts).strip()
    if donvi == 5:
        if chuc >= 1:
            parts.append("lăm")
        else:
            parts.append("năm")
        return " ".join(parts).strip()

    parts.append(ones[donvi])
    return " ".join(parts).strip()


def money_to_vietnamese_words(n: int) -> str:
    if n == 0:
        return "Không đồng"
    if n < 0:
        return "Âm " + money_to_vietnamese_words(-n)

    units = [
        (10**9, "tỷ"),
        (10**6, "triệu"),
        (10**3, "nghìn"),
    ]

    parts: list[str] = []
    remainder = n
    started = False

    for base, name in units:
        block = remainder // base
        remainder = remainder % base
        if block == 0:
            continue
        started = True
        parts.append(f"{vi_three_digits(block, full=False)} {name}")

    if remainder > 0:
        parts.append(vi_three_digits(remainder, full=started))

    text = " ".join(p for p in parts if p).strip()
    text = text[0].upper() + text[1:] if text else text
    return f"{text} đồng"


def parse_so_hop_dong_4(contract_no: str) -> str:
    if not contract_no:
        return ""
    parts = contract_no.split("/")
    return parts[0] if parts else ""


def serialize_for_json(obj):
    if isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_for_json(item) for item in obj]
    elif isinstance(obj, (date, datetime)):
        return obj.isoformat()
    else:
        return obj
