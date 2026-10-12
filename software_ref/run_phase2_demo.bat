@echo off
title Phase 2: MNIST Inference on Systolic Accelerator
cd /d "%~dp0"
echo ===============================================================================
echo   Running Phase 2: im2col + Tiling Engine + MNIST INT8 Inference
echo ===============================================================================

set "PY=C:\Users\hoang\AppData\Local\Programs\Python\Python313\python.exe"
if exist "%PY%" (
    "%PY%" run_mnist_inference.py
) else (
    python run_mnist_inference.py
)

echo.
pause
