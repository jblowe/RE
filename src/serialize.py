import os
import time
import collections
import lxml.etree as ET
from xml.dom import minidom
import RE
import inspect

run_date = f'{time.asctime()}'

def serialize_correspondence_file(filename, parameters):
    root = ET.Element('tableOfCorr')
    ET.SubElement(root, 'createdat').text = run_date
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

def serialize_lexicons(lexicons, dirname, ext='.data.xml'):
    for lexicon in lexicons:
        serialize_lexicon(
            lexicon,
            os.path.join(dirname,
                         f'{lexicon.language}{ext}'))

def serialize_lexicon(lexicon, filename):
    root = ET.Element('lexicon', attrib={'dialecte': lexicon.language})
    ET.SubElement(root, 'createdat').text = run_date

    for (number, form) in enumerate(lexicon.forms):
        entry = ET.SubElement(root, 'entry', attrib={'id': f'{lexicon.language.lower()}.{number + 1}'})
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
    ET.SubElement(root, 'createdat').text = run_date

    def render_xml(element, form, level):
        if isinstance(form, RE.ModernForm):
            rfx = ET.SubElement(element, 'rfx')
            ET.SubElement(rfx, 'lg').text = form.language
            ET.SubElement(rfx, 'lx').text = form.glyphs
            ET.SubElement(rfx, 'gl').text = form.gloss
            ET.SubElement(rfx, 'id').text = form.id
        elif isinstance(form, RE.ProtoForm):
            if level != 0:
                element = ET.SubElement(element, 'subset', attrib={'level': str(level)})
            ET.SubElement(element, 'id').text = f'%s.%s' % (number + 1, level)
            ET.SubElement(element, 'plg').text = form.language
            ET.SubElement(element, 'pfm').text = form.glyphs
            if form.mel:
                ET.SubElement(element, 'mel').text = ', '.join(form.mel.glosses)
                ET.SubElement(element, 'melid').text = form.mel.id
            else:
                pass
            ET.SubElement(element, 'rcn').text = RE.correspondences_as_ids(form.correspondences).strip()
            sf = ET.SubElement(element, 'sf')
            for supporting_form in sorted(form.supporting_forms, key=lambda x: x.language):
                render_xml(sf, supporting_form, level + 1)

    for number,form in enumerate(sorted(sets.forms, key=lambda corrs: RE.correspondences_as_ids(corrs.correspondences))):
        entry = ET.SubElement(root, 'set')
        render_xml(entry, form, 0)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(ET.tostring(root, pretty_print = True).decode("utf-8", "strict"))


def serialize_stats(stats, filename):
    root = ET.Element('stats', attrib={'project': 'foo'})
    ET.SubElement(root, 'createdat').text = run_date

    lexicons = ET.SubElement(root, 'lexicons')
    totals = collections.Counter()
    for number, language in enumerate(sorted(stats.language_stats.keys())):
        entry = ET.SubElement(lexicons, 'lexicon', attrib={'language': language})
        for stat in stats.language_stats[language].keys():
            ET.SubElement(entry, stat).set('value', str(stats.language_stats[language][stat]))
            totals[stat] += stats.language_stats[language][stat]

    runstats = ET.SubElement(root, 'totals')
    for s in totals:
        ET.SubElement(runstats, s).set('value', str(totals[s]))

    #print(inspect.getmembers(stats))
    for name, value in stats.summary_stats.items():
        ET.SubElement(runstats, name).set('value', str(stats.summary_stats[name]))

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(ET.tostring(root, pretty_print = True).decode("utf-8", "strict"))


def serialize_evaluation(stats, filename):
    root = ET.Element('stats', attrib={'project': 'foo'})
    ET.SubElement(root, 'createdat').text = run_date

    entry = ET.SubElement(root, 'totals')
    for k, v in stats.items():
        if type(v) == type(()):
            element = ET.SubElement(entry, k)
            element.set('value', str(v[0]))
            element.set('type', str(v[1]))
        else:
            ET.SubElement(entry, k).set('value', str(v))

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(ET.tostring(root, pretty_print = True).decode("utf-8", "strict"))

