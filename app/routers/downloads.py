from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

from app.config import STORAGE_DOCX_DIR, STORAGE_EXCEL_DIR

router = APIRouter()


@router.get("/download/{year}/{filename}")
def download_docx(year: int, filename: str):
    path = STORAGE_DOCX_DIR / str(year) / filename
    if not path.exists():
        return HTMLResponse("Not found", status_code=404)
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename,
    )


@router.get("/download_excel/{year}/{filename}")
def download_excel(year: int, filename: str):
    path = STORAGE_EXCEL_DIR / str(year) / filename
    if not path.exists():
        return HTMLResponse("Not found", status_code=404)
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename,
    )


@router.get("/storage/excel/download/{year}")
def download_contracts_excel(year: int):
    excel_path = STORAGE_EXCEL_DIR / f"contracts_{year}.xlsx"
    if not excel_path.exists():
        return JSONResponse({"error": "File không tồn tại"}, status_code=404)
    return FileResponse(
        path=excel_path,
        filename=f"contracts_{year}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.get("/storage/excel/works/download/{year}")
def download_works_excel(year: int):
    excel_path = STORAGE_EXCEL_DIR / f"works_contract_{year}.xlsx"
    if not excel_path.exists():
        return JSONResponse({"error": "File không tồn tại"}, status_code=404)
    return FileResponse(
        path=excel_path,
        filename=f"works_contract_{year}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.get("/storage/files/{year}")
def list_saved_files(year: int):
    year_dir_docx = STORAGE_DOCX_DIR / str(year)
    year_dir_excel = STORAGE_EXCEL_DIR / str(year)

    files = []

    if year_dir_docx.exists():
        for f in year_dir_docx.glob("*.docx"):
            files.append({
                "name": f.name,
                "type": "docx",
                "size": f.stat().st_size,
                "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
                "url": f"/storage/docx/{year}/{f.name}"
            })

    if year_dir_excel.exists():
        for f in year_dir_excel.glob("*.xlsx"):
            files.append({
                "name": f.name,
                "type": "xlsx",
                "size": f.stat().st_size,
                "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
                "url": f"/storage/excel/{year}/{f.name}"
            })

    files.sort(key=lambda x: x["modified"], reverse=True)
    return JSONResponse(files)


@router.get("/storage/docx/{year}/{filename}")
def download_docx_file(year: int, filename: str):
    file_path = STORAGE_DOCX_DIR / str(year) / filename
    if not file_path.exists():
        return JSONResponse({"error": "File không tồn tại"}, status_code=404)
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


@router.get("/storage/excel/{year}/{filename}")
def download_excel_file(year: int, filename: str):
    file_path = STORAGE_EXCEL_DIR / str(year) / filename
    if not file_path.exists():
        return JSONResponse({"error": "File không tồn tại"}, status_code=404)
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
