#!/usr/bin/env bash
# =============================================================================
# setup-packages.sh — run inside MSYS2 during Windows installation
# Installs all GTK, Python, and pip dependencies for the Reconstruction Engine.
# =============================================================================
set -e

echo "=== Synchronising MSYS2 package database ==="
pacman -Sy --noconfirm

echo "=== Installing GTK3, Python and core dependencies ==="
pacman -S --needed --noconfirm \
  mingw-w64-ucrt-x86_64-python \
  mingw-w64-ucrt-x86_64-perl \
  mingw-w64-ucrt-x86_64-gtk3 \
  mingw-w64-ucrt-x86_64-gobject-introspection \
  mingw-w64-ucrt-x86_64-python-gobject \
  mingw-w64-ucrt-x86_64-python-lxml \
  mingw-w64-ucrt-x86_64-python-matplotlib \
  mingw-w64-ucrt-x86_64-python-markupsafe \
  mingw-w64-ucrt-x86_64-python-regex \
  mingw-w64-ucrt-x86_64-python-flask \
  mingw-w64-ucrt-x86_64-python-pip \
  mingw-w64-ucrt-x86_64-python-tomli \
  mingw-w64-ucrt-x86_64-python-tomli-w \
  mingw-w64-ucrt-x86_64-zlib \
  mingw-w64-ucrt-x86_64-openssl

echo "=== Installing NLTK ==="
# Use the full path so this works regardless of MSYSTEM setting.
# Running Python from within bash uses MSYS2's process environment, which
# properly sets up DLL search paths for UCRT64 C-extension modules.
export PATH="/ucrt64/bin:/usr/bin:$PATH"
/ucrt64/bin/python -m pip install --break-system-packages nltk

echo "=== Downloading NLTK corpora ==="
/ucrt64/bin/python -m nltk.downloader stopwords wordnet omw-1.4

echo "=== Done ==="
