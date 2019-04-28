test:
	echo 'starting tests'
	cd projects/RE_DATA_1994/ ; bash ./tgtm_pipeline.sh
	cd src ; bash ./testTGTM.sh
        cd src ; bash ./testVanuatu.sh
        cd src ; bash ./testCSV2RE.sh
        cd src ; bash ./testCSV2lexicon.sh

