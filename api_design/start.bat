@echo off
echo ==============================================
echo    FFXIV Combat Data API 启动脚本
echo ==============================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo [信息] Python已安装
echo.

REM 检查是否在正确目录
if not exist "main.py" (
    echo [错误] 未找到main.py文件，请确保在正确的目录下运行此脚本
    pause
    exit /b 1
)

REM 检查和创建Definitions目录
if not exist "..\Definitions" (
    echo [信息] 创建 Definitions 目录...
    mkdir "..\Definitions" 2>nul
    copy "..\Definitions\BlackMage_sample.json" "..\Definitions\BlackMage.json" 2>nul
)

REM 检查和创建Overrides目录
if not exist "..\Overrides" (
    echo [信息] 创建 Overrides 目录...
    mkdir "..\Overrides" 2>nul
    copy "..\Overrides\sample_overrides.txt" "..\Overrides\global_sample.txt" 2>nul
)

echo [信息] 检查依赖包...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo [警告] 未安装FastAPI，正在安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖包安装失败
        pause
        exit /b 1
    )
    echo [成功] 依赖包安装完成
) else (
    echo [信息] 依赖包已安装
)

echo.
echo [信息] 启动API服务器...
echo.
echo 服务将在以下地址运行:
echo   - API文档: http://localhost:8000/docs
echo   - 健康检查: http://localhost:8000/health
echo   - 前端示例: 请用浏览器打开 frontend_example.html
echo.
echo 按 Ctrl+C 停止服务
echo.

python main.py