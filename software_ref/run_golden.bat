@echo off
echo ========================================================
echo   GENERATING GEMM GOLDEN REFERENCE VECTORS
echo ========================================================

cd /d "%~dp0\.."

set "PYTHON_EXE=C:\Users\hoang\AppData\Local\Programs\Python\Python313\python.exe"

if exist "%PYTHON_EXE%" (
    "%PYTHON_EXE%" software_ref\gemm_golden.py
) else (
    python software_ref\gemm_golden.py
)

echo ========================================================
pause
