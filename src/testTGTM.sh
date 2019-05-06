set -x

DATE=`date +%Y-%m-%d-%H-%M`

pwd
# only create "best sets" (i.e. using mel)
DATE=`date +%Y-%m-%d-%H-%M`
time python3 REcli.py TGTM --mel hand > ../projects/TGTM/TGTM.${DATE}.${DATE}.statistics.txt
cat ../projects/TGTM/TGTM.${DATE}.${DATE}.statistics.txt

