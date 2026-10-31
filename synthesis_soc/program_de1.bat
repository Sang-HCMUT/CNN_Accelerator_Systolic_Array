@echo off
echo ========================================================
echo   [DEPRECATED / ARCHIVED] PROGRAMMING TERASIC DE1 FPGA
echo ========================================================
echo [WARNING] Project DE1 is deprecated. The active deployment
echo           targets are Terasic DE2 (synthesis_soc_de2) and
echo           Terasic DE10-Standard (synthesis_soc_de10).
echo ========================================================
echo.

cd /d "%~dp0"

if not exist soc_top.sof (
    echo [ERROR] soc_top.sof not found!
    pause
    exit /b 1
)

echo Checking Altera USB-Blaster cables...
C:\13.0sp1\quartus\bin64\jtagconfig.exe

echo.
echo Programming soc_top.sof to FPGA via USB-Blaster JTAG...
C:\13.0sp1\quartus\bin64\quartus_pgm.exe -c "USB-Blaster" -m JTAG -o "p;soc_top.sof@1"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Programming failed!
    pause
    exit /b %errorlevel%
)

echo.
echo ========================================================
echo   DE1 FPGA PROGRAMMED (NOTE: DE1 IS ARCHIVED)
echo ========================================================
pause
