set -x

pwd

python3 REcli.py TGTM --mel hand --mel2 none
echo 'No mel to gold stats'
head ../RE7/DATA/TGTM/TGTM.default.analysis.txt

