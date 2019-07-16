set -x

DATE=`date +%Y-%m-%d-%H-%M`

pwd
# first make sets
#time python3 REcli.py --run tree -t tree ROMANCE/experiments/semantics > ../projects/ROMANCE/experiments/semantics/ROMANCE.${DATE}.tree.statistics.txt
#[ $? -ne 0 ] && exit 1;
#cat ../projects/ROMANCE/experiments/semantics/ROMANCE.${DATE}.tree.statistics.txt

# second make strict sets
time python3 REcli.py -w --run tree-strict -t tree ROMANCE/experiments/semantics > ../projects/ROMANCE/experiments/semantics/ROMANCE.${DATE}.tree.statistics.txt
[ $? -ne 0 ] && exit 1;
cat ../projects/ROMANCE/experiments/semantics/ROMANCE.${DATE}.tree.statistics.txt

# coverage
python3 REcli.py -c -m hand ROMANCE/experiments/semantics > ../projects/ROMANCE/experiments/semantics/ROMANCE.mel.coverage.txt

# compare results of all runs
python3 REcli.py -x -- ROMANCE/experiments/semantics

exit 1
