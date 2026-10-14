@echo off
echo ====================================================================
echo   COMPILING 8x8 RISC-V SoC CNN ACCELERATOR
echo   Target: Intel Cyclone V 5CSXFC6D6F31C6N (Terasic DE10-Standard)
echo   Array:  8x8 Systolic Array (64 PEs, 64 DSP Blocks)
echo   Tool:   Intel Quartus Prime Lite 20.1
echo ====================================================================
echo.

cd /d "%~dp0"

REM -----------------------------------------------------------------------
REM NOTE: Requires Quartus Prime Lite 20.1 for Cyclone V support.
REM       Install path: C:\intelFPGA_lite\20.1\quartus\bin64\
REM       If installed elsewhere, update QUARTUS_BIN below.
REM -----------------------------------------------------------------------

SET QUARTUS_BIN=C:\intelFPGA_lite\20.1\quartus\bin64
SET PROJECT=soc_top_de10

echo [INFO] Quartus Binary Path: %QUARTUS_BIN%
echo [INFO] Project Name: %PROJECT%
echo.

REM Check if Quartus exists
if not exist "%QUARTUS_BIN%\quartus_map.exe" (
    echo [ERROR] Quartus Prime Lite 20.1 not found at: %QUARTUS_BIN%
    echo         Verify installation at: C:\intelFPGA_lite\20.1\quartus\bin64\
    echo         Or edit QUARTUS_BIN in this script to match your path.
    pause
    exit /b 1
)

echo [1/4] Running Analysis and Synthesis (quartus_map)...
"%QUARTUS_BIN%\quartus_map.exe" %PROJECT%
if %errorlevel% neq 0 (
    echo [ERROR] Synthesis FAILED! Check synthesis errors above.
    pause
    exit /b %errorlevel%
)
echo [OK] Synthesis completed.
echo.

echo [2/4] Running Fitter - Place and Route (quartus_fit)...
"%QUARTUS_BIN%\quartus_fit.exe" %PROJECT%
if %errorlevel% neq 0 (
    echo [ERROR] Fitter FAILED! Check timing or resource errors above.
    pause
    exit /b %errorlevel%
)
echo [OK] Place and Route completed.
echo.

echo [3/4] Running Assembler - Generate bitstream (quartus_asm)...
"%QUARTUS_BIN%\quartus_asm.exe" %PROJECT%
if %errorlevel% neq 0 (
    echo [ERROR] Assembler FAILED!
    pause
    exit /b %errorlevel%
)
echo [OK] Bitstream generated: %PROJECT%.sof
echo.

echo [4/4] Running TimeQuest Static Timing Analysis (quartus_sta)...
"%QUARTUS_BIN%\quartus_sta.exe" %PROJECT%
if %errorlevel% neq 0 (
    echo [WARNING] STA completed with timing violations. Check .sta.rpt for details.
)
echo [OK] STA completed.
echo.

echo ====================================================================
echo   BUILD COMPLETE!
echo   Bitstream: synthesis_soc_de10\%PROJECT%.sof
echo   STA Report: synthesis_soc_de10\%PROJECT%.sta.rpt
echo ====================================================================
echo.
echo   To program DE10-Standard:
echo     1. Open Quartus Programmer
echo     2. Hardware Setup -> USB-Blaster
echo     3. Add device: %PROJECT%.sof
echo     4. Program!
echo.
pause
