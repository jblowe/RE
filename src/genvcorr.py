# experiment to generate correspondences from vanuatu cognate sets.
# not quite working yet...

print('preprocessing Vanuatu data')

import toolbox.toolbox as toolbox
import sys
import os
import xml.etree.ElementTree as ET
import RE
import read
import csv
from collections import defaultdict
from xml.dom import minidom

base_dir = os.path.dirname(__file__)
filename = '../projects/VANUATU/AlexF_NorthVan-reconstructions_01.txt'
correspondence_filename = '../projects/VANUATU/VANUATU.experimental.correspondences.csv'

languages = ['hiw', 'ltg', 'lhi', 'lyp', 'vlw', 'mtp', 'lmg', 'vra', 'vrs', 'msn', 'mta', 'num', 'drg', 'kro', 'olr', 'lkn', 'mrl']

def read_toolbox_file():
    print('reading toolbox file')
    with open(filename, encoding='utf-8', errors='ignore') as file:
        pairs = toolbox.read_toolbox_file(file)
        zipped = []
        for set_number, (context, data) in enumerate(toolbox.records(pairs, ['\\pnv', '\\psm'])):
            row = []
            i = 0
            row = []
            for language in languages:
                found = ''
                for d in data:
                    (tag, value) = d
                    if tag[1:] == language and value is not None:
                        found = value
                row.append(found)
            zipped.append(row)
    return (correspondence_filename, zipped)

def syllable_type(proto):
    if proto in ['a', 'o', 'i', 'e', 'u']:
        return 'V'
    else:
        return 'C'

def context_from(string):
    if '_' not in string:
        return (None, None)
    (left_context, right_context) = string.split('_')
    # We have to punt because we cannot handle these contexts as they
    # are now.
    if 'C' in left_context or 'V' in left_context or 'ˈ' in left_context:
        left_context = None
    if 'C' in right_context or 'V' in right_context or 'ˈ' in right_context:
        right_context = None
    if left_context:
        left_context = left_context.split('/')
    if right_context:
        right_context = right_context.split('/')
    return (left_context, right_context)

def write_vanuatu_csv(filename, zipped):
    with open(filename, 'w', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t')
        left = ',context,type,proto'.split(',')

        for i, row in enumerate(zipped):
            writer.writerow([i] + left + row)

print('made correspondences')


if __name__ == "__main__":

    print('running these')
    write_vanuatu_csv(*read_toolbox_file())