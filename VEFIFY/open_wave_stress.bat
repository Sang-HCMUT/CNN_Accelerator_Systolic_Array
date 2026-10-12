@echo off
cd /d "%~dp0"
echo ========================================================
echo   OPENING MODELSIM GUI: WAVEFORM 2 - STRESS TEST
echo ========================================================
C:\13.0sp1\modelsim_ase\win32aloem\vsim.exe -do run_stress_sim.do
