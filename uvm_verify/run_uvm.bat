@echo off
echo ====================================================================
echo   UVM VERIFICATION SUITE: 2D SYSTOLIC GEMM ACCELERATOR
echo   Universal Verification Methodology (UVM 1.1c) on ModelSim
echo ====================================================================
echo.

cd /d "%~dp0"

set TESTNAME=gemm_directed_test
if not "%~1"=="" set TESTNAME=%~1

echo [INFO] Target UVM Test: %TESTNAME%
echo.

C:\13.0sp1\modelsim_ase\win32aloem\vsim.exe -c -do "set UVM_TEST %TESTNAME%; do run_uvm.do"

echo.
echo ====================================================================
echo   UVM SIMULATION COMPLETE!
echo ====================================================================
