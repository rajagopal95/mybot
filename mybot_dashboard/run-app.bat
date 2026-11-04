@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  start "Forklift OS web server" /min py -m http.server 8000 --bind 127.0.0.1
) else (
  start "Forklift OS web server" /min python -m http.server 8000 --bind 127.0.0.1
)
timeout /t 2 /nobreak >nul
start "Forklift OS" "http://localhost:8000/"
echo Forklift OS is running at http://localhost:8000/
echo Close the minimized web server window when you are finished.
