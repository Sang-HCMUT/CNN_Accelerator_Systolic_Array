@echo off
setlocal
cd /d "%~dp0"

set TESTNAME=gemm_directed_test
if not "%~1"=="" set TESTNAME=%~1

echo Running UVM test: %TESTNAME%
C:\13.0sp1\modelsim_ase\win32aloem\vsim.exe -c -do "set UVM_TEST %TESTNAME%; do run_uvm.do"
