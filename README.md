# Hệ thống Quản lý Hợp đồng

Phần mềm quản lý và tạo hợp đồng tự động từ template Word.

## 🚀 Khởi động nhanh

### Windows
```cmd
Double-click: start_server.bat
```
**HOẶC** nếu cần truy cập từ máy khác:
```cmd
Click phải → "Run as Administrator"
```

### Linux/Mac
```bash
chmod +x start_server.sh
./start_server.sh
```

Sau đó mở trình duyệt và truy cập: **http://localhost:8000**

### Tính năng tự động
Script `start_server.bat` tự động:
- ✅ Kiểm tra Python & dependencies
- ✅ Tự động cài đặt packages nếu thiếu
- ✅ Mở port 8000 trên Windows Firewall
- ✅ Phát hiện và hiển thị IP để truy cập từ xa
- ✅ Xử lý port bị chiếm (tự kill hoặc đổi port)
- ✅ Giao diện màu sắc dễ theo dõi

## 📋 Yêu cầu hệ thống

- Python 3.8 trở lên
- Hệ điều hành: Windows 10+, Linux, macOS
- RAM: 2GB trở lên
- Dung lượng: 500MB trống

## 📦 Cài đặt Dependencies

**Không cần cài thủ công!** Script `start_server.bat` tự động cài đặt.

Hoặc cài thủ công:
```bash
pip install -r requirements.txt
```

## 🌐 Truy cập từ máy khác (LAN)

### Cách 1: Run as Administrator
```cmd
Click phải start_server.bat → "Run as Administrator"
```

### Cách 2: Mở port thủ công
```cmd
# Windows Firewall
netsh advfirewall firewall add rule name="Port 8000" dir=in action=allow protocol=TCP localport=8000

# Linux
sudo ufw allow 8000/tcp
```

### Truy cập từ máy khác
```
http://[IP-MÁY-CHÍNH]:8000
```
(IP sẽ được hiển thị khi chạy start_server.bat)

## 📁 Cấu trúc Project

```
project/
├── app/
│   ├── main.py              # Entry point
│   ├── models.py            # Data models
│   ├── documents/           # Document logic
│   ├── services/            # Business services
│   ├── static/              # CSS, JS, icons
│   └── web_templates/       # HTML templates
├── templates/               # Word templates
├── storage/
│   ├── excel/              # Excel database
│   └── docx/               # Generated contracts
├── scripts/                # Utility scripts
├── start_server.bat        # All-in-one startup (Windows)
└── start_server.sh         # Linux/Mac startup
```

## 📚 Tính năng

- ✅ Quản lý hợp đồng và phụ lục
- ✅ Tạo tài liệu Word tự động từ template
- ✅ Lưu trữ dữ liệu trong Excel
- ✅ Giao diện web hiện đại, responsive
- ✅ Tìm kiếm và lọc dữ liệu
- ✅ Xuất file Word có thể chỉnh sửa
- ✅ Hỗ trợ nhiều người dùng qua mạng LAN

## 🛠️ Development

### Chạy ở chế độ development (auto-reload)
```bash
python -m uvicorn app.main:app --reload
```

### Chạy ở production mode
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🐛 Xử lý lỗi thường gặp

### Port 8000 đã được sử dụng
```bash
# Windows: Tìm process đang chiếm port
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux: Kill process
lsof -ti:8000 | xargs kill -9
```

### Không truy cập được từ máy khác
1. Run as Administrator để mở port tự động
2. Hoặc mở port thủ công (xem phần "Truy cập từ máy khác")
3. Kiểm tra cùng mạng WiFi/LAN
4. Ping thử IP của server

### Module not found
```bash
pip install -r requirements.txt
```

## 📞 Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra log trong cửa sổ terminal
2. Xem phần "Xử lý lỗi thường gặp" ở trên
3. Script `start_server.bat` có hướng dẫn chi tiết khi gặp lỗi

## 📄 License

Internal use only.
