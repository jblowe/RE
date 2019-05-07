for d in ../projects; do git clean -fd ../projects/$d -e *.statistics.txt ; done
git checkout -- ../projects/TGTM/TGTM.*.data.xml
git checkout -- ../projects/POLYNESIAN/*.data.xml
