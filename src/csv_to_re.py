import read
import sys
import RE
import csv
import xml.etree.ElementTree as ET

# insert list of language names here

with open(sys.argv[1], 'r', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile, delimiter='\t')
    # get first row (header)
    for row in reader:
        languages = row[5:]
        break


table = read.read_csv_correspondences(sys.argv[1], 'placeholder', languages)

if len(sys.argv) == 4:
    root = ET.parse(sys.argv[3])
    sound_classes, regex, supra_segmentals = read.read_classes(root.findall('.//'))
else:
    sound_classes, regex, supra_segmentals = {}, None, None


RE.Parameters(table,
              RE.SyllableCanon(sound_classes, 'placeholder' if regex is None else regex, []),
              'placeholder', None).serialize(sys.argv[2])
