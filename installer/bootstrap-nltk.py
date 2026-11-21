"""
Install NLTK and download corpora inside MSYS2 UCRT64 Python from an elevated
Windows installer context.

Python 3.8+ calls SetDefaultDllDirectories(LOAD_LIBRARY_SEARCH_DEFAULT_DIRS)
early in startup, restricting DLL loading to only system directories plus those
registered with AddDllDirectory().  Under an elevated installer process,
C:\\msys64\\ucrt64\\bin may not be registered, so C-extension .pyd files
(including binascii) cannot find their runtime DLL dependencies.

The os/nt module is compiled INTO the Python interpreter itself (not a .pyd),
so os.add_dll_directory() works immediately without loading any extension.
Registering the UCRT64 bin directory here lets all subsequent .pyd imports
resolve their dependencies (e.g. libwinpthread-1.dll, libgcc_s_seh-1.dll).

We run pip in-process via runpy rather than spawning a subprocess because a
child process does not inherit the AddDllDirectory cookie.
"""
import os
import sys

_UCRT64_BIN = r"C:\msys64\ucrt64\bin"

if hasattr(os, "add_dll_directory"):
    _cookie = os.add_dll_directory(_UCRT64_BIN)

# --- Install NLTK --------------------------------------------------------
import runpy

sys.argv = ["pip", "install", "nltk"]
try:
    runpy.run_module("pip", run_name="__main__", alter_sys=True)
except SystemExit as e:
    if e.code not in (0, None):
        print(f"pip install failed: exit code {e.code}", file=sys.stderr, flush=True)
        sys.exit(int(e.code))

# --- Download corpora ----------------------------------------------------
import nltk

for corpus in ["stopwords", "wordnet", "omw-1.4"]:
    print(f"[nltk] downloading {corpus}...", flush=True)
    nltk.download(corpus, quiet=False)
