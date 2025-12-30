from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from starlette import status

from app.auth import require_role
from app.config import STORAGE_DIR
from app.db_models import UserRow
from app.utils import get_breadcrumbs


router = APIRouter()


@router.get("/admin/ops", response_class=HTMLResponse)
def admin_ops(request: Request, user: UserRow = Depends(require_role("admin"))):
    templates = request.app.state.templates

    logs_dir = STORAGE_DIR / "logs"
    backups_dir = STORAGE_DIR / "backups"

    logs: list[dict] = []
    backups: list[dict] = []

    if logs_dir.exists():
        for p in sorted(logs_dir.glob("**/*")):
            if p.is_file():
                logs.append({"name": str(p.relative_to(logs_dir)).replace("\\", "/"), "size": p.stat().st_size})

    if backups_dir.exists():
        for p in sorted(backups_dir.glob("**/*")):
            if p.is_file():
                backups.append({"name": str(p.relative_to(backups_dir)).replace("\\", "/"), "size": p.stat().st_size})

    return templates.TemplateResponse(
        "admin_ops.html",
        {
            "request": request,
            "title": "Admin Ops",
            "logs": logs,
            "backups": backups,
            "breadcrumbs": get_breadcrumbs(request.url.path),
        },
    )


@router.get("/admin/ops/download/{kind}/{path:path}")
def admin_ops_download(kind: str, path: str, user: UserRow = Depends(require_role("admin"))):
    base = STORAGE_DIR / ("logs" if kind == "logs" else "backups")
    target = (base / path).resolve()
    base_resolved = base.resolve()
    if not str(target).startswith(str(base_resolved)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid path")
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return FileResponse(path=target, filename=target.name)
