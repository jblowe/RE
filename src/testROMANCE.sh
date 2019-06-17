set -x

DATE=`date +%Y-%m-%d-%H-%M`

pwd
# first make sets
time python3 REcli.py --run tree -t tree ROMANCE > ../projects/ROMANCE/ROMANCE.${DATE}.tree.statistics.txt
[ $? -ne 0 ] && exit 1;
cat ../projects/ROMANCE/ROMANCE.${DATE}.tree.statistics.txt

# compare results of all runs
python3 REcli.py -x -- ROMANCE