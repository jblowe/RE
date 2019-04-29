set -x

pwd
time python3 REcli.py TGTM --mel hand
echo 'Comparing No-MEL to gold stats'
head ../projects/TGTM/TGTM.default.analysis.txt


