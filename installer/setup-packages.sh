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
  mingw-w64-ucrt-x86_64-python-tomli-w

echo "=== Done ==="
