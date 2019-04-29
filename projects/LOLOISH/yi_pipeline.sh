#!/usr/bin/env bash
#
set -x

# run the csv converter for the data
python3 ../../src/csv_to_lexicon.py NYI.TAB.u8.csv "1,0, 2"
python3 ../../src/csv_to_lexicon.py SYI.TAB.u8.csv "1,0, 2"

# run the csv converter for the correspondences
python3 ../../src/csv_to_re.py NYI.TOC.u8.csv NYI.correspondences.xml NYI.classes.xml
python3 ../../src/csv_to_re.py SYI.TOC.u8.csv SYI.correspondences.xml SYI.classes.xml
