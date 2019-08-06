set -x

PYTHON=python3
PROJECT="$1"
EXPERIMENT1="$2"
EXPERIMENT2="$3"
MEL1=hand
MEL2=clics

$PYTHON REcli.py new-experiment ${PROJECT} ${EXPERIMENT1}
$PYTHON REcli.py new-experiment ${PROJECT} ${EXPERIMENT2}

$PYTHON REcli.py upstream ${PROJECT} ${EXPERIMENT1} --mel ${MEL1}

#<change a bunch of the correspondences in 1st experiment>

$PYTHON REcli.py upstream ${PROJECT} ${EXPERIMENT2} --mel none

# To compare the differences:
$PYTHON REcli.py compare ${PROJECT} ${EXPERIMENT1} ${EXPERIMENT2} 

# It will give a set diff along with all the other statistics.

# The comparison tool discriminates by taking the experiment name + upstream name. Remember, run name defaults to 'default' unless otherwise specified.
# So, you could even do this with one experiment:

$PYTHON REcli.py upstream ${PROJECT} ${EXPERIMENT1} --mel ${MEL1} --run with-${MEL1}

#<change a bunch of the correspondences in 2nd experiment>
$PYTHON REcli.py upstream ${PROJECT} ${EXPERIMENT2} --mel ${MEL2} --run with-${MEL2}

$PYTHON REcli.py upstream ${PROJECT} ${EXPERIMENT1} --mel ${MEL1} --run strict-${MEL1} -w

#<change a bunch of the correspondences in 2nd experiment>
$PYTHON REcli.py upstream ${PROJECT} ${EXPERIMENT2} --mel ${MEL2} --run strict-${MEL2} -w

# and then do pairwise between the strict and with-MEL runs
$PYTHON REcli.py compare ${PROJECT} ${EXPERIMENT1} ${EXPERIMENT2} --run1 with-${MEL1} --run2 strict-${MEL2}
$PYTHON REcli.py compare ${PROJECT} ${EXPERIMENT1} ${EXPERIMENT2} --run1 with-${MEL1} --run2 strict-${MEL2}

# and then do pairwise between the 2 different MELL runs
$PYTHON REcli.py compare ${PROJECT} ${EXPERIMENT1} ${EXPERIMENT2} --run1 with-${MEL1} --run2 with-${MEL2}
