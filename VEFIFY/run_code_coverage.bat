@echo off
setlocal
cd /d "%~dp0"
echo ====================================================================
echo Running ModelSim RTL Code Coverage Analysis (bcesf)
echo ====================================================================
C:\13.0sp1\modelsim_ase\win32aloem\vsim.exe -c -do run_code_coverage.do
echo ====================================================================
echo Code Coverage Analysis Complete. Report saved to code_coverage_report.txt
echo ====================================================================
