
set -x

git submodule update --init --recursive

PROJECT="$1"
EXPERIMENT="$2"

if [ "${EXPERIMENT}" == "" ]
then
    echo "must supply name of experiments as arg 2"
    exit 1
fi

DATE=`date +%Y-%m-%d-%H-%M`

if [ ! -d ../experiments/${PROJECT}/${EXPERIMENT} ]
then
   echo "../experiments/${PROJECT}/${EXPERIMENT} does not exist. creating..."
   python3 REcli.py new-experiment ${PROJECT} ${EXPERIMENT}
fi

if [ -e "prepare${PROJECT}.sh" ]
then
   echo "running prepare${PROJECT}.sh ahead of ${PROJECT}."
   bash prepare${PROJECT}.sh ${PROJECT}/${EXPERIMENT}
   # don't try to do anything else if previous script said not to...
   [ $? -eq 0 ] || exit 0;
fi


# for mel in hand wordnet clics none
# wordnet version is too slow for regular testing use (8 mins) ... run by hand if needed.
# first make run 'none' with no MEL
time python3 REcli.py upstream ${PROJECT} ${EXPERIMENT} --run none --recon standard -z fuzzy > /dev/null
[ $? -ne 0 ] && exit 1;
for mel in hand clics wordnet
do
    if [ -e ../experiments/${PROJECT}/${EXPERIMENT}/${PROJECT}.${mel}.mel.xml ]
    then
        # first test make sets, with each mel
        time python3 REcli.py upstream ${PROJECT} ${EXPERIMENT}    --run ${mel}        --mel ${mel} --recon standard -z fuzzy > /dev/null
        [ $? -ne 0 ] && exit 1;

        # next make the "strict" sets: remove untouched mels and merge sets with identical support
        time python3 REcli.py upstream ${PROJECT} ${EXPERIMENT} -w --run ${mel}-strict --mel ${mel} --recon standard -z fuzzy > /dev/null
        [ $? -ne 0 ] && exit 1;

        # coverage
        time python3 REcli.py coverage ${PROJECT} ${EXPERIMENT} ${mel}  > ../experiments/${PROJECT}/${EXPERIMENT}/${PROJECT}.${mel}.coverage.txt

        # compare
        time python3 REcli.py compare ${PROJECT} ${EXPERIMENT} ${EXPERIMENT} --run1 hand-strict --run2 ${mel} > ../experiments/${PROJECT}/${EXPERIMENT}/${PROJECT}.${mel}.compare.txt

        # compare to non
        time python3 REcli.py compare ${PROJECT} ${EXPERIMENT} ${EXPERIMENT} --run1 ${mel} --run2 none > ../experiments/${PROJECT}/${EXPERIMENT}/${PROJECT}.${mel}.compare.txt

    fi

    # compare hand-strict to none
    time python3 REcli.py compare ${PROJECT} ${EXPERIMENT} ${EXPERIMENT} --run1 hand-strict --run2 none > ../experiments/${PROJECT}/${EXPERIMENT}/${PROJECT}.${mel}.compare.txt

done
