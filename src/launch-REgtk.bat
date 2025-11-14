@echo off
setlocal
set "MSYS2=C:\msys64"
REM Clean Windows baseline:
set "PATH=%SystemRoot%\System32;%SystemRoot%;%SystemRoot%\System32\Wbem"
REM Add ONLY UCRT64:
set "PATH=c:\msys64\ucrt64\bin;%PATH%"
set GDK_BACKEND=win32
"c:\msys64\ucrt64\bin\python.exe" "c:\Martine\RE\src\REgtk.py"
