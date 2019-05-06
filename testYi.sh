set -x

DATE=`date +%Y-%m-%d-%H-%M`

# do the comparison of MEL with no-mel
time python3 REcli.py NYI --mel hand --mel2 none
head ../projects/LOLOISH/NYI.default.analysis.txt
time python3 REcli.py SYI --mel hand --mel2 none
head ../projects/LOLOISH/SYI.default.analysis.txt

# make the "standard" sets -- with the MEL
time python3 REcli.py NYI --mel hand  > ../projects/LOLOISH/NYI.${DATE}.statistics.txt
cat ../projects/LOLOISH/NYI.${DATE}.statistics.txt

time python3 REcli.py SYI --mel hand  > ../projects/LOLOISH/SYI.${DATE}.statistics.txt
cat ../projects/LOLOISH/SYI.${DATE}.statistics.txt


