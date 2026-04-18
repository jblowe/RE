test:
	echo 'starting tests `date`'

	# cd src ; bash ./cleanup.sh > /dev/null

	cd src ; python3 REcli.py new-project test
	cd src ; python3 REcli.py delete-project test

	cd src ; bash ./testCSV2RE.sh
	cd src ; bash ./testCSV2lexicon.sh

	cd src ; bash ./testPROJECT.sh DIS standard
	cd src ; python3 REcli.py upstream DIS --run partial -t standard --mel hand -w --upstream 'tgtm: ris,sahu'

	cd src ; bash ./testPROJECT.sh POLYNESIAN standard

	# TODO: ROMANCE does have a 'standard' TOC, but it is not the real thing.
	cd src ; python3 REcli.py upstream ROMANCE --run standard -t standard --mel hand -w
	# TODO: the following 'works', but uses standard for all 3 tree nodes; is therefore incorrect
	cd src ; python3 REcli.py upstream ROMANCE --run none --recon standard -u "PIWR: PWR, it, scn; PWR: PIR, fr; PIR: es, pt, oldpt; "

	# the following runs the 'tree' upstream
	cd src ; python3 REcli.py upstream ROMANCE --run tree     -u "PIWR: PWR, it, scn; PWR: PIR, fr; PIR: es, pt, oldpt;"
	# the semicolon in -u is being left off deliberately to test whether in gets implied
	cd src ; python3 REcli.py upstream ROMANCE --run tree     -u "PIWR: PWR, it, scn; PWR: PIR, fr; PIR: es, pt, oldpt" --mel hand -w

	# SLAVIC has no MELs
	cd src ; python3 REcli.py upstream SLAVIC  --run none     -t standard

	cd src ; bash ./testPROJECT.sh HMONGMIEN standard

	# aspirational
	# cd src ; bash ./testPROJECT.sh EXER standard
	# cd src ; bash ./testPROJECT.sh GERMANIC standard
	# cd src ; bash ./testPROJECT.sh LOLOISH standard
	# cd src ; bash ./testPROJECT.sh VANUATU standard

benchmark:
	echo 'starting benchmark `date`'

	cd src ; bash ./testPROJECT.sh DIS standard
	cd src ; bash ./testPROJECT.sh POLYNESIAN standard
	# cd src ; bash ./testPROJECT.sh LOLOSH standard
        # echo "Start of test: ROMANCE"
	cd src ; python3 REcli.py upstream ROMANCE --run tree     -u "PIWR: PWR, it, scn; PWR: PIR, fr; PIR: es, pt, oldpt;"
	cd src ; python3 REcli.py upstream ROMANCE --run mel      -u "PIWR: PWR, it, scn; PWR: PIR, fr; PIR: es, pt, oldpt" --mel hand -w
        # echo "End of test: ROMANCE"
	cd src ; bash ./testPROJECT.sh SLAVIC standard
        # echo "Start of test: HMONGMIEN"
	cd src ; python3 REcli.py upstream HMONGMIEN --run mel  --recon standard  --mel hand -w
        # echo "End of test: HMONGMIEN"
	# cd src ; bash ./testPROJECT.sh HMONGMIEN standard
	cd src ; bash ./testPROJECT.sh DEMO93 C794DEM
	cd src ; python3 REcli.py upstream TGTM --run mel  --recon C796 --mel hand -w

