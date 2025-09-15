#!/usr/bin/env bash

# the following shell script regenerates to two "visible" versions of the tamang dictionary
# (the 'mobile version' (for phones) and the 'review version' (to print), both in xml and html)
# it also regenerates the 'internal version' that contains all bands
# so: 4 versions in all: abridge and full, in 2 formats, web and print

# the script does the following
#
# 1. runs the 'onbands' perl script to create the abridged version used for 'visible' publications
# 2. converts the two Lexware files to XML using Lex2XML.pl (borrowed from RE)
# 3. runs the two xsl stylesheets to recode the data and format it as html. does this for both
#    'full' and 'abridged' Lexware files.
# 
# the commands to update the website as shown but not executed by this script; to update the 'visible'
# versions, you'll need to do that by hand.

# the full dictionary, in text format (not MS Word!)
MASTER_LEXWARE_FILE="$1"

# create abridged lexware version
perl -p onbands13a.pl < $MASTER_LEXWARE_FILE > tamang-abridged.txt

# make a proforma copy of the full lexware dictionary, for making the internal versions
cp $MASTER_LEXWARE_FILE tamang-full.txt

for version in abridged full; do
  perl ~/GitHub/RE/src/Lex2XML.pl tamang-${version}.txt tamang-${version}.xml ${version}.log ris
  cp tamang-${version}.xml tamang-${version}-recoded.xml
  # xsltproc codage3.xsl tamang-${version}.xml > tamang-${version}-recoded.xml
  xsltproc format33_rev.xsl tamang-${version}-recoded.xml > tamang-${version}-review.html

  python render_tamang_dictionary.py tamang-${version}-recoded.xml -o tamang-${version}-mobile.html --no-minify
done

# the following is for update the github repo when the script is changed

# git add ../dicos/render_tamang_dictionary.py
# git commit -m "commit message"
# git push -v

# ... and to update the versions on website (requires authentication)
# scp -i ~/Downloads/jblowe.pem tamang-abridged-mobile.html  ubuntu@54.71.209.160:/var/www/html/TamangDictionary.html
# scp -i ~/Downloads/jblowe.pem tamang-abridged-review.html  ubuntu@54.71.209.160:/var/www/html/TamangDictionary4Review.html
