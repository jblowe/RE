where python
# Expect: C:\msys64\ucrt64\bin\python.exe

python - <<'PY'
import sys, gi
print("Python exe:", sys.executable)
print("sys.path[0]:", sys.path[0])
import ctypes, os
print("PATH starts with:", os.environ["PATH"].split(";")[:3])
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
print("GTK ok:", Gtk.get_major_version())
PY
