@echo off
echo ========================================================
echo   PROGRAMMING TERASIC DE2 FPGA (Cyclone II EP2C35F672C6)
echo ========================================================

cd /d "%~dp0"

if not exist soc_top_de2.sof (
    echo [ERROR] soc_top_de2.sof not found! Please run compile_soc_de2.bat first.
    pause
    exit /b 1
)

echo Checking Altera USB-Blaster cables...
C:\13.0sp1\quartus\bin64\jtagconfig.exe

echo.
echo Programming soc_top_de2.sof to FPGA via USB-Blaster JTAG...
C:\13.0sp1\quartus\bin64\quartus_pgm.exe -c "USB-Blaster" -m JTAG -o "p;soc_top_de2.sof@1"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Programming failed! Please ensure:
    echo   1. DE2 board is powered ON (Blue push button).
    echo   2. USB-Blaster cable is firmly connected and drivers installed in Device Manager.
    echo   3. RUN/PROG switch on DE2 is set to RUN.
    pause
    exit /b %errorlevel%
)

echo.
echo ========================================================
echo   DE2 FPGA PROGRAMMED SUCCESSFULLY!
echo ========================================================
pause
