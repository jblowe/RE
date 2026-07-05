## The Reconstruction Engine

#### Being another version of the Reconstruction Engine, in Python

_NB: this is a work in progress!!_

The current ``REcli`` ("reconstruction engine command line interface") script implements the "Upstream" reconstruction function
based on the input lexicons.

Currently it works with the corpora in the 
```VANUATU```, ```ROMANCE```, ```DIS``` and ```TGTM``` 'projects'.

#### Dependencies

Requires Python 3

Modules:

```pip3 install -r requirements.txt```

`mel.py` uses NLTK for gloss normalization (stopword removal and
phrasal-verb detection). `pip install` only gets the `nltk` package itself
— its corpora are a separate download:

```bash
python3 -m nltk.downloader stopwords wordnet omw-1.4
```

This downloads to `~/nltk_data` for whoever runs it. Under `mod_wsgi` (see
"Deploying under Apache/mod_wsgi" below), the daemon process may not
resolve `$HOME` the way an interactive shell does even when it runs as the
expected user, so the corpora can end up "installed" but unreachable.
Safest: download to a fixed path and point `NLTK_DATA` at that same path
explicitly, rather than relying on `$HOME`:

```bash
python3 -m nltk.downloader -d /path/to/nltk_data stopwords wordnet omw-1.4
```
```python
os.environ.setdefault('NLTK_DATA', '/path/to/nltk_data')  # before nltk is imported
```

#### Deploying under Apache/mod_wsgi

If `REwww` is served via `mod_wsgi` (`WSGIDaemonProcess ... user=someuser`),
that process is spawned by Apache and isn't guaranteed a full login
environment for `someuser`, even though it runs under that user's UID. Two
consequences seen in practice:

* Subprocesses the app shells out to (pipeline scripts, `xsltproc.py`, etc.)
  may not find the venv's `python3` unless `PATH` is set explicitly.
* NLTK's default `~/nltk_data` lookup can miss the corpora above for the
  same reason.

`REwww/app.wsgi` sets both explicitly near the top, before anything else is
imported:

```python
os.environ['PATH'] = '/path/to/venv/bin:' + os.environ.get('PATH', '/usr/local/bin:/usr/bin:/bin')
os.environ.setdefault('NLTK_DATA', '/path/to/nltk_data')
```

Adjust the paths for your deployment, then a full Apache restart (not just
a WSGI reload) is the safest way to pick up changes to `app.wsgi` or
installed packages.

### Usage

#### Command line interface 

To run using the command line interface (```REcli```)

* Clone or fork this repo
* ```cd``` to the ```src``` directory
* Run the scripts, see the results in the ```projects``` directory.

e.g.

```bash
git clone https://github.com/jblowe/RE.git
cd RE/src
# create cognate sets using the 'standard' correspondence and the 'hand' (handmade) semantics
python3 REcli.py DIS --recon standard --mel hand --run funstuff
# look at the results
less ../projects/DIS/DIS.funstuff.sets.txt
# create a new project MYPROJECT
python3 REcli.py new-project MYPROECT
```

* commands are:

| command         | description                                                |
|-----------------|------------------------------------------------------------|
| upstream        | Compute cognate sets, i.e. “upstream” in the sense of time |
| coverage        | Compute coverages of glosses and MELs                      |
| new-project     | Create a new project                                       |
| delete-project  | Delete a project                                           |
| analyze-glosses | Analyze glosses in a dataset                               |

* you can get the parameters for the commands by ``python REcli.py command --help``

#### Notes
* Notation for contexts in the Table of Correspondences
When specifying contexts, the # sign defines the end of a word, while $ specifies the beginning of a word. None means everything matches.

#### Interactive version using GTK
You must have PyGObject and GTK installed.
See e.g. `install.sh` to see what the dependencies are.

* Install GTK (ymmv!), probably in a venv
* Start it up with your desired parameters
```bash
# must run from the src directory
cd .../src
python REgtk.py
```
NB
* The GTK application may modify the project directory directly.
