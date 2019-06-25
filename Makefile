test:
	echo 'starting tests `date`'

	cd src ; bash ./cleanup.sh
	
	cd src ; bash ./testCSV2RE.sh
	cd src ; bash ./testCSV2lexicon.sh

	cd src ; bash ./testPROJECT.sh DEMO93
	cd src ; bash ./testPROJECT.sh DIS
	cd src ; bash ./testPROJECT.sh POLYNESIAN
	cd src ; bash ./testPROJECT.sh LOLOISH
	#cd src ; bash ./testPROJECT.sh TGTM
	#cd src ; bash ./testPROJECT.sh ROMANCE
	#cd src ; bash ./testPROJECT.sh VANUATU

	cd REwww; python3 -c "from utils import add_time_and_version;print(add_time_and_version())" >> ../updates.txt
