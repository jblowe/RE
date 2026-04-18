' run-bash.vbs
' Launches an MSYS2 bash --login command with CREATE_NO_WINDOW so no console
' window appears, then waits for it to complete.
'
' Usage (from Inno Setup [Run]):
'   wscript.exe //B //Nologo "path\to\run-bash.vbs" "bash-command-here"
'
' The single argument is passed verbatim as the -c script to bash.

Dim sh, bash, cmd
bash = "C:\msys64\usr\bin\bash.exe"
Set sh = CreateObject("WScript.Shell")
cmd = """" & bash & """ --login -c """ & WScript.Arguments(0) & """"
WScript.Quit sh.Run(cmd, 0, True)
