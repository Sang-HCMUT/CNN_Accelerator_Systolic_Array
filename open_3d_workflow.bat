@echo off
chcp 65001 > nul
echo ===============================================================================
echo [3D-WORKFLOW] MÔ HÌNH RENDER 3D ĐỘC LẬP - KIẾN TRÚC VI MẠCH TĂNG TỐC CNN SOC
echo Khởi chạy Mô hình không gian 3D tương tác toàn diện (Three.js WebGL Engine)
echo Bao gồm 7 công đoạn: Input/Im2Col - SRAM Buffers - Skew Unit - 64-PE Mesh - Drain - ReLU - SoC
echo ===============================================================================

set "TARGET_HTML=%~dp0figures\hardware_3d_workflow.html"

if not exist "%TARGET_HTML%" (
    echo [LỖI] Không tìm thấy file: %TARGET_HTML%
    pause
    exit /b 1
)

echo Đang mở mô hình 3D trên trình duyệt mặc định:
echo %TARGET_HTML%
start "" "%TARGET_HTML%"

exit /b 0
