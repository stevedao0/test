#!/bin/bash

echo "========================================"
echo "  Khởi động Server Quản lý Hợp đồng"
echo "========================================"
echo

echo "[1/3] Kiểm tra Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Chưa cài Python3!"
    exit 1
fi
echo "✓ Python đã cài đặt"

echo
echo "[2/3] Kiểm tra dependencies..."
pip3 show fastapi &> /dev/null
if [ $? -ne 0 ]; then
    echo "⚠ Đang cài đặt dependencies..."
    pip3 install -r requirements.txt
fi
echo "✓ Dependencies OK"

echo
echo "[3/3] Kiểm tra firewall..."
if command -v ufw &> /dev/null; then
    if sudo ufw status | grep -q "8000.*ALLOW" &> /dev/null; then
        echo "✓ Port 8000 đã được mở"
    else
        echo "⚠ Mở port 8000 trên UFW..."
        sudo ufw allow 8000/tcp
    fi
elif command -v firewall-cmd &> /dev/null; then
    echo "⚠ Mở port 8000 trên firewalld..."
    sudo firewall-cmd --permanent --add-port=8000/tcp
    sudo firewall-cmd --reload
else
    echo "✓ Không phát hiện firewall hoặc đã mở"
fi

echo
echo "========================================"
echo "  Server đang khởi động..."
echo "========================================"
echo

IP=$(hostname -I | awk '{print $1}')
echo "📍 Truy cập từ máy này:     http://localhost:8000"
echo "📍 Truy cập từ máy khác:    http://$IP:8000"
echo
echo "⚠  Để dừng server: Nhấn Ctrl+C"
echo "========================================"
echo

python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
