[Setup]
AppName=WinSecureAuditor
AppVersion=1.0
DefaultDirName={pf}\WinSecureAuditor
DefaultGroupName=WinSecureAuditor
OutputDir=.
OutputBaseFilename=WinSecureAuditor_Installer
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "main.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "gui.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "parser.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "executor.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "evaluator.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "reporter.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "sca_structs.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "scoring.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "scanner.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "rules\*"; DestDir: "{app}\rules"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\WinSecureAuditor"; Filename: "{app}\gui.py"; WorkingDir: "{app}"; IconFilename: "{app}\gui.py"
Name: "{group}\{cm:UninstallProgram,WinSecureAuditor}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\WinSecureAuditor"; Filename: "{app}\gui.py"; Tasks: desktopicon

[Run]
Filename: "{app}\gui.py"; Description: "{cm:LaunchProgram,WinSecureAuditor}"; Flags: nowait postinstall skipifsilent