
set -x

git submodule update --init --recursive

PROJECT="$1"
TOC="$2"

DATE=`date +%Y-%m-%d-%H-%M`

echo ${PROJECT}

# first make run 'none' with no MEL
time python3 REcli.py upstream ${PROJECT} --run none --recon ${TOC}
[ $? -ne 0 ] && exit 0;

# next make the "strict" sets: remove untouched mels and merge sets with identical support
time python3 REcli.py upstream ${PROJECT} --run hand --recon ${TOC} --mel hand -w
[ $? -ne 0 ] && exit 0;

# compare hand to none
# time python3 REcli.py compare ${PROJECT} --run1 hand --run2 none > ../projects/${PROJECT}/${PROJECT}.hand2none.compare.txt
# [ $? -ne 0 ] && exit 0;

exit 0
