@echo off
echo ========================================
echo 销冠云团 - 停止系统
echo ========================================
echo.

cd /d "%~dp0"

echo 正在停止所有容器...
docker-compose down
echo.

echo ✅ 系统已停止
echo.
pause
