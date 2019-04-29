import read
import sys
import os
import RE
import csv
import serialize

base_dir = os.path.dirname(sys.argv[1])

with open(sys.argv[1], 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter='\t')
    # get first row (header)
    for row in reader:
        header = row
        break

table_layout = [int(x) for x in sys.argv[2].split(',')]

lexicons = read.read_tabular_lexicons(sys.argv[1], table_layout)

serialize.serialize_lexicons(lexicons, base_dir)
