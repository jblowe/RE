#!/usr/bin/env bash
#
set -x

# run the csv converter for the data
python3 ../../src/csv_to_lexicon.py POLYNESIAN.data.csv "1,0, 3"

