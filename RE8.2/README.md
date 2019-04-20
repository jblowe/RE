RE8.2

**Being another version of the Reconstruction Engine, in Python**

NB: this is a work in progress!!

The current script implement the "Upstream" reconstruction function
based on the input lexicons.

Currently it works with the XML corpora ```DEMO93``` and ```TGTM```.

To run:

* Clone or fork this repo
* ```cd``` to the RE8.2 directory
* Run the script, see the results in the ```DATA``` directory.

e.g.

```bash
git clone https://github.com/jblowe/RE.git
cd RE/RE8.2
python REcli.py DEMO93
less ../RE7/DATA/DEMO93/DEMO93.default.sets.txt
```

**Dependencies**

requires Python 3

Modules:

* ```xml.etree.ElementTree``` (should be standard)
* ```regex``` installable via something like ```pip3 install regex```

**Usage**
* Notation for contexts
When specifying contexts, the # sign defines the end of a word, while $ specifies the beginning of a word. None means everything matches.

**Using the graphical interface**
You must have PyGObject and GTK installed.

To work on the table of correspondences, save before clicking on batch
upstream to update the results.
