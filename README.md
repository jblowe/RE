## RE

[![build status](https://travis-ci.com/jblowe/RE.svg?branch=master)](https://travis-ci.com/jblowe/RE)

The Reconstruction Engine, a computer implementation of the comparative method

This repository contains code and data files supporting the "Reconstruction Engine" project.

RE has been written now in 4 languages (SPITBOL, PERL, Java, and now Python).
The "legacy" PERL version is included here ([legacy/RE7](../tree/master/legacy/RE7)) and may still work.

However, the modern version has three components:

* The 'core system' (in `src`) which includes Python modules to diachronically process the various language files (in `projects').
* The 'desktop version', a [gTK](https://www.gtk.org/) graphical interface, currently a work in progress. see `src/REgtk.py`)
* The 'web interface', a bottle+bootstrap interface to allow users to browse the projects and results, either locally or on the web. see `REwww`

The directories of interest are:

#### main components

projects - "the data" -- various sets of language files, tables of correspondences, etc.
src - source code for everything except the web interface
REwww - source code for the bottle+bootstrap web interface
docs - documentation, very much a work in progress
make / Makefile - we use this for testing and QA

#### web interface components

styles - XSLT stylesheets
css
images
js

#### past code and other goodies

other_stuff

### python needs

requirements.txt

See individual directories for instructions on installation and operation.
