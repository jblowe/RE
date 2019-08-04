set -x

DATE=`date +%Y-%m-%d-%H-%M`

pwd
# first make sets
#time python3 REcli.py --run tree -t tree ROMANCE semantics > ../experiments/ROMANCE/semantics/ROMANCE.${DATE}.tree.statistics.txt
#[ $? -ne 0 ] && exit 1;
#cat ../experiments/ROMANCE/semantics/ROMANCE.${DATE}.tree.statistics.txt

# second make strict sets
time python3 REcli.py run ROMANCE semantics -w --run tree-strict -t tree > ../experiments/ROMANCE/semantics/ROMANCE.${DATE}.tree.statistics.txt
[ $? -ne 0 ] && exit 1;
cat ../experiments/ROMANCE/semantics/ROMANCE.${DATE}.tree.statistics.txt

# coverage
python3 REcli.py coverage ROMANCE semantics hand > ../experiments/ROMANCE/semantics/ROMANCE.mel.coverage.txt

# compare results of all runs
#python3 REcli.py compare ROMANCE semantics

exit 1
