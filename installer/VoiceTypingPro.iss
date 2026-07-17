#define MyAppName "বাংলা ভয়েস টাইপিং প্রো"
#define MyAppVersion "2.1.1"
#define MyAppPublisher "Hafez Mahdi Hasan"
#define MyAppExeName "BanglaVoiceTypingPro.exe"

[Setup]
AppId={{4E84D224-58CB-4FF3-9E17-79DCFA28559D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\BanglaVoiceTypingPro
DefaultGroupName={#MyAppName}
PrivilegesRequired=lowest
OutputDir=..\installer-dist
OutputBaseFilename=BanglaVoiceTypingPro-Setup-{#MyAppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"
Name: "startup"; Description: "Start বাংলা ভয়েস টাইপিং প্রো with Windows"; GroupDescription: "Startup:"

[Files]
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--minimized"; Tasks: startup

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
