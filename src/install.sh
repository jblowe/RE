
# needed for REgtk and REwww
pacman -S --needed  --noconfirm \
  mingw-w64-ucrt-x86_64-python \
  mingw-w64-ucrt-x86_64-gtk3 \
  mingw-w64-ucrt-x86_64-gobject-introspection \
  mingw-w64-ucrt-x86_64-python-gobject \
  mingw-w64-ucrt-x86_64-python-lxml \
  mingw-w64-ucrt-x86_64-python-matplotlib \
  mingw-w64-ucrt-x86_64-python-bottle \
  mingw-w64-ucrt-x86_64-python-regex

# consider the following? as yet unverified, maybe all dependencies of the above?
# pacman -S --needed --noconfirm mingw-w64-urct-x86_64-gcc
# pacman -S --needed --noconfirm mingw-w64-urct-x86_64-glib2
# pacman -S --needed --noconfirm mingw-w64-urct-x86_64-gobject-introspection-runtime
# pacman -S --needed --noconfirm mingw-w64-urct-x86_64-libffi