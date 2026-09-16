@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在安装打包依赖...
python -m pip install -r requirements.txt
echo 正在打包成 Windows 软件，请稍候...
python -m PyInstaller --noconfirm --clean "甲韵康跃监测系统.spec"
echo.
echo 完成。软件位置:
echo %~dp0dist\甲韵康跃监测系统\甲韵康跃监测系统.exe
echo.
pause
