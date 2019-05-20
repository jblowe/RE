set -x

pwd

python3 REcli.py TGTM --mel hand --mel2 none
[ $? -ne 0 ] && exit 1;
echo 'No mel to gold stats'
head ..data/TGTM/TGTM.default.analysis.txt

python3 REcli.py TGTM --mel hand --mel2 wordnet
[ $? -ne 0 ] && exit 1;
echo 'WordNet to gold stats'
head ..data/TGTM/TGTM.default.analysis.txt

python3 REcli.py TGTM --mel hand --mel2 wordnet-pairs
[ $? -ne 0 ] && exit 1;
echo 'WordNet pairs to gold stats'
head ..data/TGTM/TGTM.default.analysis.txt

python3 REcli.py TGTM --mel hand --mel2 clics
[ $? -ne 0 ] && exit 1;
echo 'Clics to gold stats'
head ..data/TGTM/TGTM.default.analysis.txt
