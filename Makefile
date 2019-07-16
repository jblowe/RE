test:
	echo 'starting tests `date`'

	cd src ; bash ./cleanup.sh > /dev/null
	
	cd src ; bash ./testCSV2RE.sh
	cd src ; bash ./testCSV2lexicon.sh

	cd src ; bash ./testPROJECT.sh DEMO93 semantics
	cd src ; bash ./testPROJECT.sh DIS semantics
	cd src ; bash ./testPROJECT.sh POLYNESIAN semantics
	#cd src ; bash ./testPROJECT.sh LOLOISH semantics
	cd src ; bash ./testPROJECT.sh TGTM semantics
	cd src ; bash ./testPROJECT.sh ROMANCE semantics
	#cd src ; bash ./testPROJECT.sh VANUATU semantics

	cd REwww; python3 -c "from utils import add_time_and_version;print(add_time_and_version())" >> ../updates.txt
