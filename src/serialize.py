import os
import time
import collections
import lxml.etree as ET
from xml.dom import minidom
import RE
import utils
import inspect
import pickle

run_date = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

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
    ET.SubElement(params, 'context_match_type', name='context_match_type',
                  value=syllable_canon.context_match_type)
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
        f.write(ET.tostring(root, pretty_print=True, encoding='unicode'))

def create_xml_sets(reconstruction, languages, only_with_mel):
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
    root = ET.Element('reconstruction', attrib={'protolanguage': reconstruction.language})
    ET.SubElement(root, 'createdat').text = run_date
    lgs = ET.SubElement(root, 'languages')
    for language in languages:
        ET.SubElement(lgs, 'lg').text = language

    def sort_forms(form, sf, level):
        # we need to output the supporting forms in the order specified by "languages"
        unfrozenset = [x for x in form.supporting_forms]
        lglist = [x.language for x in form.supporting_forms]
        for language in languages:
            try:
                indices = [i for i, x in enumerate(lglist) if x == language]
                for i in indices:
                    supporting_form = unfrozenset[i]
                    render_xml(sf, supporting_form, level + 1)
            except:
                pass
        return

    def add_protoform_element(element, protoform):
        ET.SubElement(element, 'plg').text = protoform.language
        ET.SubElement(element, 'pfm').text = protoform.glyphs
        ET.SubElement(element, 'rcn').text = RE.correspondences_as_ids(protoform.correspondences).strip()

    def render_xml(element, form, level):

        # handle 'strict' case: possibly output a set with multiple reconstructions
        if isinstance(form, list):
            if level != 0:
                element = ET.SubElement(element, 'subset', attrib={'level': str(level)})
            ET.SubElement(element, 'id').text = f'%s.%s' % (number + 1, level)
            if len(form) > 1:
                for protoform in form:
                    reconstruction_block = ET.SubElement(element, 'multi')
                    add_protoform_element(reconstruction_block, protoform)
            else:
                add_protoform_element(element, form[0])
            if form[0].mel:
                ET.SubElement(element, 'mel').text = ', '.join(form[0].mel.glosses)
                ET.SubElement(element, 'melid').text = form[0].mel.id
            else:
                pass
            sf = ET.SubElement(element, 'sf')
            sort_forms(form[0], sf, level)

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
            add_protoform_element(element, form)
            sf = ET.SubElement(element, 'sf')
            sort_forms(form, sf, level)

    sets = ET.SubElement(root, 'sets')

    # if 'strict' is on, squish the sets before output
    if only_with_mel:
        uniques = collections.defaultdict(list)
        for form in sorted(reconstruction.forms, key=lambda corrs: RE.correspondences_as_ids(corrs.correspondences)):
            uniques[form.supporting_forms].append(form)

        for number,set in enumerate(sorted(uniques.items(), key=lambda recons: RE.correspondences_as_ids(recons[1][0].correspondences))):
            entry = ET.SubElement(sets, 'set')
            render_xml(entry, set[1], 0)


    # otherwise, make sets the 'usual' way
    else:
        for number,form in enumerate(sorted(reconstruction.forms, key=lambda corrs: RE.correspondences_as_ids(corrs.correspondences))):
            entry = ET.SubElement(sets, 'set')
            render_xml(entry, form, 0)

    isolates = ET.SubElement(root, 'isolates')
    for number,form in enumerate(sorted(reconstruction.isolates, key=lambda corrs: RE.correspondences_as_ids(corrs.correspondences))):
        entry = ET.SubElement(isolates, 'set')
        render_xml(entry, form, 0)

    failures = ET.SubElement(root, 'failures')
    entry = ET.SubElement(failures, 'set')
    # there is only one (big) set for failures
    render_xml(entry, reconstruction.failures, 0)

    return root

def serialize_sets(reconstruction, languages, filename, only_with_mel):
    root = create_xml_sets(reconstruction, languages, only_with_mel)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(ET.tostring(root, pretty_print=True, encoding='unicode'))

def serialize_stats(stats, settings, args, filename):
    root = ET.Element('stats', attrib={'project': 'foo'})
    ET.SubElement(root, 'createdat').text = run_date

    settings_element = ET.SubElement(root, 'settings')
    try:
        ET.SubElement(settings_element, 'parm',attrib={'key': 'run', 'value': str(args.run)})
        ET.SubElement(settings_element, 'parm',attrib={'key': 'mel_filename', 'value': str(settings.mel_filename)})
        ET.SubElement(settings_element, 'parm',attrib={'key': 'correspondences', 'value': settings.proto_languages[settings.upstream_target]})
        ET.SubElement(settings_element, 'parm',attrib={'key': 'strict', 'value': str(args.only_with_mel)})
        try:
            ET.SubElement(settings_element, 'parm',attrib={'key': 'fuzzyfile', 'value': settings.other['fuzzy']})
        except:
            ET.SubElement(settings_element, 'parm', attrib={'key': 'fuzzyfile', 'value': 'No fuzzying done.'})
    except:
        pass
    # for s in settings.other:
    #     ET.SubElement(settings_element, s).set('value', settings.other[s])

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

    corrs = ET.SubElement(root, 'correspondences')
    for c in sorted(stats.correspondences_used_in_recons, key=lambda corr: utils.tryconvert(corr.id, int)):
        if c in stats.correspondences_used_in_sets:
            set_count = stats.correspondences_used_in_sets[c]
        else:
            set_count = 0
        corr = ET.SubElement(corrs, 'correspondence', attrib={'value': str(c)})
        ET.SubElement(corr, 'used_in_reconstructions').set('value', str(stats.correspondences_used_in_recons[c]))
        ET.SubElement(corr, 'used_in_sets').set('value', str(set_count))
        #print(f'{c}', '%s %s' % (stats.correspondences_used_in_recons[c], set_count))
    ET.SubElement(corrs, 'correspondences_used').set('value', str(len(stats.correspondences_used_in_recons)))

    for name, value in stats.summary_stats.items():
        ET.SubElement(runstats, name).set('value', str(stats.summary_stats[name]))


    with open(filename, 'w', encoding='utf-8') as f:
        f.write(ET.tostring(root, pretty_print=True, encoding='unicode'))


def serialize_evaluation(stats, filename):
    root = ET.Element('stats', attrib={'project': 'foo'})
    ET.SubElement(root, 'createdat').text = run_date

    entry = ET.SubElement(root, 'totals')
    for k, v in stats.items():
        if 'sets_' == k[:5]:
            # if this is one of the 'sets' elements, make it a child of the root (not <totals>)
            element = ET.SubElement(root, k)
            #element.append(create)
            continue
        elif type(v) == type(()):
            element = ET.SubElement(entry, k)
            element.set('value', str(v[0]))
            element.set('type', str(v[1]))
        else:
            ET.SubElement(entry, k).set('value', str(v))

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(ET.tostring(root, pretty_print=True, encoding='unicode'))

def serialize_mels(mel_sets, mel_name, filename):
    '''
    <semantics>
      <mel id="m1">
        <gl>beer</gl>
      </mel>

    :param mel_sets:
    :param filename:
    :return:
    '''
    root = ET.Element('semantics', attrib={'basedon': mel_name})
    ET.SubElement(root, 'createdat').text = run_date

    for (number, mel) in enumerate(list(mel_sets)):
        entry = ET.SubElement(root, 'mel', attrib={'id': f'x{str(number + 1)}'})
        ET.SubElement(entry, 'gl').text = mel
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(ET.tostring(root, pretty_print=True, encoding='unicode'))

def serialize_proto_lexicon(proto_lexicon, filename):
    with open(filename, 'wb') as f:
        pickle.dump(proto_lexicon, f)
