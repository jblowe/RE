
set -x

git submodule update --init --recursive

PROJECT=$1
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
# for mel in hand wordnet clics none
# wordnet version is too slow for regular testing use (8 mins) ... run by hand if needed.
for mel in hand clics none
do
    if [ -e ../projects/${PROJECT}/${PROJECT}.${mel}.mel.xml ] || [ "${mel}" = "none" ]
    then
        # first test make sets, with 'hand' mel
        time python3 REcli.py ${PROJECT} -r ${mel} -m ${mel} > ../projects/${PROJECT}/${PROJECT}.${DATE}.${mel}.statistics.txt
        [ $? -ne 0 ] && exit 1;
        cat ../projects/${PROJECT}/${PROJECT}.${DATE}.${mel}.statistics.txt
        rm ../projects/${PROJECT}/${PROJECT}.${DATE}.${mel}.statistics.txt

        # next make the "parsimonious" sets: remove untouched mels and merge sets with identical support
        time python3 REcli.py ${PROJECT} -w --run ${mel}-parsimonious --mel ${mel}
        [ $? -ne 0 ] && exit 1;

        # next test mel comparison
        time python3 REcli.py ${PROJECT} -r ${mel} --mel hand --mel2 ${mel}
        [ $? -ne 0 ] && exit 1;
        head ../projects/${PROJECT}/${PROJECT}.${mel}.analysis.txt
        rm ../projects/${PROJECT}/${PROJECT}.${mel}.analysis.txt
    fi
done

# compare results of all runs
python3 REcli.py -x -- ${PROJECT}