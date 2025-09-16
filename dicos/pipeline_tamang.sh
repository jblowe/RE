#!/usr/bin/env bash

# the following shell script regenerates to three versions of the tamang dictionary
# (the 'mobile version' (for phones) and the 'review version' (to print for review),
# and the 'full version', which contains all bands, for internal use)
# the versions are produced both in xml and html)
# so: 6 versions in all: mobile, review and full, in 2 formats, web and print

# the script does the following
#
# 1. runs an 'onbands' perl script to create the versions of Lexware file used for the 3 use cases.
# 2. converts the three Lexware files to XML using Lex2XML.pl (borrowed from RE)
# 3. runs the xsl stylesheet to recode the tamang and nepali transcriptions.
#    it does this for both 'full' and 'review' Lexware files. The mobile version does this itself.
# 
# the commands to update the website as shown but not executed by this script; to update the 'visible'
# versions, you'll need to do that by hand.

# the full dictionary, in text format (not MS Word!)
MASTER_LEXWARE_FILE="$1"

for version in mobile review full; do
  # create lexware versions with bands as needed
  perl -p onbands_for_${version}.pl < $MASTER_LEXWARE_FILE > tamang-${version}.txt
  # convert to xml
  perl ~/GitHub/RE/src/Lex2XML.pl tamang-${version}.txt tamang-${version}-converted.xml ${version}.log ris
  # xsltproc codage3.xsl tamang-${version}.xml > tamang-${version}-recoded.xml
  cp tamang-${version}-converted.xml tamang-${version}-recoded.xml
  # format the 'print' versions
  xsltproc format33_rev.xsl tamang-${version}-recoded.xml > tamang-${version}-4print.html
  # format the 'mobile' versions. no recoding required, the script does it all
  python render_tamang_dictionary.py tamang-${version}-converted.xml -o tamang-${version}-4mobile.html --no-minify
done

# the following is for updating the github repo when the script is changed

# git add ../dicos/render_tamang_dictionary.py
# git commit -m "commit message"
# git push -v

# ... and to update two versions on website (requires authentication)
# scp -i ~/Downloads/jblowe.pem tamang-mobile-4mobile.html  ubuntu@54.71.209.160:/var/www/html/TamangDictionary.html
# scp -i ~/Downloads/jblowe.pem tamang-review-4print.html  ubuntu@54.71.209.160:/var/www/html/TamangDictionary4Review.html
