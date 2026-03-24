@echo off
chcp 65001 >nul
echo ========================================
echo AMC 文书生成器 - Web 服务
echo ========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

:: 检查依赖
echo [1/3] 检查依赖...
pip install -q flask docxtpl pandas openpyxl python-docx requests

:: 确保目录存在
echo [2/3] 初始化目录...
if not exist "generated\风险合规部" mkdir "generated\风险合规部"
if not exist "generated\业务部" mkdir "generated\业务部"

:: 启动服务
echo [3/3] 启动服务...
echo.
echo 请在浏览器中访问：
echo   http://127.0.0.1:5000
echo.
echo 按 CTRL+C 停止服务
echo ========================================

python app.py

pause
