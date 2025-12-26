# Excel to Supabase Migration Guide

## Overview

Dự án đang migrate từ lưu trữ data trong Excel sang Supabase database.

## Migration Status

✅ **Đã hoàn thành:**
- Database schema (Supabase)
- Database service layer (`app/services/database.py`)
- Helper functions (`app/services/contract_helpers.py`)
- Migration script (`migrate_excel_to_supabase.py`)
- Imports trong `main.py`
- `/api/contracts` GET endpoint
- `/contracts` GET list endpoint

🔄 **Đang thực hiện:**
- Migration các endpoints còn lại trong `main.py`

## Steps to Complete Migration

### 1. Run Migration Script

```bash
python migrate_excel_to_supabase.py
```

Script này sẽ import:
- Contracts từ `storage/excel/contracts_2025.xlsx`
- Annexes từ `storage/excel/contracts_2025.xlsx`
- Works từ `storage/excel/works_contract_2025.xlsx`

### 2. Migrate Remaining Endpoints

Cần thay thế tất cả Excel operations trong các endpoints sau:

#### A. Works Import (`/works/import` POST - line 334-473)
**Cũ:**
```python
append_works_rows(excel_path=out_path, rows=out_rows)
```

**Mới:**
```python
# Find or create contract
contract = get_contract_by_no(contract_no)
if not contract:
    # Create contract if not exists
    contract_data = {
        "contract_no": contract_no,
        "contract_year": year,
        ...
    }
    contract = create_contract_record(contract_data, current_user)

# Find annex if exists
annex_id = None
if annex_no:
    annexes = AnnexDB.get_by_contract(contract["id"])
    for a in annexes:
        if a.get("annex_no") == annex_no:
            annex_id = a["id"]
            break

# Save works
works_data = []
for row in out_rows:
    works_data.append({
        "stt": row["stt"],
        "id_link": row["id_link"],
        "youtube_url": row["youtube_url"],
        ... # all other fields
    })

save_works_batch(works_data, contract["id"], annex_id, current_user)
```

#### B. Contract Creation (`/contracts` POST - line 670-893)
**Cũ (line 879):**
```python
append_contract_row(excel_path=excel_path, record=record)
```

**Mới:**
```python
contract_data = {
    "contract_no": contract_no,
    "contract_year": year,
    "ngay_lap_hop_dong": payload.ngay_lap_hop_dong,
    "linh_vuc": linh_vuc_value,
    "region_code": REGION_CODE,
    "field_code": FIELD_CODE,
    "don_vi_ten": payload.don_vi_ten,
    "don_vi_dia_chi": payload.don_vi_dia_chi,
    "don_vi_dien_thoai": payload.don_vi_dien_thoai,
    "don_vi_nguoi_dai_dien": payload.don_vi_nguoi_dai_dien,
    "don_vi_chuc_vu": payload.don_vi_chuc_vu,
    "don_vi_mst": payload.don_vi_mst,
    "don_vi_email": payload.don_vi_email,
    "so_CCCD": payload.so_CCCD or "",
    "ngay_cap_CCCD": payload.ngay_cap_CCCD or "",
    "kenh_ten": payload.kenh_ten,
    "kenh_id": payload.kenh_id,
    "nguoi_thuc_hien_email": payload.nguoi_thuc_hien_email or "",
    "so_tien_chua_GTGT_value": pre_vat_value,
    "so_tien_chua_GTGT_text": format_money_number(pre_vat_value) if pre_vat_value else "",
    "thue_percent": vat_percent_value,
    "thue_GTGT_value": vat_value,
    "thue_GTGT_text": format_money_number(vat_value) if vat_value else "",
    "so_tien_value": total_value,
    "so_tien_text": format_money_number(total_value) if total_value else "",
    "so_tien_bang_chu": total_words,
    "docx_path": str(out_docx_path),
    "catalogue_path": str(out_catalogue_path),
}
create_contract_record(contract_data, current_user)
```

#### C. Contract Detail (`/contracts/{year}/detail` - line 1126-1156)
**Cũ:**
```python
rows = read_contracts(excel_path=excel_path)
contract = None
for r in rows:
    if r.get("contract_no") == contract_no and not r.get("annex_no"):
        contract = r
        break
annexes = [r for r in rows if r.get("contract_no") == contract_no and r.get("annex_no")]
```

**Mới:**
```python
contract = get_contract_by_no(contract_no)
if not contract or contract.get("contract_year") != year:
    return JSONResponse({"error": f"Không tìm thấy hợp đồng: {contract_no}"}, status_code=404)

annexes = AnnexDB.get_by_contract(contract["id"])
```

#### D. Contract Edit Form (`/contracts/{year}/edit` - line 1159-1198)
**Cũ:**
```python
rows = read_contracts(excel_path=excel_path)
contract = None
for r in rows:
    if r.get("contract_no") == contract_no and not r.get("annex_no"):
        contract = r
        break
```

**Mới:**
```python
contract = get_contract_by_no(contract_no)
if not contract or contract.get("contract_year") != year:
    return RedirectResponse(url=f"/contracts?year={year}&error=Khong tim thay hop dong", status_code=303)
```

#### E. Contract Update (`/contracts/{year}/update` - line 1201-1274)
**Cũ:**
```python
success = update_contract_row(
    excel_path=excel_path,
    contract_no=contract_no,
    annex_no=None,
    updated_data=updated_data
)
```

**Mới:**
```python
contract = get_contract_by_no(contract_no)
if not contract:
    return RedirectResponse(url=f"/contracts?year={year}&error=Khong tim thay hop dong", status_code=303)

update_contract_record(contract["id"], updated_data, current_user)
```

#### F. Contract Delete (`/contracts/{year}/delete` - line 1277-1301)
**Cũ:**
```python
rows = read_contracts(excel_path=excel_path)
for r in rows:
    if r.get("contract_no") == contract_no and not r.get("annex_no"):
        docx_path = r.get("docx_path")
        ...
success = delete_contract_row(excel_path=excel_path, contract_no=contract_no, annex_no=None)
```

**Mới:**
```python
contract = get_contract_by_no(contract_no)
if not contract:
    return JSONResponse({"success": False, "error": "Không tìm thấy hợp đồng"}, status_code=404)

docx_path = contract.get("docx_path")
if docx_path and isinstance(docx_path, str):
    p = Path(docx_path)
    if p.exists():
        p.unlink()

success = delete_contract_record(contract["id"])
```

#### G. Annex Delete (`/annexes/{year}/delete` - line 1304-1336)
**Cũ:**
```python
rows = read_contracts(excel_path=excel_path)
for r in rows:
    if r.get("contract_no") == contract_no and r.get("annex_no") == annex_no:
        ...
success = delete_contract_row(excel_path=excel_path, contract_no=contract_no, annex_no=annex_no)
```

**Mới:**
```python
contract = get_contract_by_no(contract_no)
if not contract:
    return JSONResponse({"success": False, "error": "Không tìm thấy hợp đồng"}, status_code=404)

annexes = AnnexDB.get_by_contract(contract["id"])
annex = None
for a in annexes:
    if a.get("annex_no") == annex_no:
        annex = a
        break

if not annex:
    return JSONResponse({"success": False, "error": "Không tìm thấy phụ lục"}, status_code=404)

# Delete files
docx_path = annex.get("docx_path")
if docx_path:
    p = Path(docx_path)
    if p.exists():
        p.unlink()

catalogue_path = annex.get("catalogue_path")
if catalogue_path:
    p = Path(catalogue_path)
    if p.exists():
        p.unlink()

success = delete_annex_record(annex["id"])
```

#### H. Annex Creation (`/annexes` POST - line 1358-1634)
**Cũ (line 1392, 1623):**
```python
contracts = read_contracts(excel_path=STORAGE_EXCEL_DIR / f"contracts_{year}.xlsx")
...
append_contract_row(excel_path=contracts_excel_path, record=annex_record)
```

**Mới:**
```python
# Find contract
contract = get_contract_by_no(contract_no)
if not contract:
    return templates.TemplateResponse(..., error="Không tìm thấy hợp đồng")

contract_row = contract

# At the end, create annex
annex_data = {
    "contract_id": contract["id"],
    "annex_no": so_phu_luc,
    "ngay_ky_phu_luc": annex_date,
    "linh_vuc": linh_vuc_value,
    "don_vi_ten": don_vi_ten_value,
    "don_vi_dia_chi": don_vi_dia_chi_value,
    "don_vi_dien_thoai": don_vi_dien_thoai_value,
    "don_vi_nguoi_dai_dien": don_vi_nguoi_dai_dien_value,
    "don_vi_chuc_vu": don_vi_chuc_vu_value,
    "don_vi_mst": don_vi_mst_value,
    "don_vi_email": don_vi_email_value,
    "kenh_ten": kenh_ten_value,
    "kenh_id": channel_id_value,
    "so_tien_chua_GTGT_value": pre_vat_value if pre_vat_value else None,
    "so_tien_chua_GTGT_text": format_money_vnd(pre_vat_value) if pre_vat_value else None,
    "thue_percent": vat_percent_final,
    "thue_GTGT_value": vat_value if vat_value else None,
    "thue_GTGT_text": format_money_vnd(vat_value) if vat_value else None,
    "so_tien_value": total_value if total_value else None,
    "so_tien_text": format_money_vnd(total_value) if total_value else None,
    "so_tien_bang_chu": total_words if total_words else None,
    "docx_path": str(out_docx_path),
    "catalogue_path": str(out_catalogue_path),
}
create_annex_record(annex_data, current_user)
```

#### I. Document Form (`/documents/new` - line 1637-1682)
**Cũ (line 1650):**
```python
contracts = read_contracts(excel_path=STORAGE_EXCEL_DIR / f"contracts_{y}.xlsx")
contracts = [r for r in contracts if not r.get("annex_no")]
```

**Mới:**
```python
contracts, _ = get_contracts_by_year(y)
```

#### J. Annexes List (`/annexes` - line 993-1087)
**Cũ:**
```python
excel_path = STORAGE_EXCEL_DIR / f"contracts_{y}.xlsx"
rows = read_contracts(excel_path=excel_path)
annexes = [r for r in rows if r.get("annex_no")]
contracts = [r for r in rows if not r.get("annex_no")]
contracts_map = {r.get("contract_no"): r for r in contracts}
```

**Mới:**
```python
contracts, annexes = get_contracts_by_year(y)
contracts_map = {r.get("contract_no"): r for r in contracts}
```

### 3. Remove Excel Dependencies

Sau khi migrate xong tất cả endpoints:

1. Xóa file: `app/services/excel_store.py`
2. Xóa file: `storage/excel/contracts_2025.xlsx`
3. Xóa file: `storage/excel/works_contract_2025.xlsx`
4. Update `requirements.txt` - xóa `openpyxl` nếu không còn dùng cho `export_catalogue_excel`

### 4. Testing

Test tất cả endpoints sau khi migrate:
- ✅ Login/Authentication
- ✅ Contract List
- ✅ Contract Detail
- ✅ Contract Creation
- ✅ Contract Edit
- ✅ Contract Delete
- ✅ Annex List
- ✅ Annex Creation
- ✅ Annex Delete
- ✅ Works Import

## Important Notes

- `export_catalogue_excel()` vẫn giữ lại vì dùng để export template Excel (không phải lưu data)
- Tất cả date fields phải convert sang string ISO format trước khi lưu vào Supabase
- User authentication cần thiết cho tất cả operations (created_by, updated_by fields)
- Cascade delete đã được setup ở database level (contracts -> annexes -> works)
