@echo off
setlocal
cd /d "%~dp0\.."
echo This will stop the app and delete demo database data.
choice /M "Continue"
if errorlevel 2 exit /b 0
docker compose down -v
endlocal
