@echo off
echo ========================================
echo 销冠云团 - Docker 启动脚本
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] 检查 Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Docker 未安装或未运行
    echo 请先安装 Docker Desktop 并确保正在运行
    echo.
    echo 下载地址：https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)
echo [完成] Docker 已安装
echo.

echo [2/4] 停止旧的容器...
docker-compose down >nul 2>&1
echo [完成] 清理完成
echo.

echo [3/4] 启动 Docker Compose...
docker-compose up -d --build
if %errorlevel% neq 0 (
    echo [错误] Docker Compose 启动失败
    pause
    exit /b 1
)
echo [完成] 容器已启动
echo.

echo [4/4] 等待服务启动...
timeout /t 15 /nobreak >nul
echo.

echo ========================================
echo ✅ 销冠云团系统已启动成功！
echo ========================================
echo.
echo 访问地址：http://localhost:8000
echo 前端地址：http://localhost:3000
echo.
echo 登录账号：
echo   - boss_demo / password
echo   - manager_demo / password
echo   - admin_demo / password
echo   - staff_08 / password
echo.
echo 按任意键打开浏览器...
pause >nul

start http://localhost:3000

echo.
echo 如需停止系统，请运行：stop-sales-champion.bat
echo.
pause
