@echo off
cd /d "%~dp0"
echo ========================================================
echo   OPENING MODELSIM GUI: PHASE 1 SYSTOLIC GEMM WAVEFORM
echo ========================================================
C:\13.0sp1\modelsim_ase\win32aloem\vsim.exe -do run_gemm_sim.do
