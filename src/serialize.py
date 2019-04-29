import os
import lxml.etree as ET
from xml.dom import minidom
import RE

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


def serialize_sets(sets, filename):
    '''
    Here is the "classic schema" of cognate sets...

        <set>
          <id>779</id>
          <rcn>c2.c194.c23.</rcn>
          <pfm>Bse&#x2D0;</pfm>
          <ref>46 488 683 850 4674 4775 4835</ref>
          <sf>
            <rfx>
              <lg>ris</lg>
              <lx>&#xB2;se&#x2D0;</lx>
              <gl>to *know, know how</gl>
              <rn>850</rn>
              <hn>ris1119</hn>
            </rfx>
          </sf>
        </set>
    '''
    root = ET.Element('sets', attrib={'protolanguage': sets.language})

    def render_xml(element, form, level):
        if isinstance(form, RE.ModernForm):
            rfx = ET.SubElement(element, 'rfx')
            ET.SubElement(rfx, 'lg').text = form.language
            ET.SubElement(rfx, 'lx').text = form.glyphs
            ET.SubElement(rfx, 'gl').text = form.gloss
            #ET.SubElement(rfx, 'rn').text = form.id
        elif isinstance(form, RE.ProtoForm):
            ET.SubElement(element, 'pfm').text = form.glyphs
            ET.SubElement(element, 'rcn').text = RE.correspondences_as_ids(form.correspondences)
            sf = ET.SubElement(element, 'sf')
            for supporting_form in form.supporting_forms:
                render_xml(sf, supporting_form, level + 1)

    for number,form in enumerate(sets.forms):
        entry = ET.SubElement(root, 'set')
        ET.SubElement(entry, 'id').text = str(number + 1)
        render_xml(entry, form, 0)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(ET.tostring(root, pretty_print = True).decode("utf-8", "strict"))
