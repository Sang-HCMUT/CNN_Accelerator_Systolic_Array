@echo off
chcp 65001 > nul
echo ===============================================================================
echo [METIS-SUITE] PHÒNG TRỰC QUAN HÓA SUY LUẬN CNN VÀ BỘ TĂNG TỐC 64 PE
echo Đang mở Trực Tiếp Tab CNN Studio trong Cổng Hợp Nhất index.html
echo ===============================================================================

set "TARGET_HTML=%~dp0index.html#cnn-studio"

start "" "%TARGET_HTML%"
exit /b 0
