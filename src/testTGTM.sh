
set -x

git submodule update --init --recursive

PROJECT="$1"
EXPERIMENT="$2"

if [ "${EXPERIMENT}" == "" ]
then
    echo "must supply name of experiments as arg 2"
    exit 0
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

# first make run 'none' with no MEL
time python3 REcli.py upstream ${PROJECT} ${EXPERIMENT} --run none --recon standard -z fuzzy > /dev/null
[ $? -ne 0 ] && exit 0;
# next make the "strict" sets: remove untouched mels and merge sets with identical support
time python3 REcli.py upstream ${PROJECT} ${EXPERIMENT} --run hand --mel hand --recon standard -z fuzzy -w > /dev/null
[ $? -ne 0 ] && exit 0;
# compare hand to none
time python3 REcli.py compare ${PROJECT} ${EXPERIMENT} ${EXPERIMENT} --run1 hand --run2 none > ../experiments/${PROJECT}/${EXPERIMENT}/${PROJECT}.${mel}.compare.txt

for mel in clics wordnet
do
    if [ -e ../experiments/${PROJECT}/${EXPERIMENT}/${PROJECT}.${mel}.mel.xml ]
    then
        # first test make sets, with each mel
        time python3 REcli.py upstream ${PROJECT} ${EXPERIMENT}    --run ${mel}        --mel ${mel} --recon standard -z fuzzy -w > /dev/null
        [ $? -ne 0 ] && exit 0;

        # next make the "strict" sets: remove untouched mels and merge sets with identical support
        # time python3 REcli.py upstream ${PROJECT} ${EXPERIMENT} -w --run ${mel}-notstrict --mel ${mel} --recon standard -z fuzzy > /dev/null
        # [ $? -ne 0 ] && exit 0;

        # coverage
        time python3 REcli.py coverage ${PROJECT} ${EXPERIMENT} ${mel}  > ../experiments/${PROJECT}/${EXPERIMENT}/${PROJECT}.${mel}.coverage.txt

        # compare
        time python3 REcli.py compare ${PROJECT} ${EXPERIMENT} ${EXPERIMENT} --run1 hand --run2 ${mel} > ../experiments/${PROJECT}/${EXPERIMENT}/${PROJECT}.${mel}.compare.txt
    fi

done
exit 0
