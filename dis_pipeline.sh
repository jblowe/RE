#
set -x

# run the perl hack to convert the lexware files to XML
perl ../RE_DATA_1994/Lex2XML.pl GHA.DIS TEMP.gha.data.xml gha.xml.log gha
perl ../RE_DATA_1994/Lex2XML.pl MAR.DIS TEMP.mar.data.xml mar.xml.log mar
perl ../RE_DATA_1994/Lex2XML.pl MAN.DIS TEMP.pra.data.xml pra.xml.log pra
perl ../RE_DATA_1994/Lex2XML.pl RIS.DIS TEMP.ris.data.xml ris.xml.log ris
perl ../RE_DATA_1994/Lex2XML.pl SAHU.DIS TEMP.sahu.data.xml sahu.xml.log sahu
perl ../RE_DATA_1994/Lex2XML.pl SYANG.DIS TEMP.syang.data.xml syang.xml.log syang
perl ../RE_DATA_1994/Lex2XML.pl TAG.DIS TEMP.tag.data.xml tag.xml.log tag
perl ../RE_DATA_1994/Lex2XML.pl TUK.DIS TEMP.tuk.data.xml tuk.xml.log tuk

# apply xslt
python3 ../../src/xsltproc.py ../../styles/fmtLex.xsl TEMP.gha.data.xml > DIS.gha.data.xml 2> gha.xslt.log
python3 ../../src/xsltproc.py ../../styles/fmtLex.xsl TEMP.mar.data.xml > DIS.mar.data.xml 2> mar.xslt.log
python3 ../../src/xsltproc.py ../../styles/fmtLex.xsl TEMP.pra.data.xml > DIS.pra.data.xml 2> pra.xslt.log
python3 ../../src/xsltproc.py ../../styles/fmtLex.xsl TEMP.ris.data.xml > DIS.ris.data.xml 2> ris.xslt.log
python3 ../../src/xsltproc.py ../../styles/fmtLex.xsl TEMP.sahu.data.xml > DIS.sahu.data.xml 2> sahu.xslt.log
python3 ../../src/xsltproc.py ../../styles/fmtLex.xsl TEMP.syang.data.xml > DIS.syang.data.xml 2> syang.xslt.log
python3 ../../src/xsltproc.py ../../styles/fmtLex.xsl TEMP.tag.data.xml > DIS.tag.data.xml 2> tag.xslt.log
python3 ../../src/xsltproc.py ../../styles/fmtLex.xsl TEMP.tuk.data.xml > DIS.tuk.data.xml 2> tuk.xslt.log


# other minor fixups
perl -i -pe 's/\-<.hw>/<\/hw>/;' DIS.*.data.xml
perl -i -pe 's#<hw>( *[=\-])#<prefix>\1</prefix><hw>#;' DIS.*.data.xml
perl -i -pe 's#<hw>(.*?)( *[=\-].*?)</hw>#<hw>\1</hw><suffix>\2</suffix>#;' DIS.*.data.xml
perl -i -p ../RE_DATA_1994/addngl.pl DIS.*.data.xml

# combine the conversion logs (they have useful stats) into one
cat *.xml.log > foo
rm *.xml.log
mv foo xml.log

# combine the xslt logs into one
cat *.xslt.log > foo
rm *.xslt.log
mv foo xslt.log

ls -l

# get rid of the temp files
rm TEMP.*.data.xml
