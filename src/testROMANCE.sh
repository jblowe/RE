set -x

DATE=`date +%Y-%m-%d-%H-%M`

pwd
# first make sets
time python3 REcli.py upstream ROMANCE semantics --run tree -t tree > ../experiments/ROMANCE/semantics/ROMANCE.${DATE}.tree.statistics.txt
[ $? -ne 0 ] && exit 0;
#cat ../experiments/ROMANCE/semantics/ROMANCE.${DATE}.tree.statistics.txt

# second make strict sets
time python3 REcli.py upstream ROMANCE semantics -w --run tree-strict -t tree > ../experiments/ROMANCE/semantics/ROMANCE.${DATE}.tree.statistics.txt
[ $? -ne 0 ] && exit 0;
cat ../experiments/ROMANCE/semantics/ROMANCE.${DATE}.tree.statistics.txt

# coverage
python3 REcli.py coverage ROMANCE semantics hand > ../experiments/ROMANCE/semantics/ROMANCE.mel.coverage.txt

# compare results of all runs
python3 REcli.py compare ROMANCE semantics -r1 tree-strict semantics -r2 tree > /dev/null

exit 0
