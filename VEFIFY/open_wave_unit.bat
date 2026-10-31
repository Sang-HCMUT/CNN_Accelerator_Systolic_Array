@echo off
cd /d "%~dp0"
echo ========================================================
echo   OPENING MODELSIM GUI: UNIT-LEVEL HARDWARE WAVEFORMS
echo ========================================================
C:\13.0sp1\modelsim_ase\win32aloem\vsim.exe -do run_unit_sim.do
