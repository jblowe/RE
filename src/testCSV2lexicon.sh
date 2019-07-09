#!/usr/bin/env bash
python3 csv_to_lexicon.py ../projects/LOLOISH/NYI.TAB.u8.csv "1,0, 2"
[ $? -ne 0 ] && exit 1;
python3 csv_to_lexicon.py ../projects/LOLOISH/SYI.TAB.u8.csv "1,0, 2"
[ $? -ne 0 ] && exit 1;

exit 0