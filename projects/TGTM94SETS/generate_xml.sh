echo "<lexicon dialecte=\"gha\">" > gha.txt
echo "<lexicon dialecte=\"mar\">" > mar.txt
echo "<lexicon dialecte=\"pra\">" > pra.txt
echo "<lexicon dialecte=\"ris\">" > ris.txt
echo "<lexicon dialecte=\"sahu\">" > sahu.txt
echo "<lexicon dialecte=\"syang\">" > syang.txt
echo "<lexicon dialecte=\"tag\">" > tag.txt
echo "<lexicon dialecte=\"tuk\">" > tuk.txt

perl -pe 's/&/&amp;/g;s/</&lt;/g;s/>/&gt;/g;s/\.$//;' SETS0111-SRT > l1.txt

perl -ne 'next if (/^\d+\./);$i++;s#^\t(.*)\t(.*?)\t(.*)#<entry id="\1.xxx"><hw>\2</hw><gl>\3</gl></entry>#;print' l1.txt > lex.txt

perl -ne 'print if /gha\./' lex.txt | sort -u | perl -pe '$i++;s/xxx/$i/' >>  gha.txt
perl -ne 'print if /mar\./' lex.txt | sort -u | perl -pe '$i++;s/xxx/$i/' >>  mar.txt
perl -ne 'print if /pra\./' lex.txt | sort -u | perl -pe '$i++;s/xxx/$i/' >>  pra.txt
perl -ne 'print if /ris\./' lex.txt | sort -u | perl -pe '$i++;s/xxx/$i/' >>  ris.txt
perl -ne 'print if /sahu\./' lex.txt | sort -u | perl -pe '$i++;s/xxx/$i/' >>  sahu.txt
perl -ne 'print if /syang\./' lex.txt | sort -u | perl -pe '$i++;s/xxx/$i/' >>  syang.txt
perl -ne 'print if /tag\./' lex.txt | sort -u | perl -pe '$i++;s/xxx/$i/' >>  tag.txt
perl -ne 'print if /tuk\./' lex.txt | sort -u | perl -pe '$i++;s/xxx/$i/' >>  tuk.txt

echo "</lexicon>" >> gha.txt
echo "</lexicon>" >> mar.txt
echo "</lexicon>" >> pra.txt
echo "</lexicon>" >> ris.txt
echo "</lexicon>" >> sahu.txt
echo "</lexicon>" >> syang.txt
echo "</lexicon>" >> tag.txt
echo "</lexicon>" >> tuk.txt

xmllint --format gha.txt > gha.x
xmllint --format mar.txt > mar.x
xmllint --format pra.txt > pra.x
xmllint --format ris.txt > ris.x
xmllint --format sahu.txt > sahu.x
xmllint --format syang.txt > syang.x
xmllint --format tag.txt > tag.x
xmllint --format tuk.txt > tuk.x

perl -i -pe 's# *\[+ *(.*)<.hw>#</hw><srcxcr1>\1</srcxcr1>#;s#\-</hw>#</hw>#;s#\.</gl>#</gl>#' *.x
perl -i -pe 's#(<hw>)(.+?)[ \-=](.*)</hw>#\1\2</hw><srcxcr2>\3</srcxcr2>#' *.x
perl -i -pe 's#(<hw>)[\-=](.*)</hw>#\1\2</hw>#' *.x
perl -i -pe 's/\&#x303;([^<])/\1\&#x303;/g' *.x
perl -i -pe 's/ae\&#x303;/ae\&#771;/g' *.x

xmllint --format --encode 'utf-8' gha.x > TGTM.gha.data.xml
xmllint --format --encode 'utf-8' mar.x > TGTM.mar.data.xml
xmllint --format --encode 'utf-8' pra.x > TGTM.pra.data.xml
xmllint --format --encode 'utf-8' ris.x > TGTM.ris.data.xml
xmllint --format --encode 'utf-8' sahu.x > TGTM.sahu.data.xml
xmllint --format --encode 'utf-8' syang.x > TGTM.syang.data.xml
xmllint --format --encode 'utf-8' tag.x > TGTM.tag.data.xml
xmllint --format --encode 'utf-8' tuk.x > TGTM.tuk.data.xml

rm *.x *.txt

