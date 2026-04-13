@echo off
chcp 65001 >nul
echo ========================================
echo AMC 文档生成系统 - 生产环境启动
echo ========================================
echo.
echo [线程数] 12（支持约10人同时生成文档）
echo [访问地址] http://127.0.0.1:5000
echo.
echo 按 CTRL+C 停止服务
echo ========================================
echo.

:: 检测并使用虚拟环境（优先使用 .venv，否则尝试 .venv.bak）
if exist ".venv\Scripts\python.exe" (
    set PYTHON=.venv\Scripts\python.exe
) else if exist ".venv.bak\Scripts\python.exe" (
    set PYTHON=.venv.bak\Scripts\python.exe
) else (
    set PYTHON=python
)

:: 检查 Python
%PYTHON% --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

:: 确保目录存在
if not exist "generated\风险合规部" mkdir "generated\风险合规部"
if not exist "generated\业务部" mkdir "generated\业务部"

:: 启动 waitress 生产服务器
%PYTHON% -m waitress --host=0.0.0.0 --port=5000 --threads=12 app:app
pause
