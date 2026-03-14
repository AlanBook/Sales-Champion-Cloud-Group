@echo off
echo ========================================
echo 销冠云团 - 后端启动脚本 (无 Docker 版)
echo ========================================
echo.

cd /d "%~dp0"

echo 正在启动后端服务...
echo 数据库：SQLite
echo API 地址：http://localhost:8000
echo.

set PYTHONPATH=%~dp0src;%PYTHONPATH%
python -m uvicorn sales_champion_backend.main:app --host 0.0.0.0 --port 8000 --reload

pause
