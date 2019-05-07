set -x

DATE=`date +%Y-%m-%d-%H-%M`

pwd
# only create "best sets" (i.e. using mel)
time python3 REcli.py TGTM --mel hand > ../projects/TGTM/TGTM.${DATE}.statistics.txt
cat ../projects/TGTM/TGTM.${DATE}.statistics.txt

