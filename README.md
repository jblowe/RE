### Make DIS files work again

```
git commit -m "initial revised TGTM 'DIS' files: unicode, character hacks handled, etc."

# make a pipeline to convert the Lexware files to XML, based on the TGTM pipeline
cp ../RE_DATA_1994/tgtm_pipeline.sh dis_pipeline.sh
vi dis_pipeline.sh

# fix the DIS versions of the Syang and Marpha files
vi SYANG.DIS
vi MAR.DIS

./dis_pipeline.sh

git add MAR.DIS
git add SYANG.DIS

git commit -m "reworks bands for Marpha and Syang 'DIS' files so the match the corresponding "real" files"

# make a suitable classes file
cp DIS.CLS DIS.classes.xml
vi DIS.classes.xml
xmllint --format DIS.classes.xml

# make TOC, using classes
python3 ../../src/csv_to_re.py DIS.TOC DIS.default.correspondences.xml DIS.classes.xml
```