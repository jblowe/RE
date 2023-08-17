#
set -x

# run the perl hack to convert the lexware files to XML
perl Lex2XML.pl GHA.DIS TEMP.gha.data.xml gha.xml.log gha
perl Lex2XML.pl MAR.DIS TEMP.mar.data.xml mar.xml.log mar
perl Lex2XML.pl MAN.DIS TEMP.pra.data.xml pra.xml.log pra
perl Lex2XML.pl RIS.DIS TEMP.ris.data.xml ris.xml.log ris
perl Lex2XML.pl SAHU.DIS TEMP.sahu.data.xml sahu.xml.log sahu
perl Lex2XML.pl SYANG.DIS TEMP.syang.data.xml syang.xml.log syang
perl Lex2XML.pl TAG.DIS TEMP.tag.data.xml tag.xml.log tag
perl Lex2XML.pl TUK.DIS TEMP.tuk.data.xml tuk.xml.log tuk

# apply xslt
python3 $1/xsltproc.py $1/../styles/fmtLex.xsl TEMP.gha.data.xml > DIS.gha.data.xml 2> gha.xslt.log
python3 $1/xsltproc.py $1/../styles/fmtLex.xsl TEMP.mar.data.xml > DIS.mar.data.xml 2> mar.xslt.log
python3 $1/xsltproc.py $1/../styles/fmtLex.xsl TEMP.pra.data.xml > DIS.pra.data.xml 2> pra.xslt.log
python3 $1/xsltproc.py $1/../styles/fmtLex.xsl TEMP.ris.data.xml > DIS.ris.data.xml 2> ris.xslt.log
python3 $1/xsltproc.py $1/../styles/fmtLex.xsl TEMP.sahu.data.xml > DIS.sahu.data.xml 2> sahu.xslt.log
python3 $1/xsltproc.py $1/../styles/fmtLex.xsl TEMP.syang.data.xml > DIS.syang.data.xml 2> syang.xslt.log
python3 $1/xsltproc.py $1/../styles/fmtLex.xsl TEMP.tag.data.xml > DIS.tag.data.xml 2> tag.xslt.log
python3 $1/xsltproc.py $1/../styles/fmtLex.xsl TEMP.tuk.data.xml > DIS.tuk.data.xml 2> tuk.xslt.log

# other minor fixups
python3 addngl.py DIS.gha.data.xml
python3 addngl.py DIS.mar.data.xml
python3 addngl.py DIS.pra.data.xml
python3 addngl.py DIS.ris.data.xml
python3 addngl.py DIS.sahu.data.xml
python3 addngl.py DIS.syang.data.xml
python3 addngl.py DIS.tag.data.xml
python3 addngl.py DIS.tuk.data.xml

#exit

ls -l

# combine the conversion logs (they have useful stats) into one
cat *.xml.log > all.xml.logs
rm *.xml.log

# combine the xslt logs into one
cat *.xslt.log > all.xslt.logs
rm *.xslt.log

python3 -c "import os, glob;list(map(os.remove, glob.glob('*.xslt.log')))"
# get rid of the temp files
python3 -c "import os, glob;list(map(os.remove, glob.glob('TEMP.*.xml')))"

