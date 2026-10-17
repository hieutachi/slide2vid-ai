@echo off
cd /d D:\SOFT\STV
python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8765/', timeout=2)" >nul 2>nul
if errorlevel 1 start "SlideVoice local playback server" /min python -m samples.playback --root D:\SOFT\STV\out\qa_slides_20261015\delivery --port 8765
timeout /t 2 /nobreak >nul
start "" http://127.0.0.1:8765/