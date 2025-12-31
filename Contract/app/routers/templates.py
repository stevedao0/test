from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from starlette import status

from app.auth import get_permissions_for_user, require_any_permission, require_permission
from app.config import PROJECT_ROOT
from app.db_models import UserRow


router = APIRouter()


_TEMPLATES_DIR = PROJECT_ROOT / "templates"


def _safe_template_file(*, filename: str) -> Path:
    base = _TEMPLATES_DIR.resolve()
    target = (base / filename).resolve()

    # Prevent path traversal
    if not str(target).startswith(str(base)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid path")

    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    return target


@router.get("/templates/export/{doc_type}/docx")
def download_export_docx(doc_type: str, user: UserRow = Depends(require_any_permission("contracts.read", "annexes.read"))):
    doc = (doc_type or "").strip().lower()
    perms = get_permissions_for_user(user=user)
    if doc == "contract":
        if "contracts.read" not in perms:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        p = _safe_template_file(filename="export_template_contract.docx")
    elif doc == "annex":
        if "annexes.read" not in perms:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        p = _safe_template_file(filename="export_template_annex.docx")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid doc_type")

    return FileResponse(
        path=p,
        filename=p.name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@router.get("/templates/export/{doc_type}/xlsx")
def download_export_xlsx(doc_type: str, user: UserRow = Depends(require_any_permission("contracts.read", "annexes.read"))):
    doc = (doc_type or "").strip().lower()
    perms = get_permissions_for_user(user=user)
    if doc == "contract":
        if "contracts.read" not in perms:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        p = _safe_template_file(filename="export_template_contract.xlsx")
    elif doc == "annex":
        if "annexes.read" not in perms:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        p = _safe_template_file(filename="export_template_annex.xlsx")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid doc_type")

    return FileResponse(
        path=p,
        filename=p.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.get("/templates/import/{doc_type}/xlsx")
def download_import_xlsx(doc_type: str, user: UserRow = Depends(require_permission("catalogue.upload"))):
    doc = (doc_type or "").strip().lower()
    if doc == "contract":
        p = _safe_template_file(filename="import_danh muc Hop dong.xlsx")
    elif doc == "annex":
        p = _safe_template_file(filename="import_danh muc phu luc.xlsx")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid doc_type")

    return FileResponse(
        path=p,
        filename=p.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
