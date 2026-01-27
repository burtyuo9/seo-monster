; ============================================
; SEO Monster - Inno Setup Installer Script
; Для создания полноценного Windows установщика
; ============================================

#define MyAppName "SEO Monster"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "SEO Monster Team"
#define MyAppURL "https://github.com/burtyuo9/seo-monster"
#define MyAppExeName "SEO Monster.exe"

[Setup]
; Основные настройки
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; Требуем права администратора для установки зависимостей
PrivilegesRequired=admin
; Выходной файл
OutputDir=output
OutputBaseFilename=SEOMonster_Setup_{#MyAppVersion}
; Сжатие
Compression=lzma2/ultra64
SolidCompression=yes
; Внешний вид
WizardStyle=modern
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[CustomMessages]
russian.InstallingPython=Установка Python...
russian.InstallingNodeJS=Установка Node.js...
russian.InstallingDependencies=Установка зависимостей...
russian.ConfiguringBackend=Настройка Backend...
russian.ConfiguringFrontend=Настройка Frontend...
english.InstallingPython=Installing Python...
english.InstallingNodeJS=Installing Node.js...
english.InstallingDependencies=Installing dependencies...
english.ConfiguringBackend=Configuring Backend...
english.ConfiguringFrontend=Configuring Frontend...

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; GUI приложение
Source: "release\SEO Monster.exe"; DestDir: "{app}"; Flags: ignoreversion
; Скрипты
Source: "install.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "install.ps1"; DestDir: "{app}"; Flags: ignoreversion
; Документация
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
; Исходный код проекта (опционально - можно клонировать из git)
; Source: "..\backend\*"; DestDir: "{app}\backend"; Flags: ignoreversion recursesubdirs createallsubdirs
; Source: "..\frontend\*"; DestDir: "{app}\frontend"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "node_modules\*"

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Запуск установки зависимостей после установки
Filename: "{app}\install.bat"; Description: "Установить зависимости и настроить проект"; Flags: nowait postinstall skipifsilent runascurrentuser
; Запуск приложения после установки
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Проверка наличия Python
function IsPythonInstalled: Boolean;
var
  ResultCode: Integer;
begin
  Result := Exec('cmd.exe', '/c python --version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0);
end;

// Проверка наличия Node.js
function IsNodeInstalled: Boolean;
var
  ResultCode: Integer;
begin
  Result := Exec('cmd.exe', '/c node --version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0);
end;

// Проверка наличия Git
function IsGitInstalled: Boolean;
var
  ResultCode: Integer;
begin
  Result := Exec('cmd.exe', '/c git --version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0);
end;

// Инициализация установки
function InitializeSetup: Boolean;
var
  MissingDeps: String;
begin
  MissingDeps := '';
  
  if not IsPythonInstalled then
    MissingDeps := MissingDeps + '- Python 3.11+' + #13#10;
  
  if not IsNodeInstalled then
    MissingDeps := MissingDeps + '- Node.js 20+' + #13#10;
  
  if not IsGitInstalled then
    MissingDeps := MissingDeps + '- Git' + #13#10;
  
  if MissingDeps <> '' then
  begin
    if MsgBox('Следующие зависимости не найдены:' + #13#10 + #13#10 + 
              MissingDeps + #13#10 +
              'Установщик попытается установить их автоматически.' + #13#10 +
              'Продолжить?', mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := False;
      Exit;
    end;
  end;
  
  Result := True;
end;

// После установки
procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Здесь можно добавить дополнительные действия после установки
  end;
end;

[UninstallDelete]
Type: filesandordirs; Name: "{app}\backend\venv"
Type: filesandordirs; Name: "{app}\frontend\node_modules"
Type: filesandordirs; Name: "{app}\frontend\dist"
