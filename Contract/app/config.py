from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DOCX_TEMPLATE_PATH = PROJECT_ROOT / "templates" / "HDQTGAN_PN_MR_template.docx"

ANNEX_TEMPLATE_PATH = PROJECT_ROOT / "templates" / "HDQTGAN_PN_MR_annex_template.docx"

CATALOGUE_TEMPLATE_PATH = PROJECT_ROOT / "Mau danh muc" / "Nam_SHD_SCTT_Ten kenh_MR_danh muc.xlsx"

ANNEX_CATALOGUE_TEMPLATE_PATH = PROJECT_ROOT / "Mau danh muc" / "Nam_SHD_SPL_SCTT_Ten kenh_MR_danh muc.xlsx"

STORAGE_DIR = PROJECT_ROOT / "storage"
STORAGE_DOCX_DIR = STORAGE_DIR / "docx"
STORAGE_EXCEL_DIR = STORAGE_DIR / "excel"

UI_DIR = PROJECT_ROOT / "app" / "ui"
UI_TEMPLATES_DIR = UI_DIR / "templates"
UI_STATIC_DIR = UI_DIR / "static"

# Legacy (kept for backward compatibility during refactor)
WEB_TEMPLATES_DIR = PROJECT_ROOT / "app" / "web_templates"
