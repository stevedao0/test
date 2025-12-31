from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DOCX_TEMPLATE_PATH = PROJECT_ROOT / "templates" / "export_template_contract.docx"

ANNEX_TEMPLATE_PATH = PROJECT_ROOT / "templates" / "export_template_annex.docx"

CATALOGUE_TEMPLATE_PATH = PROJECT_ROOT / "templates" / "export_template_contract.xlsx"

ANNEX_CATALOGUE_TEMPLATE_PATH = PROJECT_ROOT / "templates" / "export_template_annex.xlsx"

STORAGE_DIR = PROJECT_ROOT / "storage"
STORAGE_DOCX_DIR = STORAGE_DIR / "docx"
STORAGE_EXCEL_DIR = STORAGE_DIR / "excel"

UI_DIR = PROJECT_ROOT / "app" / "ui"
UI_TEMPLATES_DIR = UI_DIR / "templates"
UI_STATIC_DIR = UI_DIR / "static"

# Legacy (kept for backward compatibility during refactor)
WEB_TEMPLATES_DIR = PROJECT_ROOT / "app" / "web_templates"
