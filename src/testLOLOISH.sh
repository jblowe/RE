set -x

DATE=`date +%Y-%m-%d-%H-%M`

XPWD=`pwd`
# run the pipeline first to set up the data
cd ../projects/LOLOISH/
cp * experiments/semantics
cd experiments/semantics; ./pipeline.sh
[ $? -ne 0 ] && exit 1;

# make the "standard" sets -- with the MEL

cd $XPWD

# generate the strict sets
time python3 REcli.py NYI/experiments/semantics -w --run hand-strict --mel hand
time python3 REcli.py SYI/experiments/semantics -w --run hand-strict --mel hand

# do the comparison of MEL with no-mel
time python3 REcli.py NYI/experiments/semantics --mel hand --mel2 none
[ $? -ne 0 ] && exit 1;
echo 'Comparing Gold to No-MEL stats...'
head ../projects/LOLOISH/experiments/semantics/NYI.default.analysis.txt
echo 'Comparing Gold to No-MEL stats...'
time python3 REcli.py SYI/experiments/semantics --mel hand --mel2 none
[ $? -ne 0 ] && exit 1;
head ../projects/LOLOISH/experiments/semantics/SYI.default.analysis.txt

# make the "standard" sets -- with the MEL
time python3 REcli.py NYI/experiments/semantics -r hand --mel hand  > ../projects/LOLOISH/experiments/semantics/NYI.${DATE}.statistics.txt
[ $? -ne 0 ] && exit 1;
cat ../projects/LOLOISH/experiments/semantics/NYI.${DATE}.statistics.txt

time python3 REcli.py SYI/experiments/semantics -r hand --mel hand  > ../projects/LOLOISH/experiments/semantics/SYI.${DATE}.statistics.txt
[ $? -ne 0 ] && exit 1;
cat ../projects/LOLOISH/experiments/semantics/SYI.${DATE}.statistics.txt

# coverage
python3 REcli.py -c -m hand SYI/experiments/semantics > ../projects/SYI/SYI.mel.coverage.txt
python3 REcli.py -c -m hand NYI/experiments/semantics > ../projects/NYI/NYI.mel.coverage.txt

# compare
python3 REcli.py -x -- SYI/experiments/semantics
python3 REcli.py -x -- NYI/experiments/semantics

exit 1