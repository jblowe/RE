set -x

DATE=`date +%Y-%m-%d-%H-%M`

XPWD=`pwd`
# run the pipeline first to set up the data
cd ../projects/LOLOISH; ./yi_pipeline.sh
[ $? -ne 0 ] && exit 1;

# make the "standard" sets -- with the MEL

cd $XPWD

# generate the strict sets
time python3 REcli.py NYI -w --run hand-strict --mel hand
time python3 REcli.py SYI -w --run hand-strict --mel hand

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
rm  ../projects/LOLOISH/NYI.${DATE}.statistics.txt

time python3 REcli.py SYI -r hand --mel hand  > ../projects/LOLOISH/SYI.${DATE}.statistics.txt
[ $? -ne 0 ] && exit 1;
cat ../projects/LOLOISH/SYI.${DATE}.statistics.txt
rm  ../projects/LOLOISH/SYI.${DATE}.statistics.txt

# coverage
python3 REcli.py -c -m hand SYI > ../projects/SYI/SYI.mel.coverage.txt
python3 REcli.py -c -m hand NYI > ../projects/NYI/NYI.mel.coverage.txt

# compare
python3 REcli.py -x -- SYI
python3 REcli.py -x -- NYI
