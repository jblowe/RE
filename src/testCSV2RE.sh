#!/usr/bin/env bash
python3 csv_to_re.py ../projects/LOLOISH/NYI.TOC.u8.csv ../projects/LOLOISH/NYI.correspondences.xml ../projects/LOLOISH/NYI.classes.xml
[ $? -ne 0 ] && exit 0;

python3 csv_to_re.py ../projects/LOLOISH/SYI.TOC.u8.csv ../projects/LOLOISH/SYI.correspondences.xml ../projects/LOLOISH/SYI.classes.xml
[ $? -ne 0 ] && exit 0;

exit 0