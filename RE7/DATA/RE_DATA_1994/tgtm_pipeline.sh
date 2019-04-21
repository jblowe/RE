#
set -x

# run the perl hack to convert the lexware files to XML
perl Lex2XML.pl MONGUR8_1994.DAT TEMP.gha.data.xml gha.xml.log gha
perl Lex2XML.pl MARPHA_1993.DAT TEMP.mar.data.xml mar.xml.log mar
perl Lex2XML.pl MONPRA8_1993.DAT TEMP.pra.data.xml pra.xml.log pra
perl Lex2XML.pl MONRIS_1994.DAT TEMP.ris.data.xml ris.xml.log ris
perl Lex2XML.pl MONSAH_1992.DAT TEMP.sahu.data.xml sahu.xml.log sahu
perl Lex2XML.pl SYANG_1994.DAT TEMP.syang.data.xml syang.xml.log syang
perl Lex2XML.pl TAG6_1994Aug1.DAT TEMP.tag.data.xml tag.xml.log tag
perl Lex2XML.pl ALLTHAK_1993.DAT TEMP.tuk.data.xml tuk.xml.log tuk

#perl Lex2XML.pl MONTAG_1994.DAT TEMP.tag2.data.xml tag.xml.log tag
#perl Lex2XML.pl MONTUK_1991.DAT TEMP.tuk2.data.xml tuk.xml.log tuk

# apply xslt
xsltproc ../../../RE7/styles/fmtLex.xsl TEMP.gha.data.xml > TGTM.gha.data.xml 2> gha.xslt.log
xsltproc ../../../RE7/styles/fmtLex.xsl TEMP.mar.data.xml > TGTM.mar.data.xml 2> mar.xslt.log
xsltproc ../../../RE7/styles/fmtLex.xsl TEMP.pra.data.xml > TGTM.pra.data.xml 2> pra.xslt.log
xsltproc ../../../RE7/styles/fmtLex.xsl TEMP.ris.data.xml > TGTM.ris.data.xml 2> ris.xslt.log
xsltproc ../../../RE7/styles/fmtLex.xsl TEMP.sahu.data.xml > TGTM.sahu.data.xml 2> sahu.xslt.log
#xsltproc ../../../RE7/styles/fmtLex.xsl TEMP.syang.data.xml > TGTM.syang.data.xml 2> syang.xslt.log
xsltproc ../../../RE7/styles/fmtLex.xsl TEMP.tag.data.xml > TGTM.tag.data.xml 2> tag.xslt.log
#xsltproc ../../../RE7/styles/fmtLex.xsl TEMP.tuk.data.xml > TGTM.tuk.data.xml 2> tuk.xslt.log

#xsltproc ../../../RE7/styles/fmtLex.xsl TEMP.tag2.data.xml > TGTM.tag2.data.xml 2> tag2.xslt.log
#xsltproc ../../../RE7/styles/fmtLex.xsl TEMP.tuk2.data.xml > TGTM.tuk2.data.xml 2> tuk2.xslt.log

cat *.xslt.log > all.logs
cat all.logs

ls -l

# overwrite the existing legacy files with the latest creations
mv TGTM.*.data.xml ../TGTM

# combine the conversion logs (they have useful stats) into one
cat *.xml.log > ../TGTM/TGTM.xml.log
rm *.xml.log

# combine the xslt logs into one
cat *.xslt.log > ../TGTM/TGTM.xslt.log
rm *.xslt.log

# get rid of the temp files
rm TEMP.*.data.xml
