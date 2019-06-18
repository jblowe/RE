print('preprocessing Vanuatu data')

import toolbox
import sys
import os
import xml.etree.ElementTree as ET
import RE
import read
import csv
from collections import defaultdict
from xml.dom import minidom

base_dir = os.path.dirname(__file__)
filename = os.path.join(base_dir, 'AlexF_NorthVan-reconstructions_01.txt')
correspondence_filename = os.path.join(base_dir, 'VANUATU.experimental.correspondences.csv')

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
                    value = value.replace('{', '').replace('}', '').replace('na-', '')
                    gloss = proto_gloss
                    if data[i + 1][0] == '\\sem':
                        gloss = data[i + 1][1]
                        i += 1
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
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        # element of redundancy here, but we can't assume order
        skipped = read.skip_comments(reader)
        names = next(skipped)[5:]
        print(names)
        for (number, row) in enumerate(skipped):
            print(row)
            table.add_correspondence(RE.Correspondence(
                str(number), context_from(row[2]), syllable_type(row[1]), row[1],
                dict(zip(names, (x.split('|') for x in row[5:])))))
    return table

RE.Parameters(read_vanuatu_csv(correspondence_filename),
              RE.SyllableCanon({}, '(CV)+', []),
              'pnv', None).serialize(
                  os.path.join(base_dir, 'VANUATU.correspondences.xml'))

print('made correspondence xml')

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
    recon = ET.SubElement(root, 'reconstruction', attrib={'name': 'default'})
    ET.SubElement(recon, 'proto_language',
                  attrib={'name': 'pvn',
                          'correspondences': 'VANUATU.correspondences.xml'})
    ET.SubElement(recon, 'action', attrib={'name': 'upstream',
                                           'target': 'pvn'})
    ET.SubElement(recon, 'action', attrib={'name': 'upstream',
                                           'from': ','.join(languages),
                                           'to': 'pvn'})
    with open(os.path.join(base_dir, 'VANUATU.default.parameters.xml'), 'w', encoding='utf-8') as f:
        f.write(minidom.parseString(ET.tostring(root))
                .toprettyxml(indent='   '))
    print('parameters file written')

def run_load_hooks(settings):
    print('running these')
    write_vanuatu_data(*read_toolbox_file())
    write_parameters_file()
