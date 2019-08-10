#!/usr/bin/env bash
#
set -x

# run the csv converter for the data
python $1/csv_to_lexicon.py POLYNESIAN.data.csv "1,0, 3"

