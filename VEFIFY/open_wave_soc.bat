@echo off
cd /d "%~dp0"
echo ========================================================
echo   OPENING MODELSIM GUI: PHASE 3 & 4 SOC CO-SIMULATION WAVEFORM
echo ========================================================
C:\13.0sp1\modelsim_ase\win32aloem\vsim.exe -do wave_soc.do
