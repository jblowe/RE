import read
import sys
import RE
import csv

hw_col = int(sys.argv[3])

with open(sys.argv[1], 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter='\t')
    with open(sys.argv[2], 'w') as lexware_file:
        writer = csv.writer(lexware_file, delimiter='\t')
        for i, row in enumerate(reader):
            # get first row (header)
            if i == 0:
                header = row
                continue
            if len(header) != len(row):
                print('invalid row', i, row)
                continue
            writer.writerow(['.' + header[hw_col], row[hw_col]])
            for b in range(len(header)-1):
                if b == hw_col: continue
                if row[b] == '': continue
                writer.writerow([header[b], row[b]])
