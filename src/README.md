RE in Python

**Being another version of the Reconstruction Engine, in Python**

NB: this is a work in progress!!

The current ```REcli`` ("reconstruction engine command line interface") script implements the "Upstream" reconstruction function
based on the input lexicons.

Currently it works with the corpora in ```VANUATU```, ``ROMANCE```, ```DEMO93``` and ```TGTM```.

**Dependencies**

requires Python 3

Modules:

* ```lxml``` ```pip3 install lxml```
* ```regex``` installable via something like ```pip3 install regex```

or

```pip3 install -r requirements.txt```


**Usage**

To run:

* Clone or fork this repo
* ```cd``` to the ```src``` directory
* Run the scripts, see the results in the ```projects``` directory.

e.g.

```bash
git clone https://github.com/jblowe/RE.git
cd RE/src
python3 REcli.py DEMO93
less ../projects/DEMO93/DEMO93.default.sets.txt
```

**Notes**
* Notation for contexts
When specifying contexts, the # sign defines the end of a word, while $ specifies the beginning of a word. None means everything matches.

**Using the graphical interface**
You must have PyGObject and GTK installed.

To work on the table of correspondences, save before clicking on batch
upstream to update the results.
