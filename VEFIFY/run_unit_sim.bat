@echo off
set MODELSIM_BIN=C:\13.0sp1\modelsim_ase\win32aloem
cd /d "%~dp0"
echo ========================================================
echo   RUNNING UNIT-LEVEL HARDWARE VERIFICATION REGRESSION
echo ========================================================
"%MODELSIM_BIN%\vsim.exe" -c -do "do run_unit_sim.do" -l transcript_unit_sim.log
echo ========================================================
echo   CHECKING TRANSCRIPT OUTPUT
echo ========================================================
type transcript_unit_sim.log | findstr "VERIFICATION RESULT Total Passed Failed"
