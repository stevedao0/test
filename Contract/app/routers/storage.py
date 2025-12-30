from __future__ import annotations

from datetime import datetime
from io import BytesIO

from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse

from app.config import STORAGE_DOCX_DIR, STORAGE_EXCEL_DIR
from app.db_ops import _db_available, _export_contracts_excel_bytes, _export_works_excel_bytes


router = APIRouter()


@router.get("/storage/excel/download/{year}")
def download_contracts_excel(year: int):
    if not _db_available():
        return JSONResponse({"error": "DB không tồn tại"}, status_code=500)

    data = _export_contracts_excel_bytes(year=year)
    return StreamingResponse(
        BytesIO(data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="contracts_{year}.xlsx"'},
    )


@router.get("/storage/excel/works/download/{year}")
def download_works_excel(year: int):
    if not _db_available():
        return JSONResponse({"error": "DB không tồn tại"}, status_code=500)

    data = _export_works_excel_bytes(year=year)
    return StreamingResponse(
        BytesIO(data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="works_contract_{year}.xlsx"'},
    )


@router.get("/storage/files/{year}")
def list_saved_files(year: int):
    year_dir_docx = STORAGE_DOCX_DIR / str(year)
    year_dir_excel = STORAGE_EXCEL_DIR / str(year)

    files = []

    if year_dir_docx.exists():
        for f in year_dir_docx.glob("*.docx"):
            files.append(
                {
                    "name": f.name,
                    "type": "docx",
                    "size": f.stat().st_size,
                    "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
                    "url": f"/storage/docx/{year}/{f.name}",
                }
            )

    if year_dir_excel.exists():
        for f in year_dir_excel.glob("*.xlsx"):
            files.append(
                {
                    "name": f.name,
                    "type": "xlsx",
                    "size": f.stat().st_size,
                    "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
                    "url": f"/storage/excel/{year}/{f.name}",
                }
            )

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
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@router.get("/storage/excel/{year}/{filename}")
def download_excel_file(year: int, filename: str):
    file_path = STORAGE_EXCEL_DIR / str(year) / filename
    if not file_path.exists():
        return JSONResponse({"error": "File không tồn tại"}, status_code=404)
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
