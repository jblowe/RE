
set -x

git submodule update --init --recursive

PROJECT=TGTM
DATE=`date +%Y-%m-%d-%H-%M`

if [ ! -d ../projects/${PROJECT} ]
then
   echo "../projects/${PROJECT} does not exist."
   exit 1
fi

# if [ -f ../projects/${PROJECT}/$2 ]
# then
#    echo "running pipeline for ../projects/${PROJECT}/$2."
#    XPWD=`pwd`
#    cd ../projects/${PROJECT} ; ./$2
#    [ $? -ne 0 ] && exit 1;
#    cd $XPWD
# fi

if [ -e "test${PROJECT}.sh" ]
then
   echo "running test${PROJECT}.sh instead of testPROJECT.sh ${PROJECT}."
   bash test${PROJECT}.sh
   exit 0
fi

# make default sets, no mel
time python3 REcli.py ${PROJECT} > ../projects/${PROJECT}/${PROJECT}.default.txt

for mel in hand clics wordnet wordnet2 none
do
    if [ -e ../projects/${PROJECT}/${PROJECT}.${mel}.mel.xml ] || [ "${mel}" = "none" ]
    then
        # first test make sets, with each mel
        time python3 REcli.py ${PROJECT} -r ${mel} -m ${mel} > ../projects/${PROJECT}/${PROJECT}.${DATE}.${mel}.statistics.txt
        [ $? -ne 0 ] && exit 1;
        cat ../projects/${PROJECT}/${PROJECT}.${DATE}.${mel}.statistics.txt
        rm ../projects/${PROJECT}/${PROJECT}.${DATE}.${mel}.statistics.txt

        # next make the "strict" sets: remove untouched mels and merge sets with identical support
        time python3 REcli.py ${PROJECT} -w --run ${mel}-strict --mel ${mel}
        [ $? -ne 0 ] && exit 1;

        # next test mel comparison
        time python3 REcli.py ${PROJECT} -r ${mel} --mel hand --mel2 ${mel}
        [ $? -ne 0 ] && exit 1;
        head ../projects/${PROJECT}/${PROJECT}.${mel}.analysis.txt
        rm ../projects/${PROJECT}/${PROJECT}.${mel}.analysis.txt
    fi
done

# coverage
time python3 REcli.py -c -m hand ${PROJECT} > ../projects/${PROJECT}/${PROJECT}.mel.coverage.txt

# compare
time python3 REcli.py -x -- ${PROJECT} > ../projects/DIS/${PROJECT}.mel.compare.txt
