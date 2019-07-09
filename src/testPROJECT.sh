
set -x

git submodule update --init --recursive

PROJECT=$1

DATE=`date +%Y-%m-%d-%H-%M`

if [ ! -d ../projects/${PROJECT} ]
then
   echo "../projects/${PROJECT} does not exist."
   exit 1
fi

if [ -e "test${PROJECT}.sh" ]
then
   echo "running test${PROJECT}.sh ahead of ${PROJECT}."
   bash test${PROJECT}.sh
   # don't try to do anything else if previous script said not to...
   [ $? -eq 0 ] || exit 0;
fi

if [ "$2" != "" ]
then
    # make another with the specified run name and abandon ship
    time python3 REcli.py ${PROJECT} $2 > ../projects/${PROJECT}/${PROJECT}.$2.txt
    exit 0
fi

# make default sets, no mel
time python3 REcli.py ${PROJECT} > ../projects/${PROJECT}/${PROJECT}.default.txt


for mel in hand wordnet clics none
# wordnet version is too slow for regular testing use (8 mins) ... run by hand if needed.
# for mel in hand clics none
do
    if [ -e ../projects/${PROJECT}/${PROJECT}.${mel}.mel.xml ] || [ "${mel}" = "none" ]
    then
        # first test make sets, with each mel
        time python3 REcli.py ${PROJECT} --run ${mel} -m ${mel} > ../projects/${PROJECT}/${PROJECT}.${DATE}.${mel}.statistics.txt
        [ $? -ne 0 ] && exit 1;
        cat ../projects/${PROJECT}/${PROJECT}.${DATE}.${mel}.statistics.txt

        # next make the "strict" sets: remove untouched mels and merge sets with identical support
        time python3 REcli.py ${PROJECT} -w --run ${mel}-strict --mel ${mel}
        [ $? -ne 0 ] && exit 1;

        # next test mel comparison
        time python3 REcli.py ${PROJECT} --run ${mel} --mel hand --mel2 ${mel}
        [ $? -ne 0 ] && exit 1;
        head ../projects/${PROJECT}/${PROJECT}.${mel}.analysis.txt
    fi
done

# coverage
time python3 REcli.py -c -m hand ${PROJECT} > ../projects/${PROJECT}/${PROJECT}.mel.coverage.txt

# compare
time python3 REcli.py -x -- ${PROJECT} > ../projects/DIS/${PROJECT}.mel.compare.txt
