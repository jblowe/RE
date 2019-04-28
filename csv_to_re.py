import read
import sys
import RE
import csv

# insert list of language names here

with open(sys.argv[1], 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter='\t')
    # get first row (header)
    for row in reader:
        languages = row[5:]
        break


table = read.read_csv_correspondences(sys.argv[1], 'placeholder', languages)

RE.Parameters(table,
              RE.SyllableCanon({}, 'placeholder', []),
              'placeholder', None).serialize(sys.argv[2])
