#
# generate 2 experimental tocs for Kiranti data
#
# generate 'trial' toc.csv files from data
python ../../src/split_segments.py pk2-feuille1.csv KIRANTI.experiment_IVF
python ../../src/split_constituents.py pk2-feuille1.csv KIRANTI.experiment_OR
#
# transform .csv tocs to xml
python3 ../../src/csv_to_re.py KIRANTI.experiment_IVF.correspondences.csv KIRANTI.experiment_IVF.correspondences.xml KIRANTI.classes.xml
python3 ../../src/csv_to_re.py KIRANTI.experiment_OR.correspondences.csv KIRANTI.experiment_OR.correspondences.xml KIRANTI.classes.xml
perl -i -pe 's/(name="syllabe" value=").*?"/\1O?RS?"/' KIRANTI.experiment_OR.correspondences.xml

