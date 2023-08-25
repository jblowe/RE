
set -x

git submodule update --init --recursive

PROJECT=$1

if [ "$2" != "" ]
then
   RUN="--run $2"
fi


DATE=`date +%Y-%m-%d-%H-%M`

if [ ! -d ../projects/${PROJECT} ]
then
   echo "../projects/${PROJECT} does not exist."
   exit 0
fi

if [ -e "test${PROJECT}.sh" ]
then
   echo "running test${PROJECT}.sh ahead of ${PROJECT}."
   bash test${PROJECT}.sh
fi

# now make another with the specified run name
time python3 REcli.py ${PROJECT} --run ${RUN} > ../projects/${PROJECT}/${PROJECT}.${RUN}.txt

# coverage
time python3 REcli.py -c -m hand ${PROJECT} > ../projects/${PROJECT}/${PROJECT}.mel.coverage.txt

# compare
time python3 REcli.py -x -- ${PROJECT} > ../projects/DIS/${PROJECT}.mel.compare.txt
