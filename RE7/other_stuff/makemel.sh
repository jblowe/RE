# might help!
cut -f3 results.csv > x0
sort -u x0 > x1
grep ',' x1 > x2
perl -pe 's/,/<\/gl>\n<gl>/g; print "</gl>\n</mel>\n<mel id=xxx>\n<gl>"' x2 > x3
perl -pe '$i++ if /id=/;s/xxx/"wn$i"/' x3 > x4
xmllint --format x4 > x5.xml
perl -pe 'tr/[A-Z]/[a-z]/' x5.xml  > TGTM.mel-wn.xml
