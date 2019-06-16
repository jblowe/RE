set -x

DATE=`date +%Y-%m-%d-%H-%M`

pwd
# only create "best sets" (i.e. using mel)
time python3 REcli.py TGTM -r hand --mel hand > ../projects/TGTM/TGTM.${DATE}.statistics.txt
[ $? -ne 0 ] && exit 1;
cat ../projects/TGTM/TGTM.${DATE}.statistics.txt
