test:
	echo 'starting tests'
	cd src ; bash ./testCSV2RE.sh
	cd src ; bash ./testCSV2lexicon.sh
	cd projects/RE_DATA_1994 ; bash ./tgtm_pipeline.sh
	cd src ; bash ./testDEMO93.sh
	cd src ; bash ./testVanuatu.sh
	cd projects/LOLOISH ; bash ./yi_pipeline.sh
	cd src ; bash ./testYi.sh
