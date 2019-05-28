test:
	echo 'starting tests'

	cd src ; bash ./cleanup.sh
	
	cd src ; bash ./testCSV2RE.sh
	cd src ; bash ./testCSV2lexicon.sh

	cd projects/RE_DATA_1994 ; bash ./tgtm_pipeline.sh
	cd src ; bash ./testPROJECT.sh TGTM
	cd src ; bash ./testPROJECT.sh DEMO93
	cd src ; bash ./testPROJECT.sh VANUATU
	cd src ; bash ./testPROJECT.sh POLYNESIAN

	cd projects/LOLOISH ; bash ./yi_pipeline.sh
	cd src ; bash ./testYi.sh

	cd src ; bash ./testROMANCE.sh

	cd src ; python3 REcli.py -c -m hand DEMO93 > ../projects/DEMO93/DEMO93.mel.coverage.txt
	cd src ; python3 REcli.py -c -m hand TGTM > ../projects/TGTM/TGTM.mel.coverage.txt
	cd src ; python3 REcli.py -c -m hand ROMANCE > ../projects/ROMANCE/ROMANCE.mel.coverage.txt
	cd src ; python3 REcli.py -c -m hand POLYNESIAN > ../projects/POLYNESIAN/POLYNESIAN.mel.coverage.txt
	cd src ; python3 REcli.py -c -m hand NYI > ../projects/LOLOISH/NYI.mel.coverage.txt
	cd src ; python3 REcli.py -c -m hand SYI > ../projects/LOLOISH/SYI.mel.coverage.txt
	cd src ; python3 REcli.py -c -m hand VANUATU > ../projects/VANUATU/VANUATU.mel.coverage.txt

	cd src ; python3 REcli.py DEMO93 > ../projects/DEMO93/DEMO93.mel.coverage.txt
	cd src ; python3 REcli.py TGTM > ../projects/TGTM/TGTM.mel.coverage.txt
	cd src ; python3 REcli.py ROMANCE > ../projects/ROMANCE/ROMANCE.mel.coverage.txt
	cd src ; python3 REcli.py POLYNESIAN > ../projects/POLYNESIAN/POLYNESIAN.mel.coverage.txt
	cd src ; python3 REcli.py NYI > ../projects/LOLOISH/NYI.mel.coverage.txt
	cd src ; python3 REcli.py SYI > ../projects/LOLOISH/SYI.mel.coverage.txt
	cd src ; python3 REcli.py VANUATU > ../projects/VANUATU/VANUATU.mel.coverage.txt

	cd src ; python3 REcli.py -x -- DEMO93 > ../projects/DEMO93/DEMO93.mel.coverage.txt
	cd src ; python3 REcli.py -x -- TGTM > ../projects/TGTM/TGTM.mel.coverage.txt
	cd src ; python3 REcli.py -x -- ROMANCE > ../projects/ROMANCE/ROMANCE.mel.coverage.txt
	cd src ; python3 REcli.py -x -- POLYNESIAN > ../projects/POLYNESIAN/POLYNESIAN.mel.coverage.txt
	cd src ; python3 REcli.py -x -- NYI > ../projects/LOLOISH/NYI.mel.coverage.txt
	cd src ; python3 REcli.py -x -- SYI > ../projects/LOLOISH/SYI.mel.coverage.txt
	cd src ; python3 REcli.py -x -- VANUATU > ../projects/VANUATU/VANUATU.mel.coverage.txt

