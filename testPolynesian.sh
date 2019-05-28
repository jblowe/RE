set -x

DATE=`date +%Y-%m-%d-%H-%M`

XPWD=`pwd`
# run the pipeline first to set up the data
cd ../projects/POLYNESIAN; ./polynesian_pipeline.sh 

# make the "standard" sets -- with the MEL

cd $XPWD
time python3 REcli.py POLYNESIAN --run hand --mel hand > ../projects/POLYNESIAN/POLYNESIAN.${DATE}.statistics.txt
[ $? -ne 0 ] && exit 1;
cat ../projects/POLYNESIAN/POLYNESIAN.${DATE}.hand.statistics.txt
