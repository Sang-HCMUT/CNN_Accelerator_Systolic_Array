@echo off
echo ========================================================
echo   COMPILING 8x8 SYSTOLIC ACCELERATOR ON CYCLONE II
echo ========================================================

cd /d "%~dp0"

echo [1/3] Running Quartus Analysis ^& Synthesis (quartus_map)...
C:\13.0sp1\quartus\bin64\quartus_map.exe systolic_accelerator_8x8
if %errorlevel% neq 0 (
    echo [ERROR] Synthesis failed!
    pause
    exit /b %errorlevel%
)

echo [2/3] Running Quartus Fitter Place ^& Route (quartus_fit)...
C:\13.0sp1\quartus\bin64\quartus_fit.exe systolic_accelerator_8x8
if %errorlevel% neq 0 (
    echo [ERROR] Fitting failed!
    pause
    exit /b %errorlevel%
)

echo [3/3] Running TimeQuest Timing Analyzer (quartus_sta)...
C:\13.0sp1\quartus\bin64\quartus_sta.exe systolic_accelerator_8x8
if %errorlevel% neq 0 (
    echo [ERROR] STA failed!
    pause
    exit /b %errorlevel%
)

echo ========================================================
echo   COMPILATION COMPLETED SUCCESSFULLY!
echo ========================================================
pause
