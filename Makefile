test:
	echo 'starting tests `date`'

	#cd src ; bash ./cleanup.sh > /dev/null
	rm -rf experiments/*/semantics

	cd src ; python3 REcli.py new-experiment DIS test
	cd src ; python3 REcli.py delete-experiment DIS test

	cd src ; bash ./testCSV2RE.sh
	cd src ; bash ./testCSV2lexicon.sh

	cd src ; bash ./testPROJECT.sh DEMO93 semantics
	cd src ; bash ./testPROJECT.sh DIS semantics
	cd src ; bash ./testPROJECT.sh POLYNESIAN semantics
	cd src ; bash ./testPROJECT.sh LOLOISH semantics

	rm -f experiments/LOLOISH/*/*.json
	rm -f experiments/LOLOISH/*/*.keys.csv

	cd src ; bash ./testPROJECT.sh TGTM semantics
	#cd src ; bash ./testPROJECT.sh ROMANCE semantics
	#cd src ; bash ./testPROJECT.sh VANUATU semantics

	rm experiments/HMONGMIEN/*/*.json
	rm experiments/VANUATU/*/*.json
	rm experiments/VANUATU/*/*.keys.csv

	cd REwww; python3 -c "from utils import add_time_and_version;print(add_time_and_version())" >> ../updates.txt
