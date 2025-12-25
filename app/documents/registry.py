from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from app.config import ANNEX_TEMPLATE_PATH, DOCX_TEMPLATE_PATH


class DocumentType(str, Enum):
    CONTRACT = "contract"
    ANNEX = "annex"


@dataclass(frozen=True)
class DocumentSpec:
    field_code: str
    document_type: DocumentType
    template_path: Path


def get_document_spec(*, field_code: str, document_type: DocumentType) -> DocumentSpec:
    if field_code == "MR" and document_type == DocumentType.CONTRACT:
        return DocumentSpec(field_code=field_code, document_type=document_type, template_path=DOCX_TEMPLATE_PATH)

    if field_code == "MR" and document_type == DocumentType.ANNEX:
        return DocumentSpec(field_code=field_code, document_type=document_type, template_path=ANNEX_TEMPLATE_PATH)

    raise KeyError(f"No template registered for field_code={field_code} document_type={document_type}")
