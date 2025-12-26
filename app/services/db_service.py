from __future__ import annotations

import os
from typing import Any, Dict, List, Optional
from datetime import date

from supabase import create_client, Client

from app.utils.logging_config import get_logger
from app.utils.exceptions import ContractManagementError

logger = get_logger("db_service")

_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    global _supabase_client

    if _supabase_client is None:
        url = os.environ.get("VITE_SUPABASE_URL")
        key = os.environ.get("VITE_SUPABASE_ANON_KEY")

        if not url or not key:
            raise ContractManagementError(
                "Supabase credentials not found in environment variables"
            )

        _supabase_client = create_client(url, key)
        logger.info("Supabase client initialized")

    return _supabase_client


class ContractDBService:
    @staticmethod
    def create_contract(data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            client = get_supabase_client()
            result = client.table("contracts").insert(data).execute()

            if result.data:
                logger.info(f"Contract created: {data.get('contract_no')}")
                return result.data[0]
            else:
                raise ContractManagementError("Failed to create contract")

        except Exception as e:
            logger.exception(f"Error creating contract: {e}")
            raise ContractManagementError(f"Failed to create contract: {str(e)}")

    @staticmethod
    def get_contract(contract_no: str) -> Optional[Dict[str, Any]]:
        try:
            client = get_supabase_client()
            result = client.table("contracts").select("*").eq("contract_no", contract_no).maybe_single().execute()
            return result.data

        except Exception as e:
            logger.exception(f"Error getting contract {contract_no}: {e}")
            return None

    @staticmethod
    def get_contracts(year: Optional[int] = None, limit: int = 1000) -> List[Dict[str, Any]]:
        try:
            client = get_supabase_client()
            query = client.table("contracts").select("*")

            if year:
                query = query.eq("contract_year", year)

            result = query.order("created_at", desc=True).limit(limit).execute()
            return result.data or []

        except Exception as e:
            logger.exception(f"Error getting contracts: {e}")
            return []

    @staticmethod
    def update_contract(contract_no: str, data: Dict[str, Any], current_version: int) -> Dict[str, Any]:
        try:
            client = get_supabase_client()

            data["version"] = current_version + 1

            result = client.table("contracts").update(data).eq("contract_no", contract_no).eq("version", current_version).execute()

            if not result.data:
                raise ContractManagementError(
                    "Conflict detected: Contract was modified by another user. Please refresh and try again."
                )

            logger.info(f"Contract updated: {contract_no} (version {current_version} -> {current_version + 1})")
            return result.data[0]

        except Exception as e:
            logger.exception(f"Error updating contract {contract_no}: {e}")
            if "Conflict detected" in str(e):
                raise
            raise ContractManagementError(f"Failed to update contract: {str(e)}")

    @staticmethod
    def delete_contract(contract_no: str) -> bool:
        try:
            client = get_supabase_client()
            client.table("contracts").delete().eq("contract_no", contract_no).execute()
            logger.info(f"Contract deleted: {contract_no}")
            return True

        except Exception as e:
            logger.exception(f"Error deleting contract {contract_no}: {e}")
            return False


class AnnexDBService:
    @staticmethod
    def create_annex(data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            client = get_supabase_client()
            result = client.table("annexes").insert(data).execute()

            if result.data:
                logger.info(f"Annex created: {data.get('contract_no')} - {data.get('annex_no')}")
                return result.data[0]
            else:
                raise ContractManagementError("Failed to create annex")

        except Exception as e:
            logger.exception(f"Error creating annex: {e}")
            raise ContractManagementError(f"Failed to create annex: {str(e)}")

    @staticmethod
    def get_annex(contract_no: str, annex_no: str) -> Optional[Dict[str, Any]]:
        try:
            client = get_supabase_client()
            result = (
                client.table("annexes")
                .select("*")
                .eq("contract_no", contract_no)
                .eq("annex_no", annex_no)
                .maybe_single()
                .execute()
            )
            return result.data

        except Exception as e:
            logger.exception(f"Error getting annex {contract_no}/{annex_no}: {e}")
            return None

    @staticmethod
    def get_annexes(contract_no: Optional[str] = None, year: Optional[int] = None, limit: int = 1000) -> List[Dict[str, Any]]:
        try:
            client = get_supabase_client()
            query = client.table("annexes").select("*")

            if contract_no:
                query = query.eq("contract_no", contract_no)

            result = query.order("created_at", desc=True).limit(limit).execute()
            return result.data or []

        except Exception as e:
            logger.exception(f"Error getting annexes: {e}")
            return []

    @staticmethod
    def update_annex(contract_no: str, annex_no: str, data: Dict[str, Any], current_version: int) -> Dict[str, Any]:
        try:
            client = get_supabase_client()

            data["version"] = current_version + 1

            result = (
                client.table("annexes")
                .update(data)
                .eq("contract_no", contract_no)
                .eq("annex_no", annex_no)
                .eq("version", current_version)
                .execute()
            )

            if not result.data:
                raise ContractManagementError(
                    "Conflict detected: Annex was modified by another user. Please refresh and try again."
                )

            logger.info(f"Annex updated: {contract_no}/{annex_no} (version {current_version} -> {current_version + 1})")
            return result.data[0]

        except Exception as e:
            logger.exception(f"Error updating annex {contract_no}/{annex_no}: {e}")
            if "Conflict detected" in str(e):
                raise
            raise ContractManagementError(f"Failed to update annex: {str(e)}")

    @staticmethod
    def delete_annex(contract_no: str, annex_no: str) -> bool:
        try:
            client = get_supabase_client()
            client.table("annexes").delete().eq("contract_no", contract_no).eq("annex_no", annex_no).execute()
            logger.info(f"Annex deleted: {contract_no}/{annex_no}")
            return True

        except Exception as e:
            logger.exception(f"Error deleting annex {contract_no}/{annex_no}: {e}")
            return False
