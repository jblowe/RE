### Vanuatu data

Alex François

in Toolbox format

How to make a "tabular" HTML version of the ToC

```
cd .../RE7/DATA/VANUATU
xsltproc ../../styles/toc2html.xsl VANUATU.correspondences.xml > vanuatu.html
```

How to process "upstream", using the defaults

(to use different parameters, look inside ```testVanuatu.sh``` -- you may need to edit various files in
the VANUATU directory as well)

```
cd .../RE8.2
./testVanuatu.sh
```

Notes

* This script uses a "SIL Toolbox File Module" (https://github.com/goodmami/toolbox.git)
* It reads the Toolbox file and outputs XML data files and XML parameter files for RE.