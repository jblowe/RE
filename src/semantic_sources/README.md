# WordNet > MEL setup
You'll need to install NLTK:

pip3 install nltk

also, you'll need to install the associated WordNet files:

http://www.nltk.org/howto/wordnet.html

`cd src
python semantic_sources/regenerate-wordnet.py`

http://www.nltk.org/howto/wordnet.html

# CLICS > MEL setup

Install the datasets:

`pip install -r pip-requirements.txt`

You'll need to clone these repositories in some directory X:

* https://github.com/clics/clics2
* https://github.com/clld/concepticon-data
* https://github.com/clld/glottolog

Then:

* cd to the X directory.
* cd to each directory and run: `pip install -e`, making sure you checkout the correct branch of each.
* `load` the concepticon and glottolog resources.
* calculate the colexification networks: (takes a while) `clics -t 3 -f families colexification`
* make sure you have the lexical data files in the source directories!
* then regenerate the CLICS MELS. `python3 semantic_sources/regenerate-clics.py X`.

Possible dialog for this:

```
cd semantic_sources/

git clone https://github.com/clics/clics2
git clone https://github.com/clld/concepticon-data
git clone https://github.com/clld/glottolog

cd clics2
pip install -e .
cd ../concepticon-data
git checkout v1.2.0
pip install -e .
cd ../glottolog
git checkout 9701cb0
pip install -e .

cd ../clics2
clics load ~/RE/src/semantic_sources/concepticon-data ~/RE/src/semantic_sources/glottolog
clics -t 3 -f families colexification

cd ../..
python REcli.py upstream HMONGMIEN semantics -t standard -r hand-std-strict -m hand -w
for t in DIS TGTM VANUATU HMONGMIEN POLYNESIAN ROMANCE; do cp ../experiments/$t/semantics/*.data.xml ../projects/$t/ ; done

python semantic_sources/regenerate-clics.py /Users/jblowe/RE2/src/semantic_sources/clics2
git clean -fd ../projects/*/*.data.xml
```

# "Not founds"

Both scripts add the glosses that were not present in the semantic source as "not found", "singleton"
MELs in their respective MEL files.

