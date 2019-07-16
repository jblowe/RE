
set -x

git submodule update --init --recursive

PROJECT=$1
EXPERIMENT=$2

if [ "${EXPERIMENT}" == "" ]
then
    echo "must supply name of experiments as arg 2"
    exit 1
fi

DATE=`date +%Y-%m-%d-%H-%M`

if [ ! -d ../experiments/${PROJECT}/${EXPERIMENT} ]
then
   echo "../experiments/${PROJECT}/${EXPERIMENT} does not exist. creating..."
   mkdir -p ../experiments/${PROJECT}/${EXPERIMENT}
   cp ../projects/${PROJECT}/*  ../experiments/${PROJECT}/${EXPERIMENT}
fi

if [ -e "prepare${PROJECT}.sh" ]
then
   echo "running prepare${PROJECT}.sh ahead of ${PROJECT}."
   bash prepare${PROJECT}.sh ${PROJECT}/${EXPERIMENT}
   # don't try to do anything else if previous script said not to...
   [ $? -eq 0 ] || exit 0;
fi

echo ${PROJECT}/${EXPERIMENT}

if [ -e "test${PROJECT}.sh" ]
then
   echo "running test${PROJECT}.sh instead...."
   bash test${PROJECT}.sh ${EXPERIMENT}
   # don't try to do anything else if previous script said not to...
   [ $? -eq 0 ] || exit 0;
fi

# for mel in hand wordnet clics none
# wordnet version is too slow for regular testing use (8 mins) ... run by hand if needed.
for mel in hand clics none
do
    if [ -e ../experiments/${PROJECT}/${EXPERIMENT}/${PROJECT}.${mel}.mel.xml ] || [ "${mel}" = "none" ]
    then
        # first test make sets, with each mel
        time python3 REcli.py ${PROJECT}/${EXPERIMENT} --run ${mel} -m ${mel} > ../experiments/${PROJECT}/${EXPERIMENT}/${PROJECT}.${DATE}.${mel}.statistics.txt
        [ $? -ne 0 ] && exit 1;
        cat ../experiments/${PROJECT}/${EXPERIMENT}/${PROJECT}.${DATE}.${mel}.statistics.txt

        # next make the "strict" sets: remove untouched mels and merge sets with identical support
        time python3 REcli.py ${PROJECT}/${EXPERIMENT} -w --run ${mel}-strict --mel ${mel}
        [ $? -ne 0 ] && exit 1;

        # next test mel comparison with and without strict
        time python3 REcli.py ${PROJECT}/${EXPERIMENT} --run ${mel} --mel hand --mel2 ${mel}
        [ $? -ne 0 ] && exit 1;
        head ../experiments/${PROJECT}/${EXPERIMENT}/${PROJECT}.${mel}.analysis.txt
        time python3 REcli.py ${PROJECT}/${EXPERIMENT} -w --run ${mel}-strict --mel hand --mel2 ${mel}
        [ $? -ne 0 ] && exit 1;
        head ../experiments/${PROJECT}/${EXPERIMENT}/${PROJECT}.${mel}-strict.analysis.txt
    fi
done

# coverage
time python3 REcli.py -c -m hand ${PROJECT}/${EXPERIMENT} > ../experiments/${PROJECT}/${EXPERIMENT}/${PROJECT}.mel.coverage.txt

# compare
time python3 REcli.py -x -- ${PROJECT}/${EXPERIMENT} > ../experiments/${PROJECT}/${EXPERIMENT}/${PROJECT}.mel.compare.txt
