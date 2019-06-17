
set -x

git submodule update --init --recursive

PROJECT=$1
DATE=`date +%Y-%m-%d-%H-%M`

if [ ! -d ../projects/${PROJECT} ]
then
   echo "../projects/${PROJECT} does not exist."
   exit 1
fi

pwd
for mel in hand wordnet clics none
do
    if [ -e ../projects/${PROJECT}/${PROJECT}.${mel}.mel.xml ] || [ "${mel}" = "none" ]
    then
        # first test make sets, with 'hand' mel
        time python3 REcli.py ${PROJECT} -r ${mel} --mel ${mel} > ../projects/${PROJECT}/${PROJECT}.${DATE}.${mel}.statistics.txt &
        #[ $? -ne 0 ] && exit 1;
        #cat ../projects/${PROJECT}/${PROJECT}.${DATE}.${mel}.statistics.txt

        # second test mel comparison
        time python3 REcli.py ${PROJECT} -r ${mel} --mel hand --mel2 ${mel} &
        #[ $? -ne 0 ] && exit 1;
        #head ../projects/${PROJECT}/${PROJECT}.${mel}.analysis.txt


        # third make the parsimonious sets
        time python3 REcli.py ${PROJECT} -w -r ${mel}-parsimonious --mel hand &
        #[ $? -ne 0 ] && exit 1;
        #head ../projects/${PROJECT}/${PROJECT}.${mel}.analysis.txt
    fi
done
wait

python3 REcli.py -x -- ${PROJECT} > ../projects/${PROJECT}/${PROJECT}.mel.compare.txt

