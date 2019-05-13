print('preprocessing Vanuatu data')

import toolbox
import sys
import os
import xml.etree.ElementTree as ET
from collections import defaultdict
from xml.dom import minidom

base_dir = os.path.dirname(__file__)
filename = os.path.join(base_dir, 'AlexF_NorthVan-reconstructions_01.txt')

languages = ['hiw', 'ltg', 'lhi', 'lyp', 'vlw', 'mtp', 'lmg', 'vra', 'vrs', 'msn', 'mta', 'num', 'drg', 'kro', 'olr', 'lkn', 'mrl']

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
                gloss = proto_gloss
                if data[i + 1][0] == '\\sem':
                    gloss = data[i + 1][1]
                    i += 1
                zipped[tag[1:]].append((value, gloss))
                if gloss:
                    mel.add(gloss)
            i += 1
        mels[set_number] = mel


def xml_name(x):
    return x + '.data.xml'


def write_vanuatu_data():
    for language in languages:
        root = ET.Element('lexicon', attrib={'dialecte': language})
        for (number, (glyphs, gloss)) in enumerate(zipped[language]):
            entry = ET.SubElement(root, 'entry', attrib={'id': str(number + 1)})
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


print('converting from toolbox format')

write_vanuatu_data()
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


write_parameters_file()
print('parameters file written')
