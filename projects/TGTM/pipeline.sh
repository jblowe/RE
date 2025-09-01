#
set -v

# run the csv converter for the correspondences
python3 $1/csv_to_re.py TGTM.C794.csv TGTM.C794.correspondences.xml TGTM.classes.xml
[ $? -ne 0 ] && exit 1;
python3 $1/csv_to_re.py C796.correspondences.csv TGTM.C796.correspondences.xml TGTM.classes.xml
[ $? -ne 0 ] && exit 1;
python3 $1/csv_to_re.py C2023-09-14.correspondences.csv TGTM.C2023-09-14.correspondences.xml TGTM.classes.xml
[ $? -ne 0 ] && exit 1;


# run the perl hack to convert the lexware files to XML
perl $1/Lex2XML.pl MONGUR8_1994.DAT TGTM.gha.data.xml gha.xml.log gha
perl $1/Lex2XML.pl MARPHA_1993.DAT TGTM.mar.data.xml mar.xml.log mar
perl $1/Lex2XML.pl MONPRA8_1993.DAT TGTM.pra.data.xml pra.xml.log pra
perl $1/Lex2XML.pl ALLRIS2019.DAT TGTM.ris.data.xml ris.xml.log ris
perl $1/Lex2XML.pl MONSAH_1992.DAT TGTM.sahu.data.xml sahu.xml.log sahu
perl $1/Lex2XML.pl SYANG_1994.DAT TGTM.syang.data.xml syang.xml.log syang
perl $1/Lex2XML.pl TAG6_1994Aug1.DAT TGTM.tag.data.xml tag.xml.log tag
perl $1/Lex2XML.pl ALLTHAK_1993.DAT TGTM.tuk.data.xml tuk.xml.log tuk
# special change for Tangbe
if [ -e TANGBE2023.DAT ]
then
  perl $1/Lex2XML.pl TANGBE2023.DAT TGTM.tang.data.xml tang.xml.log tang
  perl -i -pe 's/<(\/?)phrase_?/<\1hw/g;s/form>/hw>/g;s/(hw)?gloss>/gl>/g;' TGTM.tang.data.xml
  perl -i -pe 's/<hw>([^⁰¹²³⁴⁵⁶])/<hw>X\1/g;s/ʱ//g;' TGTM.tang.data.xml
  python3 $1/addngl.py TGTM.tang.data.xml gloss
fi

#perl $1/Lex2XML.pl MONTAG_1994.DAT TGTM.tag2.data.xml tag.xml.log tag
#perl $1/Lex2XML.pl MONTUK_1991.DAT TGTM.tuk2.data.xml tuk.xml.log tuk

# apply xslt
#python3 $1/xsltproc.py $1/../styles/fmtLex.xsl TEMP.gha.data.xml > TGTM.gha.data.xml 2> gha.xslt.log
#python3 $1/xsltproc.py $1/../styles/fmtLex.xsl TEMP.mar.data.xml > TGTM.mar.data.xml 2> mar.xslt.log
#python3 $1/xsltproc.py $1/../styles/fmtLex.xsl TEMP.pra.data.xml > TGTM.pra.data.xml 2> pra.xslt.log
#python3 $1/xsltproc.py $1/../styles/fmtLex.xsl TEMP.ris.data.xml > TGTM.ris.data.xml 2> ris.xslt.log
#python3 $1/xsltproc.py $1/../styles/fmtLex.xsl TEMP.sahu.data.xml > TGTM.sahu.data.xml 2> sahu.xslt.log
#python3 $1/xsltproc.py $1/../styles/fmtLex.xsl TEMP.syang.data.xml > TGTM.syang.data.xml 2> syang.xslt.log
#python3 $1/xsltproc.py $1/../styles/fmtLex.xsl TEMP.tag.data.xml > TGTM.tag.data.xml 2> tag.xslt.log
#python3 $1/xsltproc.py $1/../styles/fmtLex.xsl TEMP.tuk.data.xml > TGTM.tuk.data.xml 2> tuk.xslt.log
#python3 $1/xsltproc.py $1/../styles/fmtLex.xsl TEMP.tang.data.xml > TGTM.tang.data.xml 2> tang.xslt.log

#python3 $1/xsltproc.py $1/../styles/fmtLex.xsl TEMP.tag2.data.xml > TGTM.tag2.data.xml 2> tag2.xslt.log
#python3 $1/xsltproc.py $1/../styles/fmtLex.xsl TEMP.tuk2.data.xml > TGTM.tuk2.data.xml 2> tuk2.xslt.log

# other minor fixups
python3 $1/addngl.py TGTM.gha.data.xml gl
python3 $1/addngl.py TGTM.mar.data.xml dff
python3 $1/addngl.py TGTM.pra.data.xml gl
python3 $1/addngl.py TGTM.ris.data.xml dff
python3 $1/addngl.py TGTM.sahu.data.xml dfe
python3 $1/addngl.py TGTM.syang.data.xml dff
python3 $1/addngl.py TGTM.tag.data.xml dff
python3 $1/addngl.py TGTM.tuk.data.xml dff

#python3 $1/addngl.py TGTM.tag2.data.xml
#python3 $1/addngl.py TGTM.tuk2.data.xml

#exit

ls -l

# combine the conversion logs (they have useful stats) into one
cat *.xml.log > all.xml.logs
rm *.xml.log

# combine the xslt logs into one
cat *.xslt.log > all.xslt.logs
rm *.xslt.log
rm TEMP.*.xml

#python3 -c "import os, glob;list(map(os.remove, glob.glob('*.xslt.log')))"
# get rid of the temp files
#python3 -c "import os, glob;list(map(os.remove, glob.glob('TEMP.*.xml')))"

