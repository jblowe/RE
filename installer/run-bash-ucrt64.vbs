' run-bash-ucrt64.vbs
' Like run-bash.vbs but sets MSYSTEM=UCRT64 before launching bash --login,
' so the profile configures the full UCRT64 environment (PATH, DLL search path,
' etc.) automatically.  Use this for any step that invokes UCRT64 Python.
'
' Usage (from Inno Setup [Run]):
'   wscript.exe //B //Nologo "path\to\run-bash-ucrt64.vbs" "bash-command-here"

Dim sh, bash, cmd
bash = "C:\msys64\usr\bin\bash.exe"
Set sh = CreateObject("WScript.Shell")
sh.Environment("Process")("MSYSTEM") = "UCRT64"
cmd = """" & bash & """ --login -c """ & WScript.Arguments(0) & """"
WScript.Quit sh.Run(cmd, 0, True)
