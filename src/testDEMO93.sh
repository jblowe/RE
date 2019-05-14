set -x

DATE=`date +%Y-%m-%d-%H-%M`

pwd
# first make sets
time python3 REcli.py DEMO93 -r hand --mel hand > ../projects/DEMO93/DEMO93.${DATE}.statistics.txt
cat ../projects/DEMO93/DEMO93.${DATE}.statistics.txt

# second test mel comparison
time python3 REcli.py DEMO93 --mel hand --mel2 none
echo 'Comparing Gold to No-MEL stats...'
head ../projects/DEMO93/DEMO93.default.analysis.txt


