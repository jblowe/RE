#!/usr/bin/env bash
#
set -x

# do the 'initial' extraction
python hm-extract.py hm-all.csv HM.TAB.csv HM.TOC.csv

# run the csv converter for the data
python ../../../src/csv_to_lexicon.py HM.TAB.csv "1,0, 2"
[ $? -ne 0 ] && exit 1;

# run the csv converter for the correspondences
python ../../../src/csv_to_re.py HM.TOC.csv HM.standard.correspondences.xml HM.classes.xml
[ $? -ne 0 ] && exit 1;

exit 0
