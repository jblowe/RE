set -x
# start with a clean slate: restore any changed files to last commit 
./cleanup.sh
git checkout -- ../projects/VANUATU/*

# make a version of the code with the revised disyllabic canon
perl -pe 's/CV\+/(C)V((C)V)+/' ../projects/VANUATU/hook.py > ../projects/VANUATU/ CVCVhook.py

# here are our two different ToCs
diff ../projects/VANUATU/VANUATU.pwzeroexperimental.correspondences.csv ../projects/VANUATU/VANUATU.experimental.correspondences.csv

# here are our two different Syllable canons
grep RE.SyllableCanon ../projects/VANUATU/*hook.py

# OK run the status quo, using Alex's "*p,*w without zero" version of ToC, call it "CV"
time python3 REcli.py VANUATU -w -r CV --mel hand > /dev/null

# use the revised canon, call the run "CVCV"
cp ../projects/VANUATU/CVCVhook.py ../projects/VANUATU/hook.py 
time python3 REcli.py VANUATU -w -r CVCV --mel hand  > /dev/null

# use JB's "revised" ToC (*p,*w can > zero), call it CVCVpw
cp VANUATU.pwzeroexperimental.correspondences.csv VANUATU.experimental.correspondences.csv
time python3 REcli.py VANUATU -w -r CVCVpw --mel hand  > /dev/null

# restrore the original canon, try again call it CVpw
git checkout -- ../projects/VANUATU/hook.py
time python3 REcli.py VANUATU -w -r CVpw --mel hand  > /dev/null

# generate comparisons
python3 REcli.py -x -- VANUATU

