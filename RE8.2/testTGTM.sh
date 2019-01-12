python REcompare.py TGTM TGTM.default.parameters.xml TGTM.withoutmel.parameters.xml
echo 'No mel to gold stats'
head ../RE7/DATA/TGTM/TGTM.default.analysis.txt

python REcompare.py TGTM TGTM.default.parameters.xml TGTM.mel-wn.parameters.xml
echo 'WordNet to gold stats'
head ../RE7/DATA/TGTM/TGTM.default.analysis.txt

python REcompare.py TGTM TGTM.default.parameters.xml TGTM.mel-wn-pairs.parameters.xml
echo 'WordNet pairs to gold stats'
head ../RE7/DATA/TGTM/TGTM.default.analysis.txt

python REcompare.py TGTM TGTM.default.parameters.xml TGTM.mel-clics.parameters.xml
echo 'Clics to gold stats'
head ../RE7/DATA/TGTM/TGTM.default.analysis.txt
