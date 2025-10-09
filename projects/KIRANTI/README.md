### KIRANTI dataset

##### Data
The original data spreadsheet provided by GJ is "pk2.ods"
This was saved as text .csv file "pk2.csv"

##### The two experiments

Two scripts were written to 'generate' two possible ToCs based 
on the data, using the algorithm described in e.g. Lowe 1995

* "IVF" -- segmental analysis with syllable as Initial? + Vowel + Final?
* "OR" -- "constituent" analysis, with VF? combined into one ToC element, R

#### Operation

* To run the experiments, you need to run the pipeline:
```bash
cd RE/projects/KIRANTI
./pipeline.sh
```
This creates the ToC files, based on `KIRANTI.classes.xml`, etc.
* It is best to use the provided MEL `KIRANTI.hand.mel.xml`
(borrowed from the TGTM projects)to reduce noise.