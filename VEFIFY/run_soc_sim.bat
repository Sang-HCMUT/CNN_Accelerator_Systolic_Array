@echo off
set MODELSIM_BIN=C:\13.0sp1\modelsim_ase\win32aloem
cd /d "%~dp0"
"%MODELSIM_BIN%\vsim.exe" -c -do "do run_soc_sim.do" -l transcript_soc_sim.log
