set -x

DATE=`date +%Y-%m-%d-%H-%M`

pwd

git submodule update --init --recursive

time python3 REcli.py coverage VANUATU semantics hand
[ $? -ne 0 ] && exit 1;

echo 'Comparing CLICS to No-MEL stats...'
head ../projects/VANUATU/VANUATU.default.analysis.txt

time python3 REcli.py upstream VANUATU -r hand --mel hand  > ../projects/VANUATU/VANUATU.${DATE}.hand.statistics.txt
[ $? -ne 0 ] && exit 1;
cat ../projects/VANUATU/VANUATU.${DATE}.hand.statistics.txt

time python3 REcli.py upsteam VANUATU -r hand --mel wordnet  > ../projects/VANUATU/VANUATU.${DATE}.wordnet.statistics.txt
[ $? -ne 0 ] && exit 1;
cat ../projects/VANUATU/VANUATU.${DATE}.hand.statistics.txt

time python3 REcli.py upstream VANUATU -w -r hand-strict --mel hand  > ../projects/VANUATU/VANUATU.${DATE}.hand-strict.statistics.txt
[ $? -ne 0 ] && exit 1;
cat ../projects/VANUATU/VANUATU.${DATE}.hand-strict.statistics.txt

# coverage
python3 REcli.py -c -m hand VANUATU > ../projects/VANUATU/VANUATU.mel.coverage.txt

# compare results of all runs
python3 REcli.py -x -- VANUATU
