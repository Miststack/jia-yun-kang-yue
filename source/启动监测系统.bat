@echo off
chcp 65001 >nul
cd /d "%~dp0"
python -c "import webview, serial" 2>nul
if errorlevel 1 (
    echo 正在安装运行库，请稍候...
    python -m pip install -r requirements.txt
)
start "" pythonw "%~dp0main.py"
if errorlevel 1 python "%~dp0main.py"
