### Make DIS files work again

The "original files" in Lexware and "tab-delimited formats" are:

```
# ToC and Classes
DIS.CLS 
DIS.TOC

# data files (Lexware format)
GHA.DIS
MAN.DIS
MAR.DIS
RIS.DIS
SAHU.DIS
SYANG.DIS
TAG.DIS
TUK.DIS
```

The "pipeline" script mentioned below takes these data files and converts them to XML that RE can process.

In addtion, these 4 files need to be properly created for RE to work:

```
DIS.classes.xml
DIS.default.correspondences.xml
DIS.default.parameters.xml
DIS.hand.mel.xml
```

Here's a précis of how this small example dataset was modernized to work with the new RE:

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
