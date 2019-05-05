set -x

XPWD=`pwd`
# run the pipeline first to set up the data
cd ../projects/POLYNESIAN; ./polynesian_pipeline.sh 

# make the "standard" sets -- with the MEL

cd $XPWD
time python3 REcli.py POLYNESIAN --mel hand

