set -x

DATE=`date +%Y-%m-%d-%H-%M`

XPWD=`pwd`
# run the pipeline first to set up the data
rm -rf ../experiments/SYI
rm -rf ../experiments/NYI
mkdir ../experiments/SYI
mkdir ../experiments/NYI
cp -r ../projects/LOLOISH ../experiments/SYI/semantics
cp -r ../projects/LOLOISH ../experiments/NYI/semantics
cd ../experiments/SYI/semantics; ./pipeline.sh
cd ../../NYI/semantics         ; ./pipeline.sh
[ $? -ne 0 ] && exit 1;

cd $XPWD

# make the "standard" sets -- with the MEL
time python3 REcli.py upstream NYI semantics    --run hand        --mel hand --recon standard
time python3 REcli.py upstream SYI semantics    --run hand        --mel hand --recon standard

# generate the strict sets
time python3 REcli.py upstream NYI semantics -w --run hand-strict --mel hand --recon standard
time python3 REcli.py upstream SYI semantics -w --run hand-strict --mel hand --recon standard

# compare
time python3 REcli.py compare NYI semantics -r1 hand-strict semantics -r2 hand > dev/null
time python3 REcli.py compare SYI semantics -r1 hand-strict semantics -r2 hand > dev/null

# coverage
time python3 REcli.py coverage NYI semantics hand
[ $? -ne 0 ] && exit 1;
time python3 REcli.py coverage SYI semantics hand
[ $? -ne 0 ] && exit 1;

exit 1