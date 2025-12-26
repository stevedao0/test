from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from app.core.supabase import get_supabase
from app.services.auth import CurrentUser


def _serialize_date(d) -> Optional[str]:
    if d is None:
        return None
    if isinstance(d, datetime):
        return d.date().isoformat()
    if isinstance(d, date):
        return d.isoformat()
    return str(d)


class ContractDB:
    @staticmethod
    def create(data: dict, user: CurrentUser) -> dict:
        supabase = get_supabase()

        insert_data = {
            "contract_no": data["contract_no"],
            "contract_year": data["contract_year"],
            "ngay_lap_hop_dong": _serialize_date(data.get("ngay_lap_hop_dong")),
            "linh_vuc": data.get("linh_vuc", "Sao chep truc tuyen"),
            "region_code": data.get("region_code", "HDQTGAN-PN"),
            "field_code": data.get("field_code", "MR"),
            "don_vi_ten": data.get("don_vi_ten", ""),
            "don_vi_dia_chi": data.get("don_vi_dia_chi"),
            "don_vi_dien_thoai": data.get("don_vi_dien_thoai"),
            "don_vi_nguoi_dai_dien": data.get("don_vi_nguoi_dai_dien"),
            "don_vi_chuc_vu": data.get("don_vi_chuc_vu", "Giam doc"),
            "don_vi_mst": data.get("don_vi_mst"),
            "don_vi_email": data.get("don_vi_email"),
            "so_cccd": data.get("so_CCCD") or data.get("so_cccd"),
            "ngay_cap_cccd": data.get("ngay_cap_CCCD") or data.get("ngay_cap_cccd"),
            "kenh_ten": data.get("kenh_ten"),
            "kenh_id": data.get("kenh_id"),
            "nguoi_thuc_hien_email": data.get("nguoi_thuc_hien_email"),
            "so_tien_chua_gtgt_value": data.get("so_tien_chua_GTGT_value"),
            "so_tien_chua_gtgt_text": data.get("so_tien_chua_GTGT_text"),
            "thue_percent": data.get("thue_percent"),
            "thue_gtgt_value": data.get("thue_GTGT_value"),
            "thue_gtgt_text": data.get("thue_GTGT_text"),
            "so_tien_value": data.get("so_tien_value"),
            "so_tien_text": data.get("so_tien_text"),
            "so_tien_bang_chu": data.get("so_tien_bang_chu"),
            "docx_path": data.get("docx_path"),
            "catalogue_path": data.get("catalogue_path"),
            "created_by": user.id,
            "updated_by": user.id,
        }

        response = supabase.table("contracts").insert(insert_data).execute()
        return response.data[0] if response.data else {}

    @staticmethod
    def get_by_contract_no(contract_no: str) -> Optional[dict]:
        supabase = get_supabase()
        response = supabase.table("contracts").select("*").eq("contract_no", contract_no).maybeSingle().execute()
        return response.data

    @staticmethod
    def get_by_id(contract_id: str) -> Optional[dict]:
        supabase = get_supabase()
        response = supabase.table("contracts").select("*").eq("id", contract_id).maybeSingle().execute()
        return response.data

    @staticmethod
    def list_by_year(year: int) -> list[dict]:
        supabase = get_supabase()
        response = supabase.table("contracts").select("*").eq("contract_year", year).order("created_at", desc=True).execute()
        return response.data or []

    @staticmethod
    def update(contract_id: str, data: dict, user: CurrentUser) -> dict:
        supabase = get_supabase()

        update_data = {k: v for k, v in data.items() if v is not None}
        update_data["updated_by"] = user.id
        update_data["updated_at"] = datetime.now().isoformat()

        if "ngay_lap_hop_dong" in update_data:
            update_data["ngay_lap_hop_dong"] = _serialize_date(update_data["ngay_lap_hop_dong"])

        response = supabase.table("contracts").update(update_data).eq("id", contract_id).execute()
        return response.data[0] if response.data else {}

    @staticmethod
    def delete(contract_id: str) -> bool:
        supabase = get_supabase()
        response = supabase.table("contracts").delete().eq("id", contract_id).execute()
        return len(response.data) > 0 if response.data else False

    @staticmethod
    def search(year: int, query: str) -> list[dict]:
        supabase = get_supabase()
        response = supabase.table("contracts").select("*").eq("contract_year", year).or_(
            f"contract_no.ilike.%{query}%,kenh_ten.ilike.%{query}%,don_vi_ten.ilike.%{query}%"
        ).execute()
        return response.data or []


class AnnexDB:
    @staticmethod
    def create(data: dict, user: CurrentUser) -> dict:
        supabase = get_supabase()

        insert_data = {
            "contract_id": data["contract_id"],
            "annex_no": data["annex_no"],
            "ngay_ky_phu_luc": _serialize_date(data.get("ngay_ky_phu_luc")),
            "don_vi_ten": data.get("don_vi_ten"),
            "don_vi_dia_chi": data.get("don_vi_dia_chi"),
            "don_vi_dien_thoai": data.get("don_vi_dien_thoai"),
            "don_vi_nguoi_dai_dien": data.get("don_vi_nguoi_dai_dien"),
            "don_vi_chuc_vu": data.get("don_vi_chuc_vu"),
            "don_vi_mst": data.get("don_vi_mst"),
            "don_vi_email": data.get("don_vi_email"),
            "so_cccd": data.get("so_CCCD") or data.get("so_cccd"),
            "ngay_cap_cccd": data.get("ngay_cap_CCCD") or data.get("ngay_cap_cccd"),
            "kenh_ten": data.get("kenh_ten"),
            "kenh_id": data.get("kenh_id"),
            "nguoi_thuc_hien_email": data.get("nguoi_thuc_hien_email"),
            "so_tien_chua_gtgt_value": data.get("so_tien_chua_GTGT_value"),
            "so_tien_chua_gtgt_text": data.get("so_tien_chua_GTGT_text"),
            "thue_percent": data.get("thue_percent"),
            "thue_gtgt_value": data.get("thue_GTGT_value"),
            "thue_gtgt_text": data.get("thue_GTGT_text"),
            "so_tien_value": data.get("so_tien_value"),
            "so_tien_text": data.get("so_tien_text"),
            "so_tien_bang_chu": data.get("so_tien_bang_chu"),
            "docx_path": data.get("docx_path"),
            "catalogue_path": data.get("catalogue_path"),
            "created_by": user.id,
            "updated_by": user.id,
        }

        response = supabase.table("annexes").insert(insert_data).execute()
        return response.data[0] if response.data else {}

    @staticmethod
    def get_by_contract(contract_id: str) -> list[dict]:
        supabase = get_supabase()
        response = supabase.table("annexes").select("*").eq("contract_id", contract_id).order("annex_no").execute()
        return response.data or []

    @staticmethod
    def get_by_id(annex_id: str) -> Optional[dict]:
        supabase = get_supabase()
        response = supabase.table("annexes").select("*").eq("id", annex_id).maybeSingle().execute()
        return response.data

    @staticmethod
    def list_by_year(year: int) -> list[dict]:
        supabase = get_supabase()
        response = supabase.table("annexes").select("*, contracts!inner(contract_year, contract_no)").eq("contracts.contract_year", year).order("created_at", desc=True).execute()
        return response.data or []

    @staticmethod
    def update(annex_id: str, data: dict, user: CurrentUser) -> dict:
        supabase = get_supabase()

        update_data = {k: v for k, v in data.items() if v is not None}
        update_data["updated_by"] = user.id
        update_data["updated_at"] = datetime.now().isoformat()

        if "ngay_ky_phu_luc" in update_data:
            update_data["ngay_ky_phu_luc"] = _serialize_date(update_data["ngay_ky_phu_luc"])

        response = supabase.table("annexes").update(update_data).eq("id", annex_id).execute()
        return response.data[0] if response.data else {}

    @staticmethod
    def delete(annex_id: str) -> bool:
        supabase = get_supabase()
        response = supabase.table("annexes").delete().eq("id", annex_id).execute()
        return len(response.data) > 0 if response.data else False


class WorksDB:
    @staticmethod
    def create_batch(works: list[dict], contract_id: str, annex_id: Optional[str], user: CurrentUser) -> int:
        supabase = get_supabase()

        insert_data = []
        for w in works:
            insert_data.append({
                "contract_id": contract_id,
                "annex_id": annex_id,
                "stt": w.get("stt"),
                "id_link": w.get("id_link"),
                "youtube_url": w.get("youtube_url"),
                "id_work": w.get("id_work"),
                "musical_work": w.get("musical_work"),
                "author": w.get("author"),
                "composer": w.get("composer"),
                "lyricist": w.get("lyricist"),
                "time_range": w.get("time_range"),
                "duration": w.get("duration"),
                "effective_date": w.get("effective_date"),
                "expiration_date": w.get("expiration_date"),
                "usage_type": w.get("usage_type"),
                "royalty_rate": str(w.get("royalty_rate", "")) if w.get("royalty_rate") else None,
                "note": w.get("note"),
                "imported_at": w.get("imported_at"),
                "nguoi_thuc_hien": w.get("nguoi_thuc_hien"),
                "created_by": user.id,
            })

        if insert_data:
            supabase.table("works").insert(insert_data).execute()

        return len(insert_data)

    @staticmethod
    def get_by_contract(contract_id: str) -> list[dict]:
        supabase = get_supabase()
        response = supabase.table("works").select("*").eq("contract_id", contract_id).order("stt").execute()
        return response.data or []

    @staticmethod
    def get_by_annex(annex_id: str) -> list[dict]:
        supabase = get_supabase()
        response = supabase.table("works").select("*").eq("annex_id", annex_id).order("stt").execute()
        return response.data or []

    @staticmethod
    def count_by_year(year: int) -> int:
        supabase = get_supabase()
        response = supabase.table("works").select("id", count="exact").eq("contracts.contract_year", year).execute()
        return response.count or 0


class AuditLogDB:
    @staticmethod
    def get_by_record(table_name: str, record_id: str, limit: int = 50) -> list[dict]:
        supabase = get_supabase()
        response = supabase.table("audit_logs").select("*").eq("table_name", table_name).eq("record_id", record_id).order("created_at", desc=True).limit(limit).execute()
        return response.data or []

    @staticmethod
    def get_recent(limit: int = 100) -> list[dict]:
        supabase = get_supabase()
        response = supabase.table("audit_logs").select("*").order("created_at", desc=True).limit(limit).execute()
        return response.data or []

    @staticmethod
    def get_by_user(user_id: str, limit: int = 50) -> list[dict]:
        supabase = get_supabase()
        response = supabase.table("audit_logs").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
        return response.data or []
