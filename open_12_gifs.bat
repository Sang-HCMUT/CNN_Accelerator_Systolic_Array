@echo off
chcp 65001 > nul
echo ===============================================================================
echo [METIS-SUITE] THƯ VIỆN 18 MÔ PHỎNG ĐỘNG KIẾN TRÚC VI MẠCH TÂM THU
echo Đang mở Trực Tiếp Tab Thư Viện 18 GIFs trong Cổng Hợp Nhất index.html
echo ===============================================================================

set "TARGET_HTML=%~dp0index.html#gif-library"

start "" "%TARGET_HTML%"
exit /b 0
