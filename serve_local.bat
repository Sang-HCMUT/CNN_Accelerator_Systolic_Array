@echo off
chcp 65001 > nul
echo ===============================================================================
echo [SERVER] KHỞI CHẠY MÁY CHỦ WEB NỘI BỘ (LOCAL HTTP SERVER)
echo Đang mở nền tảng Metis Architecture Suite tại: http://localhost:8080/
echo ===============================================================================

start http://localhost:8080/index.html
python -m http.server 8080
pause
