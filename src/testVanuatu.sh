set -x

pwd

git clone https://github.com/goodmami/toolbox.git
python3 REcli.py VANUATU --mel none --mel2 clics
echo 'No mel to gold stats'
head ../projects/VANUATU/VANUATU.default.analysis.txt
