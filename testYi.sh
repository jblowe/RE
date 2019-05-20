set -x

DATE=`date +%Y-%m-%d-%H-%M`

# do the comparison of MEL with no-mel
time python3 REcli.py NYI --mel hand --mel2 none
[ $? -ne 0 ] && exit 1;
echo 'Comparing Gold to No-MEL stats...'
head ../projects/LOLOISH/NYI.default.analysis.txt
echo 'Comparing Gold to No-MEL stats...'
time python3 REcli.py SYI --mel hand --mel2 none
[ $? -ne 0 ] && exit 1;
head ../projects/LOLOISH/SYI.default.analysis.txt

# make the "standard" sets -- with the MEL
time python3 REcli.py NYI -r hand --mel hand  > ../projects/LOLOISH/NYI.${DATE}.statistics.txt
[ $? -ne 0 ] && exit 1;
cat ../projects/LOLOISH/NYI.${DATE}.statistics.txt

time python3 REcli.py SYI -r hand --mel hand  > ../projects/LOLOISH/SYI.${DATE}.statistics.txt
[ $? -ne 0 ] && exit 1;
cat ../projects/LOLOISH/SYI.${DATE}.statistics.txt
