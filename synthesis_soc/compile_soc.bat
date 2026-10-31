@echo off
echo ========================================================
echo   [DEPRECATED / ARCHIVED] TERASIC DE1 BUILD SCRIPT
echo ========================================================
echo [WARNING] Project DE1 is deprecated because EP2C20 has only
echo           52 multipliers, while the project uses an 8x8
echo           systolic array (requiring 64 multipliers).
echo.
echo Please use the primary project target:
echo   cd ..\synthesis_soc_de2
echo   compile_soc_de2.bat
echo ========================================================
echo.
pause

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
echo   COMPILATION COMPLETED! (NOTE: DE1 IS ARCHIVED)
echo ========================================================
