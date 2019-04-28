set -x

pwd

time python3 REcli.py TGTM --mel hand --mel2 none
echo 'No mel to gold stats'
head ../projects/TGTM/TGTM.default.analysis.txt

