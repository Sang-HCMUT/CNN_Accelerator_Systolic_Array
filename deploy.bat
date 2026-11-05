@echo off
chcp 65001 > nul
echo ===============================================================================
echo [DEPLOY] TRIỂN KHAI NỀN TẢNG METIS ARCHITECTURE PLATFORM LÊN GITHUB & CLOUD
echo ===============================================================================

echo 1. Đang kiểm tra trạng thái Git...
git status -s

echo.
echo 2. Đang thêm các file nền tảng chính...
git add index.html figures/ .github/workflows/deploy_pages.yml vercel.json netlify.toml tools/ build_metis_unified_platform.py

echo.
echo 3. Đang tạo Commit...
git commit -m "Deploy: Unified Metis Architecture Suite (Report 50%%, CNN Studio, 18 GIFs, Skew Sim)"

echo.
echo 4. Đang đẩy lên remote repository (GitHub)...
git push origin feature/gen2-phase2-opt

echo.
echo ===============================================================================
echo [HOÀN TẤT] Nếu bạn đã kích hoạt GitHub Pages trong Settings -> Pages (Source: GitHub Actions),
echo trang web sẽ tự động online tại:
echo https://Sang-HCMUT.github.io/CNN_Accelerator_Systolic_Array/
echo ===============================================================================
pause
