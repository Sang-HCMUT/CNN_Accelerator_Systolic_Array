@echo off
cd /d "%~dp0"
echo ========================================================
echo   OPENING MODELSIM GUI: PHASE 4 DE1 BOARD IO WAVEFORM
echo ========================================================
C:\13.0sp1\modelsim_ase\win32aloem\vsim.exe -do wave_de1_io.do
