set -x

DATE=`date +%Y-%m-%d-%H-%M`

XPWD=`pwd`
# run the pipeline first to set up the data
cd ../projects/POLYNESIAN; ./polynesian_pipeline.sh 

# make default sets, no mel
python3 REcli.py POLYNESIAN > ../projects/POLYNESIAN/POLYNESIAN.default.txt

# make the "standard" sets -- with the MEL

cd $XPWD
python3 REcli.py POLYNESIAN -w --run hand-parsimonious --mel hand > ../projects/POLYNESIAN/POLYNESIAN.${DATE}.statistics.txt
python3 REcli.py POLYNESIAN --run hand --mel hand > ../projects/POLYNESIAN/POLYNESIAN.${DATE}.statistics.txt
[ $? -ne 0 ] && exit 1;
cat ../projects/POLYNESIAN/POLYNESIAN.${DATE}.hand.statistics.txt
rm  ../projects/POLYNESIAN/POLYNESIAN.${DATE}.hand.statistics.txt

python3 REcli.py -c -m hand POLYNESIAN > ../projects/POLYNESIAN/POLYNESIAN.mel.coverage.txt
python3 REcli.py -x -- POLYNESIAN