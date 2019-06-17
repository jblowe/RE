set -x

DATE=`date +%Y-%m-%d-%H-%M`

XPWD=`pwd`
# run the pipeline first to set up the data
cd ../projects/DIS; ./dis_pipeline.sh

# make the "standard" sets -- with the MEL

cd $XPWD
time python3 REcli.py DIS -w --run hand-parsimonious --mel hand
time python3 REcli.py DIS    --run hand --mel hand --mel2 none
time python3 REcli.py DIS    --run hand --mel hand > ../projects/DIS/DIS.${DATE}.statistics.txt
[ $? -ne 0 ] && exit 1;
cat ../projects/DIS/DIS.${DATE}.hand.statistics.txt
rm  ../projects/DIS/DIS.${DATE}.hand.statistics.txt

# compare results of all runs
python3 REcli.py -x -- DIS