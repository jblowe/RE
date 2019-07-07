# WordNet > MEL setup
You'll need to install NLTK:

pip3 install nltk

also, you'll need to install the associated WordNet files:

http://www.nltk.org/howto/wordnet.html

`python3 ../all_glosses.py TGTM | python3 wnlookup.py > output.mel`

http://www.nltk.org/howto/wordnet.html

# CLICS > MEL setup

Install the datasets:

`pip install -r pip-requirements.txt`

you'll need to clone these repositories in some directory X:
https://github.com/clics/clics2
https://github.com/clld/concepticon-data
https://github.com/clld/glottolog

and for each directory run: `pip install -e`.

Now calculate the colexification networks: (takes a while)

`clics -t 3 -f families colexification`

(You may change the parameters to get different data, but you must also change the name of the file in the script.)

Finally, to produce the mel, do:

`python3 ../all_glosses.py TGTM | python3 clics.py X > output.mel`

# Both

Both scripts should output a file not_found, which contains glosses that were not present in the semantic source.