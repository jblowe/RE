#!/usr/bin/env bash
python3 csv_to_lexicon.py ../projects/LOLOISH/NYI.TAB.u8.csv "1,0, 2"
[ $? -ne 0 ] && exit 0;
python3 csv_to_lexicon.py ../projects/LOLOISH/SYI.TAB.u8.csv "1,0, 2"
[ $? -ne 0 ] && exit 0;

exit 0