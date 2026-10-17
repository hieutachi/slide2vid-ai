@echo off
title SlideVoice Setup (Windows)
chcp 65001 >nul

echo SlideVoice setup - Python 3.11+ required
python --version >nul 2>&1 || (echo [FAILED] Install Python 3.11+ from python.org ^& exit /b 1)
for /f "tokens=2 delims=." %%v in ('python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"') do set PY_MINOR=%%v
if %PY_MINOR% LSS 11 (echo [FAILED] Python 3.11 or newer is required. ^& exit /b 1)
if not exist ".venv\Scripts\python.exe" python -m venv .venv || exit /b 1
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel || exit /b 1
python -m pip install -e ".[dev]" || exit /b 1
python -m slidevoice --help || exit /b 1

echo.
echo Preflight (informational; ffmpeg/ffprobe must be installed separately and on PATH):
python -m slidevoice doctor
echo.
echo Setup complete. Run: python -m slidevoice smoke --out out\installed_smoke
pause