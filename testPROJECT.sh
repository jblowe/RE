
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

echo ${PROJECT}/${EXPERIMENT}

if [ -e "test${PROJECT}.sh" ]
then
   echo "running test${PROJECT}.sh instead...."
   bash test${PROJECT}.sh ${PROJECT} ${EXPERIMENT}
   # don't try to do anything else if previous script said not to...
   [ $? -eq 0 ] || exit 0;
fi

# first make run 'none' with no MEL
time python3 REcli.py upstream ${PROJECT} ${EXPERIMENT} --run none   --recon standard > /dev/null
[ $? -ne 0 ] && exit 1;

# next make the "strict" sets: remove untouched mels and merge sets with identical support
time python3 REcli.py upstream ${PROJECT} ${EXPERIMENT} --run hand  --recon standard --mel hand -w > /dev/null
[ $? -ne 0 ] && exit 1;

# compare hand to none
time python3 REcli.py compare ${PROJECT} ${EXPERIMENT} ${EXPERIMENT} --run1 hand --run2 none > ../experiments/${PROJECT}/${EXPERIMENT}/${PROJECT}.${mel}.compare.txt
[ $? -ne 0 ] && exit 1;

# wordnet version is too slow for regular testing use (8 mins) ... run by hand if needed.
# for mel in wordnet clics
for mel in wordnet clics
do
    if [ -e ../experiments/${PROJECT}/${EXPERIMENT}/${PROJECT}.${mel}.mel.xml ]
    then
        # first make sets with this mel
        time python3 REcli.py upstream ${PROJECT} ${EXPERIMENT} --run ${mel} --recon standard --mel ${mel} > /dev/null
        [ $? -ne 0 ] && exit 1;

        # coverage
        time python3 REcli.py coverage ${PROJECT} ${EXPERIMENT} ${mel}  > ../experiments/${PROJECT}/${EXPERIMENT}/${PROJECT}.${mel}.coverage.txt
        [ $? -ne 0 ] && exit 1;

        # compare
        time python3 REcli.py compare ${PROJECT} ${EXPERIMENT} ${EXPERIMENT} --run1 hand --run2 ${mel} > ../experiments/${PROJECT}/${EXPERIMENT}/${PROJECT}.${mel}.compare.txt
        [ $? -ne 0 ] && exit 1;

        # compare to none
        time python3 REcli.py compare ${PROJECT} ${EXPERIMENT} ${EXPERIMENT} --run1 ${mel} --run2 none > ../experiments/${PROJECT}/${EXPERIMENT}/${PROJECT}.${mel}.compare.txt
        [ $? -ne 0 ] && exit 1;
    fi

done
exit 0
