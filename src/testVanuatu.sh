set -x

pwd

git submodule update --init --recursive

time python3 REcli.py VANUATU --mel none --mel2 clics
echo 'No mel to gold stats'
head ../projects/VANUATU/VANUATU.default.analysis.txt
