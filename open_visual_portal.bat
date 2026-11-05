@echo off
chcp 65001 > nul
echo ===============================================================================
echo [METIS-SUITE] CỔNG KIẾN TRÚC VI MẠCH TĂNG TỐC TÂM THU CNN SOC (CYCLONE V)
echo Đang mở Trực Tiếp Cổng Hợp Nhất Độc Nhất (Unified Flagship Platform): index.html
echo Bao gồm: Báo Cáo 50%%, Live CNN Studio, Thư Viện 18 GIFs, Skew Simulator, STA
echo ===============================================================================

set "TARGET_HTML=%~dp0index.html"

if not exist "%TARGET_HTML%" (
    echo [LỖI] Không tìm thấy file: %TARGET_HTML%
    pause
    exit /b 1
)

start "" "%TARGET_HTML%"
exit /b 0
