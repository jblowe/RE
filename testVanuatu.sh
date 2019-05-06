set -x

DATE=`date +%Y-%m-%d-%H-%M`

pwd

git submodule update --init --recursive

time python3 REcli.py VANUATU --mel none --mel2 clics

echo 'Comparing No-MEL to gold stats'
head ../projects/VANUATU/VANUATU.default.analysis.txt

time python3 REcli.py VANUATU --mel hand  > ../projects/VANUATU/VANUATU.${DATE}.statistics.txt
cat ../projects/VANUATU/VANUATU.${DATE}.statistics.txt
