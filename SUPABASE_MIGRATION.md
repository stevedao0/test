# Supabase Migration - Summary

## ✅ ĐÃ HOÀN THÀNH

### 1. Database Schema
- ✅ Tables đã tạo trong Supabase:
  - `profiles` - User profiles
  - `contracts` - Main contracts
  - `annexes` - Contract annexes
  - `works` - Musical works/items
  - `audit_logs` - Change tracking
- ✅ Row Level Security (RLS) policies đã setup
- ✅ Triggers cho audit logging
- ✅ Foreign key relationships và cascading deletes

### 2. Service Layer
- ✅ `app/services/database.py` - Database operations với Supabase
  - `ContractDB` - Contract CRUD operations
  - `AnnexDB` - Annex CRUD operations
  - `WorksDB` - Works batch operations
  - `AuditLogDB` - Audit log queries

- ✅ `app/services/contract_helpers.py` - Helper functions
  - `get_contracts_by_year()` - Lấy contracts và annexes theo năm
  - `create_contract_record()` - Tạo contract mới
  - `create_annex_record()` - Tạo annex mới
  - `update_contract_record()` - Update contract
  - `delete_contract_record()` - Xóa contract
  - `save_works_batch()` - Lưu nhiều works

### 3. Migration Script
- ✅ `migrate_excel_to_supabase.py` - Script migrate data từ Excel
  - Migrate contracts từ `storage/excel/contracts_2025.xlsx`
  - Migrate annexes từ `storage/excel/contracts_2025.xlsx`
  - Migrate works từ `storage/excel/works_contract_2025.xlsx`

### 4. Code Migration (Partial)
- ✅ Imports updated trong `main.py`
- ✅ `/api/contracts` GET endpoint
- ✅ `/contracts` GET list endpoint

## 🔄 CẦN HOÀN THÀNH

### 1. Chạy Migration Script

```bash
# Setup virtual environment (nếu chưa có)
python3 -m venv venv
source venv/bin/activate  # hoặc `venv\Scripts\activate` trên Windows

# Install dependencies
pip install -r requirements.txt

# Chạy migration
python migrate_excel_to_supabase.py
```

**Lưu ý:** Script sẽ import data từ Excel vào Supabase. Chỉ chạy 1 lần!

### 2. Migrate Remaining Endpoints

Xem chi tiết trong `MIGRATION_GUIDE.md`. Cần migrate các endpoints:

- [ ] `/works/import` POST - Import works from Excel
- [ ] `/contracts` POST - Create new contract
- [ ] `/contracts/{year}/detail` GET - Contract detail
- [ ] `/contracts/{year}/edit` GET - Edit form
- [ ] `/contracts/{year}/update` POST - Update contract
- [ ] `/contracts/{year}/delete` POST - Delete contract
- [ ] `/annexes` GET - Annexes list
- [ ] `/annexes/new` GET - Annex form
- [ ] `/annexes` POST - Create annex
- [ ] `/annexes/{year}/delete` POST - Delete annex
- [ ] `/documents/new` GET - Document form

### 3. Testing

Sau khi migrate xong code, test tất cả chức năng:

```bash
# Chạy server
python -m uvicorn app.main:app --reload

# Test các endpoints:
# - Login: http://localhost:8000/auth/login
# - Contracts: http://localhost:8000/contracts
# - Create Contract: http://localhost:8000/documents/new?doc_type=contract
# - Create Annex: http://localhost:8000/documents/new?doc_type=annex
# - Import Works: http://localhost:8000/works/import
```

### 4. Cleanup

Sau khi test thành công:

1. **Xóa Excel files (backup trước):**
   ```bash
   mkdir -p storage/excel_backup
   mv storage/excel/*.xlsx storage/excel_backup/
   ```

2. **Xóa excel_store.py:**
   ```bash
   rm app/services/excel_store.py
   ```

3. **Update imports trong code** (xóa references đến excel_store)

4. **(Optional) Xóa openpyxl từ requirements.txt** nếu chỉ dùng cho export_catalogue_excel

## 📋 Migration Checklist

```
[✅] 1. Database schema created in Supabase
[✅] 2. Service layer implemented (database.py, contract_helpers.py)
[✅] 3. Migration script created (migrate_excel_to_supabase.py)
[✅] 4. Partial code migration done (2/12 endpoints)
[✅] 5. Migration guide created (MIGRATION_GUIDE.md)
[⏳] 6. Run migration script to import Excel data
[⏳] 7. Complete remaining endpoint migrations (10/12 remaining)
[⏳] 8. Test all functionality
[⏳] 9. Backup and remove Excel files
[⏳] 10. Remove excel_store.py
```

## 🚀 Quick Start (Tiếp tục migration)

```bash
# 1. Chạy migration script
python migrate_excel_to_supabase.py

# 2. Xem hướng dẫn chi tiết
cat MIGRATION_GUIDE.md

# 3. Migrate từng endpoint theo guide
# (Copy/paste code từ MIGRATION_GUIDE.md)

# 4. Test từng endpoint sau khi migrate
python -m uvicorn app.main:app --reload

# 5. Khi tất cả hoạt động tốt:
rm app/services/excel_store.py
mkdir -p storage/excel_backup
mv storage/excel/*.xlsx storage/excel_backup/
```

## ⚠️ Important Notes

1. **Backup data trước khi chạy migration:**
   ```bash
   cp -r storage/excel storage/excel_backup_$(date +%Y%m%d)
   ```

2. **Migration script chỉ chạy 1 lần** - nó không check duplicates (có thể thêm logic check nếu cần)

3. **RLS policies đã được setup** - tất cả operations yêu cầu authentication

4. **Audit logging tự động** - mọi thay đổi được log vào `audit_logs` table

5. **Cascade delete enabled** - xóa contract sẽ tự động xóa annexes và works

## 📞 Support

Nếu gặp lỗi trong quá trình migration:

1. Check database connection trong `.env`:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ```

2. Check RLS policies trong Supabase dashboard

3. Check audit logs trong Supabase để debug issues:
   ```sql
   SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT 50;
   ```

4. Xem logs của application:
   ```bash
   python -m uvicorn app.main:app --reload --log-level debug
   ```
