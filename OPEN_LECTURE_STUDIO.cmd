@echo off
cd /d D:\SOFT\STV
if not exist "D:\SOFT\STV\out\lecture_demo\studio_v2\index.html" (
  echo Studio demo not generated. See D:\SOFT\STV\PRESENTATION_GUIDE.md
  exit /b 1
)
"D:\SOFT\STV\.venv311\Scripts\python.exe" -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8767/demo_evidence.json', timeout=2)" >nul 2>nul
if errorlevel 1 start "SlideVoice studio playback" /min "D:\SOFT\STV\.venv311\Scripts\python.exe" -m samples.playback --root D:\SOFT\STV\out\lecture_demo --port 8767
timeout /t 2 /nobreak >nul
start "" http://127.0.0.1:8767/studio_v2/