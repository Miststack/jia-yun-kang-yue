@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在应用 config.json ...
python "%~dp0apply_config.py"
if errorlevel 1 (
    echo 配置失败。
    pause
    exit /b 1
)
call "%~dp0branding.inc.bat"
echo 正在安装打包依赖...
python -m pip install -r requirements.txt
echo 正在打包成 Windows 软件，请稍候...
python -m PyInstaller --noconfirm --clean "甲韵康跃监测系统.spec"
echo.
echo 完成。软件位置:
echo %~dp0dist\%APP_SHORT_NAME%\%APP_SHORT_NAME%.exe
echo.
pause
