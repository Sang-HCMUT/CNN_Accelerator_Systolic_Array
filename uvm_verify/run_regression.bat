@echo off
echo ========================================================
echo   RUNNING UVM MULTI-SEED REGRESSION FOR GEMM ACCELERATOR
echo ========================================================

cd /d "%~dp0"
python run_regression.py %*
if %errorlevel% neq 0 (
    echo [ERROR] Regression failed!
    exit /b %errorlevel%
)
