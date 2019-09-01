cat > header.txt <<EOF
<reconstruction protolanguage="tgtm">
  <createdat>2019-09-01 16:06:51 UTC</createdat>
  <languages>
    <lg>ris</lg>
    <lg>sahu</lg>
    <lg>tag</lg>
    <lg>tuk</lg>
    <lg>mar</lg>
    <lg>syang</lg>
    <lg>gha</lg>
    <lg>man</lg>
  </languages>
  <sets>
EOF

# get ready for xml
perl -pe 's/&/&amp;/g;s/</&lt;/g;s/>/&gt;/g;s/\.$//;' SETS0111-SRT > lex.txt

perl -i -pe 's#(\d+)\.\s+(.*?) +\[(.*?)\](.*)#</sf></set>\n<set>\n<id>\1</id>\n<plg>tgtm</plg>\n<pfm>A\2</pfm>\n<rcn>\3</rcn><rest>\4</rest>\n<sf>#' lex.txt
# 64.  ᴬkra [1.111.33]

# 	sahu	¹kra [[¹kra	head
perl -i -ne 'if (/^</){print;}else{$i++;s#^\t(.*)\t(.*?)\t(.*)#<rfx>\n<lg>\1</lg>\n<lx>\2</lx>\n<gl>\3</gl>\n<id>\1.$i</id>\n</rfx>#;print}' lex.txt

perl -i -pe 's# *\[+ *(.*)<.lx>#</lx><srcxcr1>\1</srcxcr1>#;s#\-</lx>#</lx>#;s#\.</gl>#</gl>#' lex.txt
perl -i -pe 's#(<lx>)(.+?)[ \-=](.*)</lx>#\1\2</lx><srcxcr2>\3</srcxcr2>#' lex.txt
perl -i -pe 's#(<lx>)[\-=](.*)</lx>#\1\2</lx>#' lex.txt
perl -i -pe 's/\&#x303;([^<])/\1\&#x303;/g' lex.txt
perl -i -pe 's/ae\&#x303;/ae\&#771;/g' lex.txt
perl -i -pe 's#lg>pra<#lg>man<#' lex.txt

# remove the 'extra' closing tag we added earlier
tail -n +2 lex.txt > l2.txt

echo "</sf></set></sets></reconstruction>" > tail.txt

cat header.txt l2.txt tail.txt > both.txt

xmllint --format --encode 'utf-8' both.txt > SETS0111-SRT.sets.xml

#rm both.txt tail.txt header.txt l2.txt lex.txt
