@echo off
setlocal

cd /d "%~dp0\.."

where docker >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Docker Desktop is not installed or docker is not in PATH.
  echo Install Docker Desktop for Windows first, then run this file again.
  pause
  exit /b 1
)

docker info >nul 2>nul
if errorlevel 1 (
  echo [INFO] Docker Desktop is not running. Trying to start it...
  if exist "C:\Program Files\Docker\Docker\Docker Desktop.exe" (
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo Waiting for Docker Desktop to become ready...
    powershell -ExecutionPolicy Bypass -File "%~dp0\wait-for-docker.ps1"
    if errorlevel 1 (
      echo [ERROR] Docker Desktop did not become ready in time.
      pause
      exit /b 1
    )
  ) else (
    echo [ERROR] Docker Desktop is not running.
    echo Start Docker Desktop manually, then run this file again.
    pause
    exit /b 1
  )
)

echo [INFO] Starting sales champion demo...
docker compose up --build -d
if errorlevel 1 (
  echo [ERROR] Failed to start containers.
  pause
  exit /b 1
)

powershell -ExecutionPolicy Bypass -File "%~dp0\wait-and-open.ps1"
endlocal
