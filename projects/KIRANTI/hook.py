print('preprocessing Kiranti data')

import sys
import os
import glob
import collections
import xml.etree.ElementTree as ET
import regex as re
import RE
import serialize
import read
import csv
from collections import defaultdict
from xml.dom import minidom

base_dir = os.path.dirname(__file__)
filename = os.path.join(base_dir, 'pk2-feuille1.csv')
correspondence_filename = 'KIRANTI.jbl.correspondences.csv'

languages = ['khaling', 'wambule', 'limbu', 'bantawa']

# from sheet 1
def read_tabular_lexicons(filename, delimiter='\t'):
    index_map = {'khaling': (5, 6),
                 'wambule': (3, 4),
                 'limbu': (11, 12),
                 'bantawa': (8, 10)}
    with open(filename, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter)
        # element of redundancy here, but we can't assume order
        n1 = list(read.skip_comments(reader))
        #names = [x.strip() for x in list(skip_comments(reader))[data_start_column:]]
        forms_dict = {name: [] for name in languages}
        for row in n1[1:]:
            for language, (form_column, gloss_column) in index_map.items():
                forms = row[form_column]
                gloss = row[gloss_column]
                forms = forms.strip()
                for form in re.split(' |,|, ', forms):
                    if form:
                        form = form.strip('(')
                        form = form.strip(')')
                        str_id = 'irrelevant' # KLUDGE: serialize obliterates this
                        forms_dict[language].append(RE.ModernForm(language, form, gloss, str_id))
        return [RE.Lexicon(language, forms, []) for language, forms in forms_dict.items()]

def run_load_hooks(arg, settings):
    print('creating lexicons')
    serialize.serialize_lexicons(read_tabular_lexicons(filename), base_dir)
