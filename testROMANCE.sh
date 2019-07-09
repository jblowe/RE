set -x

DATE=`date +%Y-%m-%d-%H-%M`

pwd
# first make sets
#time python3 REcli.py --run tree -t tree ROMANCE > ../projects/ROMANCE/ROMANCE.${DATE}.tree.statistics.txt
#[ $? -ne 0 ] && exit 1;
#cat ../projects/ROMANCE/ROMANCE.${DATE}.tree.statistics.txt

# second make strict sets
time python3 REcli.py -w --run tree-strict -t tree ROMANCE > ../projects/ROMANCE/ROMANCE.${DATE}.tree.statistics.txt
[ $? -ne 0 ] && exit 1;
cat ../projects/ROMANCE/ROMANCE.${DATE}.tree.statistics.txt

# coverage
python3 REcli.py -c -m hand ROMANCE > ../projects/ROMANCE/ROMANCE.mel.coverage.txt

# compare results of all runs
python3 REcli.py -x -- ROMANCE

exit 1
