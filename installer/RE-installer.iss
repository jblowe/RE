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
#define AppVersion   "2.0"
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

; ── Project pipeline runner ───────────────────────────────────────────────────
; Copied to MSYS2's /tmp so bash can reach it as /tmp/run-pipelines.sh
Source: "run-pipelines.sh"; DestDir: "{#Msys2Dir}\tmp"; \
  DestName: "run-pipelines.sh"; Flags: ignoreversion

; ── Hidden-bash trampoline ────────────────────────────────────────────────────
; WScript.Shell.Run with style=0 passes CREATE_NO_WINDOW to CreateProcess,
; which prevents MSYS2/Cygwin from allocating a visible console window.
; Inno Setup's own runhidden flag only sets SW_HIDE, which MSYS2 overrides.
Source: "run-bash.vbs"; DestDir: "{#Msys2Dir}\tmp"; \
  DestName: "run-bash.vbs"; Flags: ignoreversion

; ── RE application source ────────────────────────────────────────────────────
Source: "..\src\*";    DestDir: "{app}\src";    Flags: ignoreversion recursesubdirs
Source: "..\REwww\*";  DestDir: "{app}\REwww";  Flags: ignoreversion recursesubdirs
Source: "..\styles\*"; DestDir: "{app}\styles"; Flags: ignoreversion recursesubdirs

; ── Bundled example projects ─────────────────────────────────────────────────
; Timestamped run outputs (NAME.YYYYMMDD-HHMMSS.*) and compiled Python files
; are excluded; everything else (data, correspondences, reference runs) is included.
Source: "..\projects\DIS\*";        DestDir: "{app}\projects\DIS";        Flags: ignoreversion recursesubdirs; Excludes: "*.????????-??????.*,*.pyc"
Source: "..\projects\HMONGMIEN\*"; DestDir: "{app}\projects\HMONGMIEN"; Flags: ignoreversion recursesubdirs; Excludes: "*.????????-??????.*,*.pyc"
Source: "..\projects\LOLOISH\*";   DestDir: "{app}\projects\LOLOISH";   Flags: ignoreversion recursesubdirs; Excludes: "*.????????-??????.*,*.pyc"
Source: "..\projects\POLYNESIAN\*"; DestDir: "{app}\projects\POLYNESIAN"; Flags: ignoreversion recursesubdirs; Excludes: "*.????????-??????.*,*.pyc"
Source: "..\projects\ROMANCE\*";   DestDir: "{app}\projects\ROMANCE";   Flags: ignoreversion recursesubdirs; Excludes: "*.????????-??????.*,*.pyc"
Source: "..\projects\SLAVIC\*";    DestDir: "{app}\projects\SLAVIC";    Flags: ignoreversion recursesubdirs; Excludes: "*.????????-??????.*,*.pyc"

; ── Default projects.toml ────────────────────────────────────────────────────
; onlyifdoesntexist preserves any edits the user has made on upgrade.
; Paths inside the file are relative so they work for any install directory.
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
; Routed through run-bash.vbs so WScript.Shell.Run passes CREATE_NO_WINDOW to
; bash, preventing the empty MSYS2 console window that SW_HIDE/runhidden alone
; cannot suppress for Cygwin-family binaries.
; wscript.exe is a GUI app so Inno Setup never shows a window for it.
Filename: "wscript.exe"; \
  Parameters: "//B //Nologo ""{#Msys2Dir}\tmp\run-bash.vbs"" ""bash /tmp/re-setup.sh >> /tmp/re-setup.log 2>&1"""; \
  Flags: waituntilterminated; \
  StatusMsg: "Installing GTK and Python packages — this may take a few minutes..."

; ── Step 3: Run project data pipelines ────────────────────────────────────────
; Prepares DIS, HMONGMIEN, and POLYNESIAN example data.
; The Windows app path is passed via single quotes so cygpath can convert it.
Filename: "wscript.exe"; \
  Parameters: "//B //Nologo ""{#Msys2Dir}\tmp\run-bash.vbs"" ""bash /tmp/run-pipelines.sh '{app}' >> /tmp/pipelines.log 2>&1"""; \
  Flags: waituntilterminated; \
  StatusMsg: "Preparing example project data..."

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

; Desktop shortcuts
Name: "{commondesktop}\REwww"; Filename: "{app}\start-REwww.bat"
Name: "{commondesktop}\REgtk"; Filename: "{app}\start-REgtk.bat"

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


// ── Launcher creation ────────────────────────────────────────────────────────
// Launchers are written by Pascal code rather than bundled as static files
// so they always contain the correct install path even if the user changed
// the default destination directory.
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
