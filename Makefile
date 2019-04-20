test:
	echo 'starting tests'
	cd RE7/DATA/RE_DATA_1994/ ; bash ./tgtm_pipeline.sh
	cd RE8.2 ; bash ./testTGTM.sh
