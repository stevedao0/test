"""
Helper functions for contract operations with Supabase.
Replaces Excel-based operations with database queries.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from app.services.database import ContractDB, AnnexDB, WorksDB
from app.services.auth import CurrentUser


def get_contracts_by_year(year: int) -> tuple[list[dict], list[dict]]:
    """
    Get contracts and annexes for a given year.
    Returns (contracts, annexes)
    """
    contracts = ContractDB.list_by_year(year)

    # Get annexes with contract information
    all_annexes_raw = AnnexDB.list_by_year(year)

    # Flatten annexes - extract contract info from nested structure
    annexes = []
    for annex in all_annexes_raw:
        annex_flat = annex.copy()
        if "contracts" in annex_flat and isinstance(annex_flat["contracts"], dict):
            # Extract contract_no from nested structure
            annex_flat["contract_no"] = annex_flat["contracts"].get("contract_no")
            del annex_flat["contracts"]
        annexes.append(annex_flat)

    return contracts, annexes


def create_contract_record(data: dict, user: CurrentUser) -> dict:
    """Create a new contract record in database"""
    return ContractDB.create(data, user)


def create_annex_record(data: dict, user: CurrentUser) -> dict:
    """Create a new annex record in database"""
    return AnnexDB.create(data, user)


def get_contract_by_no(contract_no: str) -> Optional[dict]:
    """Get contract by contract number"""
    return ContractDB.get_by_contract_no(contract_no)


def update_contract_record(contract_id: str, data: dict, user: CurrentUser) -> dict:
    """Update contract record"""
    return ContractDB.update(contract_id, data, user)


def delete_contract_record(contract_id: str) -> bool:
    """Delete contract record"""
    return ContractDB.delete(contract_id)


def delete_annex_record(annex_id: str) -> bool:
    """Delete annex record"""
    return AnnexDB.delete(annex_id)


def save_works_batch(works: list[dict], contract_id: str, annex_id: Optional[str], user: CurrentUser) -> int:
    """Save multiple works at once"""
    return WorksDB.create_batch(works, contract_id, annex_id, user)


def format_date_for_display(d) -> str:
    """Format date for display (dd/mm/yyyy)"""
    if d is None:
        return ""
    if isinstance(d, str):
        try:
            d = date.fromisoformat(d)
        except:
            return d
    if isinstance(d, datetime):
        return d.strftime("%d/%m/%Y")
    if isinstance(d, date):
        return d.strftime("%d/%m/%Y")
    return str(d)
