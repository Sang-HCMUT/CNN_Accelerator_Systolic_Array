@echo off
echo ========================================================
echo   PROGRAMMING TERASIC DE1 FPGA (Cyclone II EP2C20F484C7)
echo ========================================================

cd /d "%~dp0"

if not exist soc_top.sof (
    echo [ERROR] soc_top.sof not found! Please run compile_soc.bat first.
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
    echo [ERROR] Programming failed! Please ensure:
    echo   1. DE1 board is powered ON (Red push button).
    echo   2. USB-Blaster cable is firmly connected and drivers installed in Device Manager.
    echo   3. RUN/PROG switch on DE1 is set to RUN.
    pause
    exit /b %errorlevel%
)

echo.
echo ========================================================
echo   DE1 FPGA PROGRAMMED SUCCESSFULLY!
echo ========================================================
pause
