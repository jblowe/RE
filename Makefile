test:
	echo 'starting tests'

	cd src ; bash ./cleanup.sh
	
	cd src ; bash ./testCSV2RE.sh
	cd src ; bash ./testCSV2lexicon.sh

	cd projects/RE_DATA_1994 ; bash ./tgtm_pipeline.sh
	cd src ; bash ./testTGTM.sh
	cd src ; bash ./testDEMO93.sh

	cd src ; bash ./testVanuatu.sh

	cd src ; bash ./testPolynesian.sh

	cd projects/LOLOISH ; bash ./yi_pipeline.sh
	cd src ; bash ./testYi.sh

	cd src ; bash ./testROMANCE.sh

	cd src ; python3 REcli.py -c -m hand DEMO93 > ../projects/DEMO93/DEMO93.mel.coverage.txt
	cd src ; python3 REcli.py -c -m hand TGTM > ../projects/TGTM/TGTM.mel.coverage.txt
	cd src ; python3 REcli.py -c -m hand ROMANCE > ../projects/ROMANCE/ROMANCE.mel.coverage.txt
	cd src ; python3 REcli.py -c -m hand POLYNESIAN > ../projects/POLYNESIAN/POLYNESIAN.mel.coverage.txt
	cd src ; python3 REcli.py -c -m hand NYI > ../projects/LOLOISH/NYI.mel.coverage.txt
	cd src ; python3 REcli.py -c -m hand SYI > ../projects/LOLOISH/SYI.mel.coverage.txt
