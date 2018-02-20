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
cd RE8.2
python upstream.py DEMO93
less ../RE7/DATA/DEMO93/DEMO93.default.sets.txt
```

**Dependencies**

requires Python 3

Modules:

* ```xml.etree.ElementTree``` (should be standard)
* ```regex``` installabled via something like ```pip3 install regex``` 
