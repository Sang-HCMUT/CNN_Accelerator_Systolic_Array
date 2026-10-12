@echo off
echo ========================================================
echo   COMPILING RISC-V SoC TOP ON CYCLONE II (EP2C20F484C7)
echo ========================================================

cd /d "%~dp0"

echo [1/4] Running Quartus Analysis and Synthesis (quartus_map)...
C:\13.0sp1\quartus\bin64\quartus_map.exe soc_top
if %errorlevel% neq 0 (
    echo [ERROR] Synthesis failed!
    exit /b %errorlevel%
)

echo [2/4] Running Quartus Fitter Place and Route (quartus_fit)...
C:\13.0sp1\quartus\bin64\quartus_fit.exe soc_top
if %errorlevel% neq 0 (
    echo [ERROR] Fitting failed!
    exit /b %errorlevel%
)

echo [3/4] Running Quartus Assembler (quartus_asm) to generate .sof...
C:\13.0sp1\quartus\bin64\quartus_asm.exe soc_top
if %errorlevel% neq 0 (
    echo [ERROR] Assembler failed!
    exit /b %errorlevel%
)

echo [4/4] Running TimeQuest Timing Analyzer (quartus_sta)...
C:\13.0sp1\quartus\bin64\quartus_sta.exe soc_top
if %errorlevel% neq 0 (
    echo [ERROR] STA failed!
    exit /b %errorlevel%
)

echo ========================================================
echo   COMPILATION COMPLETED SUCCESSFULLY!
echo ========================================================

