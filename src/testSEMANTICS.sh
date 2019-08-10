set -x

PYTHON=python3
PROJECT="$1"
EXPERIMENT="$2"
MEL1=hand
MEL2=clics

$PYTHON REcli.py new-experiment ${PROJECT} ${EXPERIMENT}
$PYTHON REcli.py upstream ${PROJECT} ${EXPERIMENT} --mel ${MEL1} --recon standard --run w-${MEL1} -w
$PYTHON REcli.py upstream ${PROJECT} ${EXPERIMENT} --mel ${MEL2} --recon standard --run w-${MEL2} -w
$PYTHON REcli.py upstream ${PROJECT} ${EXPERIMENT}               --recon standard --run standard

# To compare the differences:
$PYTHON REcli.py compare ${PROJECT} ${EXPERIMENT} ${EXPERIMENT} -run1 w-${MEL1} -run2 standard
$PYTHON REcli.py compare ${PROJECT} ${EXPERIMENT} ${EXPERIMENT} -run1 w-${MEL2} -run2 standard
$PYTHON REcli.py compare ${PROJECT} ${EXPERIMENT} ${EXPERIMENT} -run1 w-${MEL1} -run2 w-${MEL2}

