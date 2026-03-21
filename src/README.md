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
