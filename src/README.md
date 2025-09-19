## The Reconstruction Engine

#### Being another version of the Reconstruction Engine, in Python

_NB: this is a work in progress!!_

The current ``REcli`` ("reconstruction engine command line interface") script implements the "Upstream" reconstruction function
based on the input lexicons.

Currently it works with the corpora in the 
```VANUATU```, ```ROMANCE```, ```DEMO93``` and ```TGTM``` 'projects'.

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
# create a new experiment for DEMO93
python3 REcli.py new-experiment DEMO93 mydemo
# create cognate sets using the 'standard' correspondence and the 'hand' (handmade) semantics
python3 REcli.py DEMO93 mydemo --recon standard --mel hand --run funstuff
# look at the results
less ../experiments/DEMO93/mydemo/DEMO93.funstuff.sets.txt
```

* commands are:

| command           | description                                                |
|-------------------|------------------------------------------------------------|
| upstream          | Compute cognate sets, i.e. “upstream” in the sense of time |
| compare, diff     | Compare or diff two upstream 'runs'                        |
| coverage          | Compute coverages of glosses and MELs                      |
| new-experiment    | Create a new experiment                                    |
| delete-experiment | Delete an experiemnt                                       |
| analyze-glosses   | Analyze glosses in a dataset                               |

* you can get the parameters for the commands by ``python REcli.py command --help``

#### Notes
* Notation for contexts in the Table of Correspondences
When specifying contexts, the # sign defines the end of a word, while $ specifies the beginning of a word. None means everything matches.

#### Interactive version using GTK
You must have PyGObject and GTK installed.

* Install GTK (ymmv!), probably in a venv
* Start it up with your desired parameters
```bash
# must run from the src directory
cd .../src
python REgtk.py
```
NB
* The GTK application modifies the project directory directly. An
  interface for sandboxing different input states and comparing the
  inputs and outputs is planned!
