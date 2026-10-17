@echo off
cd /d D:\SOFT\STV
"D:\SOFT\STV\.venv311\Scripts\python.exe" -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8766/', timeout=2)" >nul 2>nul
if errorlevel 1 start "SlideVoice Vietnamese playback" /min "D:\SOFT\STV\.venv311\Scripts\python.exe" -m samples.playback --root D:\SOFT\STV\out\qa_vietnamese_20261015\delivery --port 8766
timeout /t 2 /nobreak >nul
start "" http://127.0.0.1:8766/