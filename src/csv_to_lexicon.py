import read
import sys
import os
import RE
import csv
import serialize

table_layout = [int(x) for x in sys.argv[2].split(',')]

lexicons = read.read_tabular_lexicons(sys.argv[1], table_layout)

serialize.serialize_lexicons(lexicons, os.path.dirname(sys.argv[1]))
