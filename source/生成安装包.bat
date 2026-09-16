@echo off
chcp 65001 >nul
cd /d "%~dp0"

python "%~dp0apply_config.py"
if errorlevel 1 (
  echo 配置失败。
  pause
  exit /b 1
)
call "%~dp0branding.inc.bat"

set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if exist "%LocalAppData%\Programs\Inno Setup 6\ISCC.exe" set "ISCC=%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"

if not defined ISCC (
  echo 未找到 Inno Setup 编译器。请先安装 Inno Setup 6。
  pause
  exit /b 1
)

if not exist "%~dp0dist\%APP_SHORT_NAME%\%APP_SHORT_NAME%.exe" (
  echo 还没有打包好的程序，正在先生成 EXE...
  call "%~dp0打包成EXE.bat"
)

echo 正在编译安装包...
"%ISCC%" "%~dp0installer\甲韵康跃监测系统.iss"
if errorlevel 1 (
  echo 编译失败。
  pause
  exit /b 1
)

echo.
copy /Y "%~dp0installer_output\%APP_SHORT_NAME%安装包.exe" "%USERPROFILE%\Desktop\%APP_SHORT_NAME%安装包.exe" >nul
echo.
echo 安装包已生成，并已放到桌面:
echo 桌面\%APP_SHORT_NAME%安装包.exe
echo.
pause
