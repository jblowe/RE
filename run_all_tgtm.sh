set -x

pwd

python3 REcli.py TGTM --mel hand --mel2 none
echo 'No mel to gold stats'
head ..data/TGTM/TGTM.default.analysis.txt

python3 REcli.py TGTM --mel hand --mel2 wordnet
echo 'WordNet to gold stats'
head ..data/TGTM/TGTM.default.analysis.txt

python3 REcli.py TGTM --mel hand --mel2 wordnet-pairs
echo 'WordNet pairs to gold stats'
head ..data/TGTM/TGTM.default.analysis.txt

python3 REcli.py TGTM --mel hand --mel2 clics
echo 'Clics to gold stats'
head ..data/TGTM/TGTM.default.analysis.txt
