cd ../experiments/TGTM/semantics || die

python3 $1/solr_prep.py TGTM.gha.data.xml TGTM.gha.solr.xml
python3 $1/solr_prep.py TGTM.mar.data.xml TGTM.mar.solr.xml
python3 $1/solr_prep.py TGTM.pra.data.xml TGTM.pra.solr.xml
python3 $1/solr_prep.py TGTM.ris.data.xml TGTM.ris.solr.xml
python3 $1/solr_prep.py TGTM.sahu.data.xml TGTM.sahu.solr.xml
python3 $1/solr_prep.py TGTM.syang.data.xml TGTM.syang.solr.xml
python3 $1/solr_prep.py TGTM.tag.data.xml TGTM.tag.solr.xml
python3 $1/solr_prep.py TGTM.tuk.data.xml TGTM.tuk.solr.xml

#python3 $1/solr_prep.py TGTM.tag2.solr.xml
#python3 $1/solr_prep.py TGTM.tuk2.solr.xml

