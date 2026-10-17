@echo off
title SlideVoice Worker Setup (GPU + VieNeu)
chcp 65001 >nul
set WORKER_DIR=workers\vieneu
set CACHE_ROOT=%CD%\models\vieneu
set ALLOWED_ROOT=%CD%\out

echo SlideVoice VieNeu worker setup - CUDA GPU required
python --version >nul 2>&1 || (echo [FAILED] Python not found. ^& exit /b 1)
if not exist "%WORKER_DIR%\.venv\Scripts\python.exe" python -m venv "%WORKER_DIR%\.venv" || exit /b 1
"%WORKER_DIR%\.venv\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel || exit /b 1
"%WORKER_DIR%\.venv\Scripts\python.exe" -m pip install torch==2.8.0 torchaudio==2.8.0 --index-url https://download.pytorch.org/whl/cu128 || exit /b 1
"%WORKER_DIR%\.venv\Scripts\python.exe" -m pip install -r "%WORKER_DIR%\requirements.txt" || exit /b 1
if not exist "%CACHE_ROOT%" mkdir "%CACHE_ROOT%"
"%WORKER_DIR%\.venv\Scripts\python.exe" "%WORKER_DIR%\download_models.py" --cache-root "%CACHE_ROOT%" || exit /b 1
"%WORKER_DIR%\.venv\Scripts\python.exe" -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('Device count:', torch.cuda.device_count())"
echo Start worker using server.py; it binds only to 127.0.0.1:8770. Do not expose it to a network.
echo "%WORKER_DIR%\.venv\Scripts\python.exe" "%WORKER_DIR%\server.py" --allowed-root "%ALLOWED_ROOT%" --cache-root "%CACHE_ROOT%" --port 8770
pause
