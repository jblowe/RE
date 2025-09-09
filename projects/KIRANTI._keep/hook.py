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
filename = os.path.join(base_dir, 'proto-kiranti - Feuille1.csv')
correspondence_filename = 'kiranti.correspondence.csv'

languages = ['khaling1', 'khaling2', 'wambule', 'limbu1', 'limbu2', 'bantawa']

# from sheet 1
def read_tabular_lexicons(filename, delimiter=','):
    index_map = {'khaling1': (3, 5),
                 'khaling2': (7, 8),
                 'wambule': (9, 10),
                 'limbu1': (11, 12),
                 'limbu2': (13, 14),
                 'bantawa': (15, 16)}
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
