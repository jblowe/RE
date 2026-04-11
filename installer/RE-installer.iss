; =============================================================================
; Reconstruction Engine — Windows Installer
; =============================================================================
;
; BUILD INSTRUCTIONS
; ------------------
; 1. Install Inno Setup from https://jrsoftware.org/isdl.php
; 2. Place the MSYS2 installer in this directory, renamed to:
;      msys2-installer.exe
;    (download from https://www.msys2.org/ — pick the x86_64 .exe)
; 3. From this directory run:
;      ISCC.exe RE-installer.iss
;    The finished installer appears in installer\dist\RE-setup.exe
;
; NOTE: The GitHub Actions workflow (build-windows-installer.yml) does all
; of the above automatically on every tagged release.
; =============================================================================

#define AppName      "Reconstruction Engine"
#define AppVersion   "1.0"
#define AppPublisher "John B. Lowe"
#define AppURL       "https://github.com/jblowe/RE"
#define Msys2Dir     "C:\msys64"
#define Msys2Python  "C:\msys64\ucrt64\bin\python.exe"

[Setup]
AppId={{63D7B5AC-EF2C-4642-A90E-987CCDF26184}}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
; Install to C:\RE2 — no spaces, works easily inside MSYS2 bash
DefaultDirName=C:\RE2
DefaultGroupName={#AppName}
OutputDir=dist
OutputBaseFilename=RE-setup
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Dirs]
; Create MSYS2's /tmp early so we can copy the setup script there
; before MSYS2 itself is installed.
Name: "{#Msys2Dir}\tmp"
; Ensure the projects directory exists inside the app folder
Name: "{app}\projects"

[Files]
; ── MSYS2 installer ──────────────────────────────────────────────────────────
; Rename your downloaded msys2-x86_64-YYYYMMDD.exe to msys2-installer.exe
Source: "msys2-installer.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

; ── Package setup script ─────────────────────────────────────────────────────
; Copied to MSYS2's /tmp so bash can reach it as /tmp/re-setup.sh
Source: "setup-packages.sh"; DestDir: "{#Msys2Dir}\tmp"; \
  DestName: "re-setup.sh"; Flags: ignoreversion

; ── RE application source ────────────────────────────────────────────────────
Source: "..\src\*";    DestDir: "{app}\src";    Flags: ignoreversion recursesubdirs
Source: "..\REwww\*";  DestDir: "{app}\REwww";  Flags: ignoreversion recursesubdirs
Source: "..\styles\*"; DestDir: "{app}\styles"; Flags: ignoreversion recursesubdirs
Source: "..\projects\README.md"; DestDir: "{app}\projects"; Flags: ignoreversion

; ── Default projects.toml ────────────────────────────────────────────────────
; onlyifdoesntexist: user edits are preserved across upgrades
Source: "projects.toml.default"; DestDir: "{app}"; DestName: "projects.toml"; \
  Flags: onlyifdoesntexist

[Run]
; ── Step 1: Install MSYS2 (skipped if already at C:\msys64) ──────────────────
; MSYS2 uses NSIS: /S = silent, /D= must be last and unquoted.
Filename: "{tmp}\msys2-installer.exe"; \
  Parameters: "/S /D={#Msys2Dir}"; \
  Flags: waituntilterminated; \
  StatusMsg: "Installing MSYS2..."; \
  Check: ShouldInstallMsys2

; ── Step 2: Install all packages (pacman + pip) ───────────────────────────────
; bash --login sources the MSYS2 profile so PATH is correct inside the script.
Filename: "{#Msys2Dir}\usr\bin\bash.exe"; \
  Parameters: "--login -c ""bash /tmp/re-setup.sh >> /tmp/re-setup.log 2>&1"""; \
  Flags: waituntilterminated runhidden; \
  StatusMsg: "Installing GTK and Python packages — this may take a few minutes..."

[Icons]
; Start Menu
Name: "{group}\{#AppName} — Web Interface"; \
  Filename: "{app}\start-REwww.bat"
Name: "{group}\{#AppName} — Desktop App (GTK)"; \
  Filename: "{app}\start-REgtk.bat"
Name: "{group}\{#AppName} — Command Line"; \
  Filename: "{app}\REcli.bat"
Name: "{group}\Uninstall {#AppName}"; \
  Filename: "{uninstallexe}"

; Desktop shortcut for the web interface
Name: "{commondesktop}\{#AppName}"; \
  Filename: "{app}\start-REwww.bat"

[UninstallDelete]
; Remove the generated launcher scripts on uninstall
Type: files; Name: "{app}\start-REwww.bat"
Type: files; Name: "{app}\start-REgtk.bat"
Type: files; Name: "{app}\REcli.bat"

[Code]

{ ── Helpers ────────────────────────────────────────────────────────────────── }

function ShouldInstallMsys2: Boolean;
begin
  Result := not FileExists(ExpandConstant('{#Msys2Dir}\usr\bin\bash.exe'));
end;


{ ── Launcher creation ────────────────────────────────────────────────────────
  Launchers are written by Pascal code rather than bundled as static files
  so they always contain the correct {app} path even if the user changed it
  from the default C:\RE2.
}
procedure CreateLaunchers;
var
  AppDir:   String;
  Python:   String;
  PathLine: String;
  Content:  String;
begin
  AppDir   := ExpandConstant('{app}');
  Python   := '{#Msys2Python}';
  PathLine := 'set PATH={#Msys2Dir}\ucrt64\bin;{#Msys2Dir}\usr\bin;%PATH%';

  { ── start-REwww.bat ──────────────────────────────────────────────────────
    Starts the Flask server and opens the browser.
    The browser may open slightly before Flask is ready; that is normal —
    the page will load once Flask finishes starting up.
  }
  Content :=
    '@echo off'                                              + #13#10 +
    PathLine                                                 + #13#10 +
    'cd /d "' + AppDir + '"'                                + #13#10 +
    'start "" http://localhost:3001'                         + #13#10 +
    '"' + Python + '" "' + AppDir + '\REwww\app.py"'       + #13#10;
  SaveStringToFile(AppDir + '\start-REwww.bat', Content, False);

  { ── start-REgtk.bat ─────────────────────────────────────────────────────── }
  Content :=
    '@echo off'                                              + #13#10 +
    PathLine                                                 + #13#10 +
    'cd /d "' + AppDir + '"'                                + #13#10 +
    '"' + Python + '" "' + AppDir + '\src\REgtk.py"'       + #13#10;
  SaveStringToFile(AppDir + '\start-REgtk.bat', Content, False);

  { ── REcli.bat ────────────────────────────────────────────────────────────── }
  Content :=
    '@echo off'                                              + #13#10 +
    PathLine                                                 + #13#10 +
    'cd /d "' + AppDir + '"'                                + #13#10 +
    '"' + Python + '" "' + AppDir + '\src\REcli.py" %*'    + #13#10;
  SaveStringToFile(AppDir + '\REcli.bat', Content, False);
end;


{ ── Called by Inno Setup after all files are installed ───────────────────── }
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
    CreateLaunchers;
end;
