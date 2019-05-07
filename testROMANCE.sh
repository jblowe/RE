set -x

DATE=`date +%Y-%m-%d-%H-%M`

pwd
# first make sets
time python3 REcli.py -t tree ROMANCE > ../projects/ROMANCE/ROMANCE.${DATE}.statistics.txt
cat ../projects/ROMANCE/ROMANCE.${DATE}.statistics.txt
