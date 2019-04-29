import os
import lxml.etree as ET
from xml.dom import minidom

def serialize_correspondence_file(filename, parameters):
    root = ET.Element('tableOfCorr')
    params = ET.SubElement(root, 'parameters')
    syllable_canon = parameters.syllable_canon
    for cover, values in syllable_canon.sound_classes.items():
        ET.SubElement(params, 'class', name=cover,
                      value=','.join(values))
    ET.SubElement(params, 'canon', name='syllabe',
                  value=syllable_canon.regex.pattern)
    ET.SubElement(params, 'spec', name='supra_segmentals',
                  value=','.join(syllable_canon.supra_segmentals))
    for correspondence in parameters.table.correspondences:
        corr = ET.SubElement(root, 'corr', num=correspondence.id)
        attributes = {'syll': ','.join(correspondence.syllable_types)}
        if correspondence.context[0]:
            attributes['contextL'] = ','.join(correspondence.context[0])
        if correspondence.context[1]:
            attributes['contextR'] = ','.join(correspondence.context[1])
        ET.SubElement(corr, 'proto', **attributes).text = \
            correspondence.proto_form
        for language, forms in correspondence.daughter_forms.items():
            if forms != ['']:
                modern = ET.SubElement(corr, 'modern', dialecte=language)
                for form in forms:
                    if form != '':
                        ET.SubElement(modern, 'seg').text = form
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(minidom.parseString(ET.tostring(root))
                .toprettyxml(indent='   '))

def serialize_lexicons(lexicons, dirname):
    for lexicon in lexicons:
        serialize_lexicon(
            lexicon,
            os.path.join(dirname,
                         f'{lexicon.language}.data.xml'))

def serialize_lexicon(lexicon, filename):
    root = ET.Element('lexicon', attrib={'dialecte': lexicon.language})
    for (number, form) in enumerate(lexicon.forms):
        entry = ET.SubElement(root, 'entry', attrib={'id': str(number)})
        try:
            ET.SubElement(entry, 'gl').text = form.gloss
        except:
            ET.SubElement(entry, 'gl').text = 'missing'
            print(f'error in {lexicon.language} {number} {form.glyphs} {form.gloss}')
        try:
            ET.SubElement(entry, 'hw').text = form.glyphs
        except:
            ET.SubElement(entry, 'hw').text = 'missing'
            print(f'conversion error in {lexicon.language} {number} {form.glyphs} {form.gloss}')
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(ET.tostring(root, pretty_print = True).decode("utf-8", "strict"))
