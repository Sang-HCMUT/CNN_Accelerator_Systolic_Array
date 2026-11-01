@echo off
echo ====================================================================
echo   HARDWARE-IN-THE-LOOP (HIL) TEST RUNNER - DE2 BOARD
echo ====================================================================
echo.

cd /d "%~dp0"

echo [1/2] Checking Python environment...
python --version
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in PATH!
    pause
    exit /b 1
)

echo.
echo [2/2] Running automated HIL verification suite over UART...
echo Note: If your adapter is on a specific COM port, pass it as:
echo       run_hil_test.bat COM3
echo.

if "%1"=="" (
    python ..\software_ref\hil_test_board.py --output hardware_test_log.txt
) else (
    python ..\software_ref\hil_test_board.py --port %1 --output hardware_test_log.txt
)

echo.
pause
