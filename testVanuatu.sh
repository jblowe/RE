set -x

DATE=`date +%Y-%m-%d-%H-%M`

pwd

git submodule update --init --recursive

time python3 REcli.py VANUATU --mel clics --mel2 none

echo 'Comparing CLICS to No-MEL stats...'
head ../projects/VANUATU/VANUATU.default.analysis.txt

time python3 REcli.py VANUATU --mel hand  > ../projects/VANUATU/VANUATU.${DATE}.statistics.txt
cat ../projects/VANUATU/VANUATU.${DATE}.statistics.txt
