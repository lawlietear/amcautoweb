@echo off
chcp 65001 >nul
echo ========================================
echo AMC Doc Generator - Web 服务
echo ========================================
echo.

:: 检测并使用虚拟环境（优先使用 .venv，否则尝试 .venv.bak）
if exist ".venv\Scripts\python.exe" (
    echo [信息] 使用虚拟环境: .venv
    set PYTHON=.venv\Scripts\python.exe
) else if exist ".venv.bak\Scripts\python.exe" (
    echo [信息] 使用备份虚拟环境: .venv.bak
    set PYTHON=.venv.bak\Scripts\python.exe
) else (
    echo [信息] 未找到虚拟环境，使用系统 Python
    set PYTHON=python
)

:: 检查 Python
%PYTHON% --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

:: 检查依赖（如果使用系统Python则安装依赖）
if "%PYTHON%"=="python" (
    echo [1/3] 检查依赖...
    pip install -q flask docxtpl pandas openpyxl python-docx requests
)

:: 确保目录存在
echo [2/3] 初始化目录...
if not exist "generated\风险合规部" mkdir "generated\风险合规部"
if not exist "generated\业务部" mkdir "generated\业务部"

:: 选择启动模式
echo.
echo [3/3] 选择启动模式...
echo.
echo   [1] 开发模式 ^(Flask - 自动重载，适合调试^)
echo   [2] 生产模式 ^(Waitress - 稳定并发，适合多人使用^)
echo.
set /p MODE=请选择 ^(1/2，默认为1^):

:: 启动服务
echo.
echo ========================================
echo.

if "%MODE%"=="2" (
    echo [生产模式] 使用 Waitress 启动服务...
    echo [提示] 此模式支持10+人并发，代码修改后需重启才能生效
echo.
    echo 请在浏览器中访问：
    echo   http://127.0.0.1:5000
    echo.
    echo 按 CTRL+C 停止服务
    echo ========================================
    %PYTHON% -m waitress --host=0.0.0.0 --port=5000 app:app
) else (
    echo [开发模式] 使用 Flask 启动服务...
    echo [提示] 此模式支持代码热重载，适合开发调试
echo.
    echo 请在浏览器中访问：
    echo   http://127.0.0.1:5000
    echo.
    echo 按 CTRL+C 停止服务
    echo ========================================
    %PYTHON% app.py
)

pause
