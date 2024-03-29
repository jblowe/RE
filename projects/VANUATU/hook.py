print('preprocessing Vanuatu data')

import toolbox
import sys
import os
import glob
import collections
import xml.etree.ElementTree as ET
import regex as re
import RE
import read
import csv
from collections import defaultdict
from xml.dom import minidom

base_dir = os.path.dirname(__file__)
filename = os.path.join(base_dir, 'AlexF_NorthVan-reconstructions_01.txt')
correspondence_filenames = [os.path.basename(f) for f in glob.glob(os.path.join(base_dir, '*.correspondences.csv'))]

languages = ['hiw', 'ltg', 'lhi', 'lyp', 'vlw', 'mtp', 'lmg', 'vra', 'vrs', 'msn', 'mta', 'num', 'drg', 'kro', 'olr', 'lkn', 'mrl']

def read_toolbox_file():
    print('reading toolbox file')
    with open(filename, encoding='utf-8', errors='ignore') as file:
        pairs = toolbox.read_toolbox_file(file)
        zipped = defaultdict(list)
        mels = defaultdict(list)
        for set_number, (context, data) in enumerate(toolbox.records(pairs, ['\\pnv', '\\psm'])):
            mel = set()
            proto_gloss = context['\\psm']
            mel.add(proto_gloss)
            i = 0
            while (i < len(data) - 1):
                (tag, value) = data[i]
                if tag[1:] in languages and value:
                    # precisiate data to be used by RE
                    # 1. extract gloss first (even if it's corresponding form is not used
                    gloss = proto_gloss
                    if data[i + 1][0] == '\\sem':
                        gloss = data[i + 1][1]
                        i += 1
                    else:
                        # the ith+2 element might not exist...
                        try:
                            if data[i + 2][0] == '\\sem':
                                gloss = data[i + 2][1]
                                i += 1
                        except:
                            pass
                    # 2. 'fix' the forms themselves
                    # skip forms that contain '{' (i.e. assume these are bracketed forms '{xxx}')
                    v2 = value
                    if '{' in value:
                        # print(f'skipping {value}')
                        i += 1
                        continue
                    # skip forms that contain '('
                    if '(' in value:
                        value = re.sub(r' *\((.*?)\) *', r'', value).strip()
                        if not value:
                            # print(f'skipping {v2}')
                            i += 1
                            continue
                    value = value.replace('??', '').strip()
                    value = re.sub(r'^n\-', '', value)
                    value = re.sub(r'^n.\-', '', value)
                    value = value.replace('-k', '').replace('-n', '')
                    value = re.sub(r'^.*?\\','', value)
                    value = re.sub(r'/.*?$','', value)
                    value = re.sub(r'\-.*$', '', value)
                    value = re.sub(r'\?', '', value)
                    value = value.strip()
                    if v2 != value:
                        # print(f'before: {v2} :: after {value}')
                        pass
                    zipped[tag[1:]].append((value, gloss, set_number + 1))
                    if gloss:
                        mel.add(gloss)
                i += 1
            mels[set_number] = mel
    return (zipped, mels)

def syllable_type(proto):
    if proto in ['a', 'o', 'i', 'e', 'u']:
        return 'V'
    else:
        return 'C'

def context_from(string):
    if '_' not in string:
        return (None, None)
    (left_context, right_context) = string.split('_')
    string = string.strip(')')
    string = string.strip('(')
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

def read_vanuatu_csv(filename):
    table = RE.TableOfCorrespondences('VANUATU', languages)
    with open(filename, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        # element of redundancy here, but we can't assume order
        skipped = read.skip_comments(reader)
        names = next(skipped)[5:]
        print(names)
        for (number, row) in enumerate(skipped):
            table.add_correspondence(RE.Correspondence(
                # str(number), context_from(row[2]), syllable_type(row[1]), row[1],
                row[0], context_from(row[2]), row[4].split(','), row[1],
                dict(zip(names, (x.split('|') for x in row[5:])))))
    sound_classes = collections.defaultdict(list)
    for c in table.correspondences:
        for type in c.syllable_types:
            if type in 'CVcv':
                if c.proto_form not in sound_classes[type]:
                    sound_classes[type].append(c.proto_form)
    return table, sound_classes

for corr_file in correspondence_filenames:
    correspondence_filename = os.path.join(base_dir, corr_file)
    table, sound_classes = read_vanuatu_csv(correspondence_filename)
    # TODO: fix this hack regarding canons
    if 'standard' in corr_file: canon = '(c?v)?(C?Vc?w)+'
    elif 'experimental' in corr_file: canon = '(c?vc?)?(C?Vc?)+'
    else: canon = '(c?v)?(C?Vc?w)+'
    RE.Parameters(table,
                  RE.SyllableCanon(sound_classes, canon, [], 'glyphs'),
                  'pnv', None).serialize(
                      os.path.join(base_dir, corr_file.replace('.csv','.xml')))
    print(f'made correspondence xml from {corr_file}')

def xml_name(x):
    return x + '.data.xml'

def write_vanuatu_data(zipped, mels):
    print('converting from toolbox format')
    for language in languages:
        root = ET.Element('lexicon', attrib={'dialecte': language})
        for (number, (glyphs, gloss, set_number)) in enumerate(zipped[language]):
            entry = ET.SubElement(root, 'entry', attrib={'id': str(set_number)})
            ET.SubElement(entry, 'hw').text = glyphs
            ET.SubElement(entry, 'gl').text = gloss or 'placeholder'
        with open(os.path.join(base_dir, xml_name(language)), 'w', encoding='utf-8') as f:
            f.write(minidom.parseString(ET.tostring(root))
                    .toprettyxml(indent='   '))

    root = ET.Element('semantics')
    for mel in mels:
        entry = ET.SubElement(root, 'mel', attrib={'id': str(mel + 1)})
        if mel == 0: continue
        for gloss in sorted(mels[mel]):
            ET.SubElement(entry, 'gl').text = gloss
    with open(os.path.join(base_dir, 'VANUATU.hand.mel.xml'), 'w', encoding='utf-8') as f:
        f.write(minidom.parseString(ET.tostring(root))
                .toprettyxml(indent='   '))
    print('conversion complete')

def write_parameters_file():
    root = ET.Element('params')
    for language in languages:
        ET.SubElement(root, 'attested', attrib={'name': language,
                                                'file': xml_name(language)})

    ET.SubElement(root, 'mel', attrib={'name': 'clics', 'file': 'VANUATU.clics.mel.xml'})
    ET.SubElement(root, 'mel', attrib={'name': 'hand', 'file': 'VANUATU.hand.mel.xml'})
    ET.SubElement(root, 'mel', attrib={'name': 'wordnet', 'file': 'VANUATU.wordnet.mel.xml'})
    for corr_file in correspondence_filenames:
        recon = ET.SubElement(root, 'reconstruction', attrib={'name': corr_file.replace('.correspondences.csv','').replace('VANUATU.','')})
        ET.SubElement(recon, 'proto_language',
                      attrib={'name': 'pvn',
                              'correspondences': corr_file.replace('.csv','.xml')})
        ET.SubElement(recon, 'action', attrib={'name': 'upstream',
                                               'target': 'pvn'})
        ET.SubElement(recon, 'action', attrib={'name': 'upstream',
                                               'from': ','.join(languages),
                                               'to': 'pvn'})
    with open(os.path.join(base_dir, 'VANUATU.generated.parameters.xml'), 'w', encoding='utf-8') as f:
        f.write(minidom.parseString(ET.tostring(root))
                .toprettyxml(indent='   '))
    print('parameters file written')

def run_load_hooks(arg, settings):
    print('running these')
    write_vanuatu_data(*read_toolbox_file())
    write_parameters_file()
