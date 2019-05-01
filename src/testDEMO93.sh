set -x

pwd
# first make sets
time python3 REcli.py DEMO93 --mel hand
# second test mel comparison
time python3 REcli.py DEMO93 --mel hand --mel2 none
echo 'Comparing No-MEL to gold stats'
head ../projects/DEMO93/DEMO93.default.analysis.txt


