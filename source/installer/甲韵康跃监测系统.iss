; 甲韵康跃监测系统 - Windows 安装向导
; 用 Inno Setup 编译后会生成「下一步 / 安装 / 完成」安装包

#define MyAppName "甲韵康跃监测系统"
#define MyAppVersion "1.0.1"
#define MyAppPublisher "甲韵康跃"
#define MyAppExeName "甲韵康跃监测系统.exe"

[Setup]
AppId={{8E4C2A71-6B3F-4D19-9C5A-21F0A8D47B16}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\installer_output
OutputBaseFilename=甲韵康跃监测系统安装包
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
UsePreviousAppDir=no
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
SetupLogging=yes
DisableWelcomePage=no
AllowNoIcons=yes
ChangesAssociations=no
CloseApplications=force
RestartApplications=no
VersionInfoVersion=1.0.1
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} 安装程序
VersionInfoProductName={#MyAppName}

[Languages]
Name: "chinesesimplified"; MessagesFile: "ChineseSimplified.isl"

[Messages]
WelcomeLabel1=欢迎安装 [name]
WelcomeLabel2=这是「甲韵康跃 · 监测与预警系统」的安装程序。%n%n请先关掉已经打开的监测窗口，再点「下一步」。装完后会在开始菜单和桌面生成快捷方式。
FinishedLabel=安装已经完成。您可以马上打开监测系统，也可以以后从桌面快捷方式打开。
ClickFinish=点「完成」关闭此安装向导。
SelectDirLabel3=安装程序会把软件装到下面的文件夹。一般不用改，直接点「下一步」。
SelectDirBrowseLabel=若要换别的位置，点「浏览」。
ReadyLabel1=已经准备好把 [name] 装到这台电脑。
ReadyLabel2a=点「安装」开始复制文件。
InstallingLabel=正在安装，请稍候…
ButtonInstall=安装(&I)
ButtonNext=下一步(&N)
ButtonBack=上一步(&B)
ButtonFinish=完成(&F)
ButtonCancel=取消
SetupAppTitle=甲韵康跃监测系统 安装
SetupWindowTitle=甲韵康跃监测系统 安装向导
UninstallAppFullTitle=卸载 甲韵康跃监测系统
ConfirmUninstall=确定要从这台电脑卸下 %1 吗？

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加图标:"; Flags: checkedonce

[InstallDelete]
Type: filesandordirs; Name: "{app}\_internal"

[Files]
Source: "..\dist\甲韵康跃监测系统\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "ucrtbase.dll"

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{group}\使用说明"; Filename: "{app}\甲韵康跃监测系统使用说明.docx"
Name: "{group}\卸载 {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "立即打开 甲韵康跃监测系统"; Flags: nowait postinstall skipifsilent
Filename: "{app}\甲韵康跃监测系统使用说明.docx"; Description: "打开使用说明（Word）"; Flags: nowait postinstall skipifsilent unchecked shellexec

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
