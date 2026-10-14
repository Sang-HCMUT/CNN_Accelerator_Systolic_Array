@echo off
echo ========================================================
echo   PROGRAMMING TERASIC DE10-STANDARD (Cyclone V 5CSXFC6D6)
echo ========================================================

cd /d "%~dp0"

SET QUARTUS_BIN=C:\intelFPGA_lite\20.1\quartus\bin64

if not exist output_files\soc_top_de10.sof (
    echo [ERROR] output_files\soc_top_de10.sof not found! Please run compile_soc_de10.bat first.
    pause
    exit /b 1
)

echo Checking Altera / Intel USB-Blaster cables...
"%QUARTUS_BIN%\jtagconfig.exe"

echo.
echo Attempting to program soc_top_de10.sof to FPGA...
echo Note: On DE10-Standard SoC, FPGA is typically device index @2 on JTAG chain.
"%QUARTUS_BIN%\quartus_pgm.exe" -m JTAG -o "p;output_files\soc_top_de10.sof@2"

if %errorlevel% neq 0 (
    echo.
    echo Trying device index @1 in case of direct JTAG chain...
    "%QUARTUS_BIN%\quartus_pgm.exe" -m JTAG -o "p;output_files\soc_top_de10.sof@1"
)

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Programming failed! Please ensure:
    echo   1. DE10-Standard board is powered ON (Power toggle switch).
    echo   2. USB-Blaster II cable is connected to USB BLASTER port.
    echo   3. Device driver is installed (USB-Blaster II in Device Manager).
    echo   4. If multiple cables exist, open Quartus Prime GUI Programmer to select.
    pause
    exit /b %errorlevel%
)

echo.
echo ========================================================
echo   DE10-STANDARD FPGA PROGRAMMED SUCCESSFULLY!
echo ========================================================
pause
