
set -x

git submodule update --init --recursive

PROJECT=$1
EXPERIMENT=$2

if [ "${EXPERIMENT}" != "" ]
then
   SPACER="/experiments/"
fi

DATE=`date +%Y-%m-%d-%H-%M`

if [ ! -d ../projects/${PROJECT}${SPACER}${EXPERIMENT} ]
then
   echo "../projects/${PROJECT}${SPACER}${EXPERIMENT} does not exist. creating..."
   mkdir -p ../projects/${PROJECT}${SPACER}${EXPERIMENT}
   cp ../projects/${PROJECT}/*  ../projects/${PROJECT}${SPACER}${EXPERIMENT}
fi

if [ -e "prepare${PROJECT}.sh" ]
then
   echo "running prepare${PROJECT}.sh ahead of ${PROJECT}."
   bash prepare${PROJECT}.sh ${PROJECT}${SPACER}${EXPERIMENT}
   # don't try to do anything else if previous script said not to...
   [ $? -eq 0 ] || exit 0;
fi

echo ${PROJECT}${SPACER}${EXPERIMENT}

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
    if [ -e ../projects/${PROJECT}${SPACER}${EXPERIMENT}/${PROJECT}.${mel}.mel.xml ] || [ "${mel}" = "none" ]
    then
        # first test make sets, with each mel
        time python3 REcli.py ${PROJECT}${SPACER}${EXPERIMENT} --run ${mel} -m ${mel} > ../projects/${PROJECT}${SPACER}${EXPERIMENT}/${PROJECT}.${DATE}.${mel}.statistics.txt
        [ $? -ne 0 ] && exit 1;
        cat ../projects/${PROJECT}${SPACER}${EXPERIMENT}/${PROJECT}.${DATE}.${mel}.statistics.txt

        # next make the "strict" sets: remove untouched mels and merge sets with identical support
        time python3 REcli.py ${PROJECT}${SPACER}${EXPERIMENT} -w --run ${mel}-strict --mel ${mel}
        [ $? -ne 0 ] && exit 1;

        # next test mel comparison with and without strict
        time python3 REcli.py ${PROJECT}${SPACER}${EXPERIMENT} --run ${mel} --mel hand --mel2 ${mel}
        [ $? -ne 0 ] && exit 1;
        head ../projects/${PROJECT}${SPACER}${EXPERIMENT}/${PROJECT}.${mel}.analysis.txt
        time python3 REcli.py ${PROJECT}${SPACER}${EXPERIMENT} -w --run ${mel}-strict --mel hand --mel2 ${mel}
        [ $? -ne 0 ] && exit 1;
        head ../projects/${PROJECT}${SPACER}${EXPERIMENT}/${PROJECT}.${mel}-strict.analysis.txt
    fi
done

# coverage
time python3 REcli.py -c -m hand ${PROJECT}${SPACER}${EXPERIMENT} > ../projects/${PROJECT}${SPACER}${EXPERIMENT}/${PROJECT}.mel.coverage.txt

# compare
time python3 REcli.py -x -- ${PROJECT}${SPACER}${EXPERIMENT} > ../projects/${PROJECT}${SPACER}${EXPERIMENT}.mel.compare.txt
