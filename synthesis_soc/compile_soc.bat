@echo off
echo ========================================================
echo   COMPILING RISC-V SoC TOP ON CYCLONE II (EP2C20F484C7)
echo ========================================================

cd /d "%~dp0"

echo [1/3] Running Quartus Analysis & Synthesis (quartus_map)...
C:\13.0sp1\quartus\bin64\quartus_map.exe soc_top
if %errorlevel% neq 0 (
    echo [ERROR] Synthesis failed!
    exit /b %errorlevel%
)

echo [2/3] Running Quartus Fitter Place & Route (quartus_fit)...
C:\13.0sp1\quartus\bin64\quartus_fit.exe soc_top
if %errorlevel% neq 0 (
    echo [ERROR] Fitting failed!
    exit /b %errorlevel%
)

echo [3/3] Running TimeQuest Timing Analyzer (quartus_sta)...
C:\13.0sp1\quartus\bin64\quartus_sta.exe soc_top
if %errorlevel% neq 0 (
    echo [ERROR] STA failed!
    exit /b %errorlevel%
)

echo ========================================================
echo   COMPILATION COMPLETED SUCCESSFULLY!
echo ========================================================
