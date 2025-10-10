#!/usr/bin/env bash
#
set -x

# do the 'initial' extraction

# don't do this for now: the ToC and tabular data are now committed in GitHub for development
#python3 hm-extract.py hm-all.csv HM.TAB.csv HM.TOC.csv

# run the csv converter for the data
python3 ../../src/csv_to_lexicon.py HM.TAB.csv "1,0, 2"
[ $? -ne 0 ] && exit 1;

# run the csv converter for the correspondences
python3 ../../src/csv_to_re.py HM.TOC.csv HM.standard.correspondences.xml HM.classes.xml
[ $? -ne 0 ] && exit 1;

exit 0
