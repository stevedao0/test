# Tính năng mới - Contract Management System

## 📋 Tổng quan

Hệ thống đã được nâng cấp với các tính năng mới:
- ✅ Tooltips on hover
- ✅ Auto-backup system
- ✅ Error handling
- ✅ Logging system
- ✅ Code refactoring (giảm 97% dòng code trong main.py)

---

## 🎯 1. Tooltips (Gợi ý khi hover)

### Cách sử dụng
Thêm attribute `data-tooltip` vào bất kỳ element nào:

```html
<button data-tooltip="Xóa hợp đồng" class="btn btn-danger">
  Xóa
</button>

<span data-tooltip="Số hợp đồng" data-tooltip-pos="top">
  Contract No.
</span>
```

### Vị trí tooltips
- `data-tooltip-pos="top"` - Hiện ở trên
- `data-tooltip-pos="bottom"` - Hiện ở dưới (mặc định)
- `data-tooltip-pos="left"` - Hiện bên trái
- `data-tooltip-pos="right"` - Hiện bên phải

### Tooltip nhiều dòng
Thêm class `tooltip-multiline`:
```html
<button class="tooltip-multiline" data-tooltip="Đây là tooltip dài
có thể xuống dòng">
  Hover me
</button>
```

---

## 💾 2. Auto-Backup System

### Tự động backup
Hệ thống **TỰ ĐỘNG** tạo backup mỗi khi:
- Tạo hợp đồng mới
- Cập nhật hợp đồng
- Xóa hợp đồng
- Import danh sách tác phẩm

### Vị trí backup
```
storage/backups/
├── contracts_2025_20241226_143020.xlsx
├── contracts_2025_20241226_143145.xlsx
└── works_contract_2025_20241226_144030.xlsx
```

### Định dạng tên file backup
```
<filename>_YYYYMMDD_HHMMSS<extension>
```
Ví dụ: `contracts_2025_20241226_143020.xlsx`

### Sử dụng BackupManager
```python
from app.services.backup import BackupManager
from pathlib import Path

# Khởi tạo
backup_mgr = BackupManager(storage_dir=Path("storage/excel"))

# Tạo backup thủ công
backup_path = backup_mgr.create_backup(Path("storage/excel/contracts_2025.xlsx"))

# Tạo backup an toàn (không báo lỗi nếu file không tồn tại)
backup_path = backup_mgr.create_auto_backup(Path("storage/excel/contracts_2025.xlsx"))

# Liệt kê backups
backups = backup_mgr.list_backups(pattern="contracts_*.xlsx")

# Restore backup
backup_mgr.restore_backup(
    backup_path=Path("storage/backups/contracts_2025_20241226_143020.xlsx"),
    target_path=Path("storage/excel/contracts_2025.xlsx")
)

# Xóa backup cũ (giữ lại 10 file mới nhất)
removed = backup_mgr.cleanup_old_backups(keep_count=10, pattern="*.xlsx")
print(f"Đã xóa {removed} backup cũ")
```

---

## 🛡️ 3. Error Handling

### ErrorHandler class
```python
from app.utils.error_handler import ErrorHandler, create_error_response

# Xử lý lỗi trong route
try:
    # Code có thể gây lỗi
    result = risky_operation()
except Exception as e:
    return ErrorHandler.handle_route_error(
        e,
        redirect_url="/contracts",
        error_message="Không thể thực hiện thao tác"
    )

# Xử lý lỗi cho API
try:
    data = api_operation()
except Exception as e:
    return ErrorHandler.handle_api_error(e, status_code=400)

# Safe execute (không crash nếu có lỗi)
result = ErrorHandler.safe_execute(
    func=lambda: dangerous_operation(),
    on_error=lambda e: print(f"Error: {e}"),
    default_return=None
)
```

### Tự động format validation errors
```python
from app.utils.error_handler import format_validation_error

try:
    validate_data(data)
except Exception as e:
    friendly_msg = format_validation_error(e)
    # Hiện message thân thiện cho user
```

---

## 📝 4. Logging System

### Logger tự động ghi log vào file
```
logs/
├── app_20241226.log
├── app_20241227.log
└── app_20241228.log
```

### Sử dụng logger
```python
from app.utils.logger import logger

# Log thông tin
logger.info("Thao tác thành công", user="admin", action="create_contract")

# Log cảnh báo
logger.warning("Dung lượng disk thấp", available_gb=2.5)

# Log lỗi
logger.error("Không thể kết nối database", host="localhost", port=5432)

# Log debug
logger.debug("Processing data", records=150, duration_ms=234)
```

### Log chuyên biệt cho contracts
```python
# Log tạo hợp đồng
logger.log_contract_created(contract_no="0001/2025/HĐQTGAN-PN/MR", user="admin")

# Log cập nhật hợp đồng
logger.log_contract_updated(contract_no="0001/2025/HĐQTGAN-PN/MR", user="admin")

# Log xóa hợp đồng
logger.log_contract_deleted(contract_no="0001/2025/HĐQTGAN-PN/MR", user="admin")

# Log tạo phụ lục
logger.log_annex_created(
    contract_no="0001/2025/HĐQTGAN-PN/MR",
    annex_no="01",
    user="admin"
)

# Log import tác phẩm
logger.log_works_imported(
    contract_no="0001/2025/HĐQTGAN-PN/MR",
    count=50,
    user="admin"
)

# Log backup
logger.log_backup_created(file_path="storage/backups/contracts_2025_20241226.xlsx")

# Log lỗi với context
try:
    risky_operation()
except Exception as e:
    logger.log_error_occurred(e, context="Creating contract")
```

### Format log
```
2024-12-26 14:30:20 - contract_management - INFO - Contract created - contract_no=0001/2025/HĐQTGAN-PN/MR | user=admin
2024-12-26 14:30:25 - contract_management - INFO - Backup created - file=storage/backups/contracts_2025_20241226_143020.xlsx
2024-12-26 14:30:30 - contract_management - WARNING - Contract deleted - contract_no=0001/2025/HĐQTGAN-PN/MR | user=admin
2024-12-26 14:30:35 - contract_management - ERROR - Creating contract - ValueError: Invalid contract number
```

---

## 🏗️ 5. Code Structure (Refactored)

### Cấu trúc mới
```
app/
├── main.py                    (52 dòng - chỉ setup app)
├── routers/
│   ├── contracts.py          (485 dòng - CRUD contracts)
│   ├── annexes.py            (375 dòng - CRUD annexes)
│   ├── works.py              (298 dòng - Import works)
│   ├── documents.py          (137 dòng - Document generation)
│   └── downloads.py          (114 dòng - File downloads)
├── services/
│   ├── backup.py             (NEW - Backup management)
│   ├── excel_store.py        (Updated - With auto-backup)
│   └── docx_renderer.py
└── utils/
    ├── formatters.py         (280 dòng - Helper functions)
    ├── error_handler.py      (NEW - Error handling)
    └── logger.py             (NEW - Logging system)
```

### Lợi ích
- ✅ Dễ tìm code gấp 10 lần
- ✅ Mỗi file < 500 dòng
- ✅ Tách biệt rõ ràng theo chức năng
- ✅ Dễ test từng module
- ✅ Dễ thêm features mới

---

## 🚀 Sử dụng

### 1. Cài đặt dependencies mới
```bash
pip install -r requirements.txt
```

### 2. Khởi động server
```bash
./start_server.sh
```

### 3. Kiểm tra logs
```bash
tail -f logs/app_$(date +%Y%m%d).log
```

### 4. Xem backups
```bash
ls -lh storage/backups/
```

---

## 📊 Thống kê

### Before refactoring
- **main.py**: 1791 dòng
- **Modules**: 1 file khổng lồ

### After refactoring
- **main.py**: 52 dòng (giảm 97%)
- **Modules**: 8 files có tổ chức
- **Tổng dòng code**: 1854 dòng (gần bằng, nhưng dễ quản lý hơn nhiều)

### New features
- ✅ Tooltips CSS + HTML attributes
- ✅ Auto-backup trước mỗi thao tác quan trọng
- ✅ Error handling với friendly messages
- ✅ Logging system với daily rotation
- ✅ Modular architecture

---

## ⚙️ Configuration

### Backup settings
Trong `app/services/backup.py`:
```python
# Thay đổi số lượng backup giữ lại
backup_mgr.cleanup_old_backups(keep_count=20)  # Mặc định: 10
```

### Log settings
Trong `app/utils/logger.py`:
```python
# Thay đổi log level
self._logger.setLevel(logging.DEBUG)  # Mặc định: INFO

# Chỉ log vào file (không console)
self._logger.removeHandler(console_handler)
```

---

## 🔧 Troubleshooting

### Lỗi "Module not found"
```bash
pip install -r requirements.txt
```

### Backup không tự động
Kiểm tra quyền ghi vào thư mục:
```bash
chmod -R 755 storage/backups/
```

### Logs không ghi
Kiểm tra thư mục logs:
```bash
mkdir -p logs
chmod -R 755 logs/
```

---

## 📚 API Reference

### BackupManager
- `create_backup(file_path)` - Tạo backup
- `create_auto_backup(file_path)` - Tạo backup an toàn
- `list_backups(pattern)` - Liệt kê backups
- `restore_backup(backup_path, target_path)` - Restore
- `cleanup_old_backups(keep_count, pattern)` - Dọn dẹp

### Logger
- `info(message, **kwargs)` - Log thông tin
- `warning(message, **kwargs)` - Log cảnh báo
- `error(message, **kwargs)` - Log lỗi
- `debug(message, **kwargs)` - Log debug
- Các method chuyên biệt: `log_contract_created`, `log_contract_updated`, etc.

### ErrorHandler
- `handle_route_error(error, redirect_url, error_message)` - Xử lý lỗi route
- `handle_api_error(error, status_code)` - Xử lý lỗi API
- `safe_execute(func, on_error, default_return)` - Thực thi an toàn

---

## 🎉 Kết luận

Hệ thống đã được nâng cấp toàn diện với:
- **UX tốt hơn** (tooltips)
- **An toàn hơn** (auto-backup)
- **Dễ debug hơn** (logging)
- **Bảo trì dễ hơn** (refactored code)
- **Xử lý lỗi tốt hơn** (error handling)

Tất cả các tính năng **hoạt động tự động**, không cần cấu hình thêm!
