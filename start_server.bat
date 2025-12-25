@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ============================================================
::  SERVER QUẢN LÝ HỢP ĐỒNG - ALL-IN-ONE STARTUP SCRIPT
:: ============================================================

color 0A
title Server Quản Lý Hợp Đồng - Đang Khởi Động...

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║   SERVER QUẢN LÝ HỢP ĐỒNG - KHỞI ĐỘNG TỰ ĐỘNG        ║
echo ╚════════════════════════════════════════════════════════╝
echo.

:: ============================================================
:: BƯỚC 1: KIỂM TRA PYTHON
:: ============================================================
echo [1/5] Đang kiểm tra Python...

python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo.
    echo ❌ LỖI: Chưa cài đặt Python!
    echo.
    echo 📥 Vui lòng cài Python 3.8+ từ:
    echo    https://www.python.org/downloads/
    echo.
    echo ⚠  Nhớ tích chọn "Add Python to PATH" khi cài!
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYTHON_VER=%%v
echo    ✓ Python %PYTHON_VER% - OK
echo.

:: ============================================================
:: BƯỚC 2: KIỂM TRA VÀ CÀI ĐẶT DEPENDENCIES
:: ============================================================
echo [2/5] Đang kiểm tra dependencies...

pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo    ⚠  Dependencies chưa đầy đủ
    echo    📦 Đang cài đặt từ requirements.txt...
    echo.
    pip install -q -r requirements.txt
    if errorlevel 1 (
        color 0C
        echo.
        echo ❌ Không thể cài dependencies!
        echo    Chạy thủ công: pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
    echo    ✓ Đã cài đặt xong dependencies
) else (
    echo    ✓ Dependencies đã có sẵn
)
echo.

:: ============================================================
:: BƯỚC 3: LẤY THÔNG TIN IP
:: ============================================================
echo [3/5] Đang lấy thông tin mạng...

set "LOCAL_IP="
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set "LOCAL_IP=%%a"
    set "LOCAL_IP=!LOCAL_IP:~1!"
    goto :ip_found
)
:ip_found

if "%LOCAL_IP%"=="" (
    set "LOCAL_IP=127.0.0.1"
    echo    ⚠  Không tìm thấy IP mạng, dùng localhost
) else (
    echo    ✓ IP của máy này: %LOCAL_IP%
)
echo.

:: ============================================================
:: BƯỚC 4: MỞ PORT TRÊN FIREWALL
:: ============================================================
echo [4/5] Đang cấu hình Windows Firewall...

:: Kiểm tra xem đã có rule chưa
netsh advfirewall firewall show rule name="Contract Manager Port 8000" >nul 2>&1
if errorlevel 1 (
    echo    ⚠  Port 8000 chưa được mở
    echo    🔓 Đang thử mở port tự động...
    echo.

    :: Thử mở port (có thể cần quyền admin)
    netsh advfirewall firewall add rule name="Contract Manager Port 8000" dir=in action=allow protocol=TCP localport=8000 >nul 2>&1

    if errorlevel 1 (
        color 0E
        echo    ⚠  KHÔNG THỂ TỰ ĐỘNG MỞ PORT ^(thiếu quyền Admin^)
        echo.
        echo    ══════════════════════════════════════════════════
        echo     CÁC CÁCH MỞ PORT:
        echo    ══════════════════════════════════════════════════
        echo.
        echo     CÁCH 1: Click phải file này ^→ "Run as Administrator"
        echo.
        echo     CÁCH 2: Mở Windows Defender Firewall:
        echo       • Tìm "Windows Defender Firewall" trong Start
        echo       • Advanced Settings ^→ Inbound Rules
        echo       • New Rule ^→ Port ^→ TCP ^→ Port 8000 ^→ Allow
        echo.
        echo     CÁCH 3: Tắt Firewall tạm thời ^(không khuyến khích^):
        echo       • Settings ^→ Windows Security ^→ Firewall
        echo       • Turn off cho Private network
        echo.
        echo    ══════════════════════════════════════════════════
        echo.
        echo    ℹ  Server vẫn sẽ chạy, nhưng chỉ truy cập được
        echo       từ máy này ^(localhost^). Muốn truy cập từ máy
        echo       khác thì phải mở port theo 1 trong 3 cách trên.
        echo.
        timeout /t 5 >nul
    ) else (
        echo    ✓ Đã mở port 8000 thành công!
    )
) else (
    echo    ✓ Port 8000 đã được mở từ trước
)
echo.

:: ============================================================
:: BƯỚC 5: KIỂM TRA PORT CÓ BỊ CHIẾM KHÔNG
:: ============================================================
echo [5/5] Đang kiểm tra port 8000...

netstat -ano | findstr :8000 | findstr LISTENING >nul 2>&1
if not errorlevel 1 (
    color 0E
    echo.
    echo ⚠  WARNING: Port 8000 đã được sử dụng bởi process khác!
    echo.
    echo Các process đang dùng port 8000:
    for /f "tokens=5" %%p in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
        echo    • PID: %%p
        for /f "tokens=1" %%n in ('tasklist /FI "PID eq %%p" /NH 2^>nul') do echo      Process: %%n
    )
    echo.
    echo Bạn muốn:
    echo   1. Dừng process đang chiếm port và tiếp tục
    echo   2. Đổi sang port khác ^(8080^)
    echo   3. Thoát
    echo.
    set /p "choice=Chọn (1/2/3): "

    if "!choice!"=="1" (
        for /f "tokens=5" %%p in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
            echo Đang dừng PID %%p...
            taskkill /PID %%p /F >nul 2>&1
        )
        timeout /t 2 >nul
    ) else if "!choice!"=="2" (
        set "SERVER_PORT=8080"
        echo Sẽ chạy trên port 8080
        timeout /t 2 >nul
    ) else (
        echo Đã hủy.
        pause
        exit /b 0
    )
) else (
    echo    ✓ Port 8000 sẵn sàng
)

if not defined SERVER_PORT set "SERVER_PORT=8000"
echo.

:: ============================================================
:: HIỂN THỊ THÔNG TIN KẾT NỐI
:: ============================================================
color 0B
cls
echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║          SERVER ĐANG KHỞI ĐỘNG THÀNH CÔNG            ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo ┌────────────────────────────────────────────────────────┐
echo │  THÔNG TIN KẾT NỐI:                                   │
echo ├────────────────────────────────────────────────────────┤
echo │                                                        │
echo │  🖥️  Từ MÁY NÀY truy cập:                             │
echo │      http://localhost:%SERVER_PORT%                              │
echo │                                                        │
echo │  🌐 Từ MÁY KHÁC trong mạng LAN:                       │
echo │      http://%LOCAL_IP%:%SERVER_PORT%                        │
echo │                                                        │
echo │  📱 Từ ĐIỆN THOẠI ^(cùng WiFi^):                       │
echo │      http://%LOCAL_IP%:%SERVER_PORT%                        │
echo │                                                        │
echo └────────────────────────────────────────────────────────┘
echo.
echo ┌────────────────────────────────────────────────────────┐
echo │  ⚠️  QUAN TRỌNG:                                       │
echo ├────────────────────────────────────────────────────────┤
echo │  • KHÔNG ĐÓNG cửa sổ này khi đang dùng               │
echo │  • Để dừng server: Nhấn Ctrl+C                        │
echo │  • Xem log bên dưới để theo dõi hoạt động            │
echo └────────────────────────────────────────────────────────┘
echo.
echo ════════════════════════════════════════════════════════
echo                    LOG HOẠT ĐỘNG
echo ════════════════════════════════════════════════════════
echo.

:: ============================================================
:: KHỞI ĐỘNG SERVER
:: ============================================================
title Server Quản Lý Hợp Đồng - Port %SERVER_PORT% - IP: %LOCAL_IP%

python -m uvicorn app.main:app --host 0.0.0.0 --port %SERVER_PORT% --reload

:: ============================================================
:: XỬ LÝ KHI SERVER DỪNG
:: ============================================================
echo.
echo.
color 0E
echo ════════════════════════════════════════════════════════
echo   SERVER ĐÃ DỪNG
echo ════════════════════════════════════════════════════════
echo.
echo Nhấn phím bất kỳ để đóng cửa sổ...
pause >nul
