set -x

time python3 REcli.py NYI --mel hand --mel2 none
head ../projects/LOLOISH/NYI.default.analysis.txt
time python3 REcli.py SYI --mel hand --mel2 none
head ../projects/LOLOISH/SYI.default.analysis.txt

