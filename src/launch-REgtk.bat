@echo off
setlocal EnableExtensions EnableDelayedExpansion

rem === customize these paths if needed ===
set "MSYS2=C:\msys64"
set "APPDIR=C:\RE\src"
set "VENV=%APPDIR%\venv-gtk3"

rem --- ensure GTK/GObject DLLs & typelibs are found ---
set "PATH=%MSYS2%\mingw64\bin;%PATH%"
set "GI_TYPELIB_PATH=%MSYS2%\mingw64\lib\girepository-1.0"
set "GSETTINGS_SCHEMA_DIR=%MSYS2%\mingw64\share\glib-2.0\schemas"
set "PYTHONIOENCODING=utf-8"

cd /d "%APPDIR%" || (echo [ERROR] Folder not found: %APPDIR% & pause & exit /b 1)

rem --- pick the venv's Python ---
if exist "%VENV%\Scripts\python.exe" (
  set "PY=%VENV%\Scripts\python.exe"
) else if exist "%VENV%\bin\python.exe" (
  set "PY=%VENV%\bin\python.exe"
) else (
  echo [ERROR] Could not find venv Python under "%VENV%".
  echo Recreate it from MINGW64 Python with:
  echo     python -m venv --system-site-packages venv-gtk3
  pause & exit /b 1
)

rem --- collect user arguments (everything after 'upstream') ---
if "%~1"=="" goto ASK
set "ARGS=%*"
goto RUN

:ASK
echo Enter parameters after "upstream"
echo   e.g. KIRANTI new --recon experiment1
set /p "ARGS=> "
echo.
goto RUN

:RUN
rem NOTE: quote any Windows paths with spaces, e.g. "C:\path with spaces\file.xml"
rem       to pass a literal &, write ^&   ; to pass ^, write ^^
"%PY%" REgtk.py upstream !ARGS!
set "RC=%ERRORLEVEL%"
if not "!RC!"=="0" (
  echo.
  echo [FAIL] REgtk exited with code !RC!.
  pause
)
endlocal & exit /b %RC%
