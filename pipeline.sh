#!/usr/bin/env bash
#
set -x

# run the csv converter for the data
python ../../../src/csv_to_lexicon.py NYI.TAB.u8.csv "1,0, 2"
[ $? -ne 0 ] && exit 1;
python ../../../src/csv_to_lexicon.py SYI.TAB.u8.csv "1,0, 2"
[ $? -ne 0 ] && exit 1;

# other minor fixups
#
# remove parens surrounding forms
perl -i -pe 's#<hw>\((.*)\)</hw>#<hw>\1</hw>#;' *.data.xml
perl -i -pe 's#<hw>(.*?), (.*?)</hw>#<hw>\1</hw>\n    <hw>\2</hw>#;' *.data.xml

# run the csv converter for the correspondences
python ../../../src/csv_to_re.py NYI.TOC.u8.csv NYI.correspondences.xml NYI.classes.xml
[ $? -ne 0 ] && exit 1;
python ../../../src/csv_to_re.py SYI.TOC.u8.csv SYI.correspondences.xml SYI.classes.xml
[ $? -ne 0 ] && exit 1;

exit 0