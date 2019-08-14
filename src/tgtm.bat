# make a new experiment
python REcli.py new-experiment TGTM exp1

#upstream: MEL=none, hand, hand-extended, all with fuzzy

python REcli.py upstream TGTM exp1                  -r std-nomel    -t standard -w -z fuzzy
python REcli.py upstream TGTM exp1 -m hand          -r std-hand     -t standard -w -z fuzzy
python REcli.py upstream TGTM exp1 -m hand-extended -r std-hand-ext -t standard -w -z fuzzy

# MEL coverage: hand, hand-extended
python REcli.py coverage TGTM exp1 hand
python REcli.py coverage TGTM exp1 hand-extended

# compare hand with nomel
python REcli.py compare TGTM exp1 exp1 -r1 std-hand -r2 std-nomel
# compare hand with hand-ext
python REcli.py compare TGTM exp1 exp1 -r1 std-hand -r2 std-hand-ext
