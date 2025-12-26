from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import UI_STATIC_DIR, UI_TEMPLATES_DIR, WEB_TEMPLATES_DIR
from app.routers import annexes, contracts, documents, downloads, works

app = FastAPI()


def pick_existing_dir(primary: Path, fallback: Path) -> Path:
    try:
        if primary.exists():
            for _ in primary.iterdir():
                return primary
    except Exception:
        pass
    return fallback


def pick_templates_dir(primary: Path, fallback: Path) -> Path:
    try:
        if primary.exists() and (primary / "document_form.html").exists():
            return primary
    except Exception:
        pass
    return fallback


def pick_static_dir(primary: Path, fallback: Path) -> Path:
    try:
        if primary.exists() and (primary / "css" / "main.css").exists():
            return primary
    except Exception:
        pass
    return fallback


templates_dir = pick_templates_dir(UI_TEMPLATES_DIR, WEB_TEMPLATES_DIR)
static_dir = pick_static_dir(UI_STATIC_DIR, Path("app/static"))

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

app.include_router(documents.router)
app.include_router(contracts.router)
app.include_router(annexes.router)
app.include_router(works.router)
app.include_router(downloads.router)
