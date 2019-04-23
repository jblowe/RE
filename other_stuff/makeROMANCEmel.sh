# how i made the ROMANCE mel...
#
# nb: not really an executable script. you need to edit some of the intermediate files
#
perl -pe 's/^.*?: (.*)/<gl>\1<\/gl>/;s/.*\*.*/<\/mel><mel id=xxx>/' ROMANCE.default.sets.txt | uniq > m1
perl -pe 'chomp;s/(\/mel>)/\1\n/' m1 | sort | uniq > m2
vi m2
sort -u m2 > m3
perl -pe '$i++ if /id=/;s/xxx/"rom-wn$i"/' m3 > m4
vi m4 
xmllint --format m4 > ROMANCE.mel.xml
cp ROMANCE.default.parameters.xml ROMANCE.withmel.parameters.xml
vi ROMANCE.withmel.parameters.xml 
git add ROMANCE.mel.*
git add ROMANCE.withmel.parameters.xml 
git commit -m "initial MEL, and parameters, for ROMANCE"
