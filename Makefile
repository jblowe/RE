test:
	echo 'starting tests'
	cd projects/RE_DATA_1994/ ; bash ./tgtm_pipeline.sh
	cd src ; bash ./testTGTM.sh ; bash ./testVanuatu.sh
