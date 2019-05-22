perl -ne 'print if /^(\.+hwX?|dff|dfe|so)\b/' dico2019.txt > ALLRIS2019.DAT
python3 tr.py ALLRIS2019.DAT A
mv A ALLRIS2019.DAT 
# 
# these are the two pipeline steps for this lexicon...
# perl Lex2XML.pl A TEMP.ris.data.xml ris.xml.log ris
# python3 ../../src/xsltproc.py ../../styles/fmtLex.xsl TEMP.ris.data.xml > TGTM.ris.data.xml 2> ris.xslt.log

