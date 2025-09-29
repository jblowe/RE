@echo off
"C:\msys64\msys2_shell.cmd" -mingw64 -here -c ^
  "cd c:/RE/src && source venv-gtk3/bin/activate && cd c:/RE/REwww && python app.py"

