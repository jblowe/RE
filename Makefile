test:
	echo 'starting tests `date`'

	cd src ; bash ./cleanup.sh
	
	cd src ; bash ./testCSV2RE.sh
	cd src ; bash ./testCSV2lexicon.sh

	cd src ; bash ./testPROJECT.sh TGTM
	cd src ; bash ./testPROJECT.sh DEMO93

	#cd src ; bash ./testPROJECT.sh VANUATU
	cd src ; bash ./testPROJECT.sh DIS
	cd src ; bash ./testPROJECT.sh POLYNESIAN
	cd src ; bash ./testPROJECT.sh LOLOISH
	cd src ; bash ./testPROJECT.sh ROMANCE

    # coverage
	cd src ; python3 REcli.py -c -m hand DEMO93 > ../projects/DEMO93/DEMO93.mel.coverage.txt
	cd src ; python3 REcli.py -c -m hand TGTM > ../projects/TGTM/TGTM.mel.coverage.txt
	cd src ; python3 REcli.py -c -m hand ROMANCE > ../projects/ROMANCE/ROMANCE.mel.coverage.txt
	cd src ; python3 REcli.py -c -m hand POLYNESIAN > ../projects/POLYNESIAN/POLYNESIAN.mel.coverage.txt
	cd src ; python3 REcli.py -c -m hand NYI > ../projects/LOLOISH/NYI.mel.coverage.txt
	cd src ; python3 REcli.py -c -m hand SYI > ../projects/LOLOISH/SYI.mel.coverage.txt
	cd src ; python3 REcli.py -c -m hand VANUATU > ../projects/VANUATU/VANUATU.mel.coverage.txt

    # default sets, no mel
	cd src ; python3 REcli.py DIS > ../projects/DIS/DIS.mel.coverage.txt
	cd src ; python3 REcli.py DEMO93 > ../projects/DEMO93/DEMO93.mel.coverage.txt
	cd src ; python3 REcli.py TGTM > ../projects/TGTM/TGTM.mel.coverage.txt
	cd src ; python3 REcli.py ROMANCE > ../projects/ROMANCE/ROMANCE.mel.coverage.txt
	cd src ; python3 REcli.py POLYNESIAN > ../projects/POLYNESIAN/POLYNESIAN.mel.coverage.txt
	cd src ; python3 REcli.py NYI > ../projects/LOLOISH/NYI.mel.coverage.txt
	cd src ; python3 REcli.py SYI > ../projects/LOLOISH/SYI.mel.coverage.txt
	#cd src ; python3 REcli.py VANUATU > ../projects/VANUATU/VANUATU.mel.coverage.txt

    # compare
	cd src ; python3 REcli.py -x -- DIS > ../projects/DIS/DIS.mel.compare.txt
	cd src ; python3 REcli.py -x -- DEMO93 > ../projects/DEMO93/DEMO93.mel.compare.txt
	cd src ; python3 REcli.py -x -- TGTM > ../projects/TGTM/TGTM.mel.compare.txt
	cd src ; python3 REcli.py -x -- ROMANCE > ../projects/ROMANCE/ROMANCE.mel.compare.txt
	cd src ; python3 REcli.py -x -- POLYNESIAN > ../projects/POLYNESIAN/POLYNESIAN.mel.compare.txt
	cd src ; python3 REcli.py -x -- NYI > ../projects/LOLOISH/NYI.mel.compare.txt
	cd src ; python3 REcli.py -x -- SYI > ../projects/LOLOISH/SYI.mel.compare.txt
	cd src ; python3 REcli.py -x -- VANUATU > ../projects/VANUATU/VANUATU.mel.compare.txt

	cd REwww; python3 -c "from utils import add_time_and_version;print(add_time_and_version())" >> ../updates.txt
