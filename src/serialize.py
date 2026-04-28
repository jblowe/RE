import os
import time
import collections
import lxml.etree as ET
from xml.dom import minidom
import RE
import utils
import inspect
import pickle
import json
import csv

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
    for rule in parameters.table.rules:
        r = ET.SubElement(root, 'rule', num=rule.id, stage=str(rule.stage))
        attributes = {}
        if rule.context[0]:
            attributes['contextL'] = ','.join(rule.context[0])
        if rule.context[1]:
            attributes['contextR'] = ','.join(rule.context[1])
        ET.SubElement(r, 'input', **attributes).text = \
            rule.input
        ET.SubElement(r, 'outcome', languages=','.join(rule.languages)).text = \
            ','.join(rule.outcome)
    '''
    <quirks>
        <quirk id="99">
          <sourceid>gha.99</sourceid>
          <lg>gha</lg>
          <lx>4straw</lx>
          <alt>3strum</alt>
          <analysis><slot>T</slot><value>3</value></analysis>
          <gl>gloss (optional)</gl>
          <note>note (optional)</note>
          <note>note(s) (repeatable)</note>
        </quirk>
    </quirks>
    :param quirks:
    :param filename:
    :return:
    '''
    for (number, (key, quirk)) in enumerate(sorted(parameters.table.quirks.items())):
        entry = ET.SubElement(root, 'quirk', attrib={'id': f'x{str(number + 1)}'})
        ET.SubElement(entry, 'source_id').text = quirk.source_id
        ET.SubElement(entry, 'lg').text = quirk.language
        ET.SubElement(entry, 'lx').text = quirk.form
        ET.SubElement(entry, 'gl').text = quirk.gloss
        ET.SubElement(entry, 'alternative').text = quirk.alternative
        ET.SubElement(entry, 'analysis_slot').text = quirk.slot
        ET.SubElement(entry, 'analysis_value').text = quirk.value
        for note in list(quirk.notes):
            ET.SubElement(entry, 'note').text = note

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(minidom.parseString(ET.tostring(root))
                .toprettyxml(indent='   '))


def serialize_csv_correspondences(table, filename):
    with open(filename, 'w', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t')
        writer.writerow(table.correspondence_header_row())
        for c in table.correspondences:
            writer.writerow(c.as_row(table.daughter_languages))


def serialize_csv_rules(table, filename):
    with open(filename, 'w', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t')
        writer.writerow(table.rule_header_row())
        for rule in table.rules:
            writer.writerow(rule.as_row())


def serialize_csv_quirks(table, filename):
    with open(filename, 'w', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t')
        writer.writerow(table.quirks_header_row())
        for quirk in table.quirks.values():
            writer.writerow(quirk.as_row())


def serialize_lexicons(lexicons, project_name, dirname, ext='.data.xml'):
    for lexicon in lexicons:
        serialize_lexicon(
            lexicon,
            os.path.join(dirname,
                         f'{project_name}.{lexicon.language}{ext}'))


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


def add_entry(root, form, number):
    rfx = ET.SubElement(root, 'rfx')
    if isinstance(form, RE.ModernForm):
        rfx.set('id', form.id)
        ET.SubElement(rfx, 'lx').text = form.glyphs
        # A failure carries the fuzzied form when neither version parsed.
        fuzzied = getattr(form, 'fuzzied', None)
        if fuzzied is not None:
            ET.SubElement(rfx, 'lxf').text = fuzzied.glyphs
    elif isinstance(form, RE.FuzzyForm):
        rfx.set('id', form.actual.id)
        ET.SubElement(rfx, 'lx').text = form.actual.glyphs
        ET.SubElement(rfx, 'lxf').text = form.glyphs
    ET.SubElement(rfx, 'lg').text = form.language
    try:
        ET.SubElement(rfx, 'gl').text = form.gloss
    except:
        ET.SubElement(rfx, 'gl').text = 'missing'
    return


def render_sets(forms, sets, languages, set_type):
    def sort_forms(form, sf, level):
        # we need to output the supporting forms in the order specified by "languages"
        unfrozenset = [x for x in form.supporting_forms]
        lglist = [x.language for x in form.supporting_forms]
        emitted = set()
        for language in languages:
            try:
                indices = [i for i, x in enumerate(lglist) if x == language]
                for i in indices:
                    supporting_form = unfrozenset[i]
                    render_xml(sf, supporting_form, level + 1)
                    emitted.add(i)
            except:
                pass
        # Emit any remaining forms (intermediate proto-languages not in the leaf languages list)
        for i, supporting_form in enumerate(unfrozenset):
            if i not in emitted:
                render_xml(sf, supporting_form, level + 1)
        return

    def add_protoform_element(element, protoform):
        ET.SubElement(element, 'plg').text = protoform.language
        ET.SubElement(element, 'pfm').text = protoform.glyphs
        ET.SubElement(element, 'rcn').text = RE.correspondences_as_ids(protoform.correspondences).strip()
        try:
            ET.SubElement(element, 'venn').text = form.venn
        except:
            pass

    def render_xml(element, form, level):

        # handle merged case: a tuple (supporting_forms, [ProtoForm, ...]) produced
        # by grouping sets with identical reflexes; len > 1 means multiple reconstructions.
        if isinstance(form, tuple):
            if level != 0:
                element = ET.SubElement(element, 'subset', attrib={'level': str(level)})
            ET.SubElement(element, 'id').text = f'%s.%s' % (number + 1, level)
            if len(form[1]) > 1:
                for protoform in form[1]:
                    reconstruction_block = ET.SubElement(element, 'multi')
                    add_protoform_element(reconstruction_block, protoform)
            else:
                add_protoform_element(element, form[1][0])
            if form[1][0].mel and form[1][0].mel.glosses:
                ET.SubElement(element, 'mel').text = ', '.join(form[1][0].mel.glosses)
                ET.SubElement(element, 'melid').text = form[1][0].mel.id
            sf = ET.SubElement(element, 'sf')
            sort_forms(form[1][0], sf, level)

        elif isinstance(form, RE.ModernForm):
            rfx = ET.SubElement(element, 'rfx')
            ET.SubElement(rfx, 'lg').text = form.language
            ET.SubElement(rfx, 'lx').text = form.glyphs
            ET.SubElement(rfx, 'gl').text = form.gloss
            ET.SubElement(rfx, 'id').text = form.id
            try:
                ET.SubElement(rfx, 'membership').text = form.membership
            except:
                pass
        elif isinstance(form, RE.FuzzyForm):
            # Fuzzied reflex: <lx> carries the original glyphs (preserved for
            # display / XSLT compatibility); <lxf> carries the fuzzied glyphs
            # that were actually used for parsing.  XSLT renders as "lxf << lx".
            rfx = ET.SubElement(element, 'rfx')
            ET.SubElement(rfx, 'lg').text = form.language
            ET.SubElement(rfx, 'lx').text = form.actual.glyphs
            ET.SubElement(rfx, 'lxf').text = form.glyphs
            ET.SubElement(rfx, 'gl').text = form.gloss
            ET.SubElement(rfx, 'id').text = form.actual.id
            try:
                ET.SubElement(rfx, 'membership').text = form.membership
            except:
                pass
        elif isinstance(form, RE.ProtoForm):
            if level != 0:
                element = ET.SubElement(element, 'subset', attrib={'level': str(level)})
            ET.SubElement(element, 'id').text = f'%s.%s' % (number + 1, level)
            add_protoform_element(element, form)
            # Emit MEL gloss and id when a real MEL is associated (glosses is
            # non-empty for real Mel objects; default_mel has glosses=[]).
            if form.mel and form.mel.glosses:
                ET.SubElement(element, 'mel').text = ', '.join(form.mel.glosses)
                ET.SubElement(element, 'melid').text = form.mel.id
            sf = ET.SubElement(element, 'sf')
            sort_forms(form, sf, level)

    number = 0
    for number, form in enumerate(forms):
        entry = ET.SubElement(sets, 'set')
        render_xml(entry, form, 0)

    print(f'number of "{set_type}" {number}')
    return sets


def create_xml_sets(reconstruction, languages, only_with_mel):
    '''
    Here is the "classic schema" of cognate sets...

        <set>
          <id>779</id>
          <rcn>c2.c194.c23.</rcn>
          <pfm>Bse&#x2D0;</pfm>
          <mel>heart</mel>
          <melid>m6</melid>
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

    sets = ET.SubElement(root, 'sets')

    # Always merge sets that share identical supporting forms, collecting all
    # competing reconstructions into a tuple so render_xml can emit <multi>
    # elements for them.  (Whether forms *reach* this point depends on
    # only_with_mel / strict, which is handled upstream in mel.associated_mels.)
    uniques = collections.defaultdict(list)
    for form in sorted(reconstruction.forms, key=lambda corrs: RE.correspondences_as_ids(corrs.correspondences)):
        uniques[form.supporting_forms].append(form)

    render_sets(sorted(uniques.items(), key=lambda recons: RE.correspondences_as_ids(recons[1][0].correspondences)),
                sets, languages, 'sets')

    isolates = ET.SubElement(root, 'isolates')
    if hasattr(reconstruction, 'isolates_dict'):
        serialize_isolates_dict(reconstruction.isolates_dict, isolates)
    else:
        serialize_isolates_and_failures(reconstruction.isolates, isolates, 'isolates')

    failures = ET.SubElement(root, 'failures')
    # there is only one (big) set for failures, pass it in as a list
    serialize_isolates_and_failures(reconstruction.failures, failures, 'failures')

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
        ET.SubElement(settings_element, 'parm', attrib={'key': 'run', 'value': str(args.run)})
        ET.SubElement(settings_element, 'parm', attrib={'key': 'mel_filename', 'value': str(settings.mel_filename)})
        ET.SubElement(settings_element, 'parm',
                      attrib={'key': 'correspondences', 'value': settings.proto_languages[settings.upstream_target]})
        ET.SubElement(settings_element, 'parm', attrib={'key': 'strict', 'value': str(args.only_with_mel)})
        try:
            ET.SubElement(settings_element, 'parm', attrib={'key': 'fuzzyfile', 'value': settings.fuzzy_filename})
        except:
            ET.SubElement(settings_element, 'parm', attrib={'key': 'fuzzyfile', 'value': 'No fuzzying done.'})
        try:
            sc = settings.syllable_canon
            ET.SubElement(settings_element, 'parm', attrib={
                'key': 'context_match_type', 'value': str(sc.context_match_type)})
            ET.SubElement(settings_element, 'parm', attrib={
                'key': 'spec', 'value': ', '.join(sc.supra_segmentals)})
        except Exception:
            pass
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

    try:
        correspondences_used = 0
        for reference_set in stats.correspondence_index.values():
            if len(reference_set) != 0:
                correspondences_used += 1
        if correspondences_used > 0:
            corrs = ET.SubElement(root, 'correspondences')
            for (c, sets) in sorted(list(stats.correspondence_index.items()), key=lambda u: len(u[1])):
                corr = ET.SubElement(corrs, 'correspondence', attrib={'value': str(c)})
                ET.SubElement(corr, 'used_in_cognate_sets').set('value', str(len(sets)))
            ET.SubElement(corrs, 'correspondences_used').set('value', str(correspondences_used))
    except Exception:
        pass

    for name, value in stats.summary_stats.items():
        ET.SubElement(runstats, name).set('value', str(stats.summary_stats[name]))

    try:
        if len(stats.mel_usage.items()) > 0:
            semantics = ET.SubElement(root, 'semantics')
            for mel in stats.mel_usage.items():
                entry = ET.SubElement(semantics, 'mel', attrib={'id': mel[0]})
                for gl in mel[1]:
                    if gl == 'usage': continue
                    gl_element = ET.SubElement(entry, 'gl', attrib={'uses': str(mel[1][gl])})
                    gl_element.text = gl
    except:
        pass

    try:
        if len(stats.glosses_by_language.items()) > 0:
            glosses_by_language = ET.SubElement(root, 'glosses_by_language')
            for lg in stats.glosses_by_language:
                # we reuse the <mel> element here for each language
                list_of_glosses = ET.SubElement(glosses_by_language, 'mel', attrib={'id': lg})
                for g in sorted(stats.glosses_by_language[lg]):
                    gl_element = ET.SubElement(list_of_glosses, 'gl')
                    gl_element.text = g
                    gl_element.set('count', str(stats.glosses_by_language[lg][g]))
    except:
        pass

    try:
        if len(stats.unmatched_glosses) > 0:
            unmatched_glosses = ET.SubElement(root, 'unmatched_glosses')
            list_of_unmatched_glosses = ET.SubElement(unmatched_glosses, 'mel')
            for g in sorted(stats.unmatched_glosses):
                gl_element = ET.SubElement(list_of_unmatched_glosses, 'gl')
                gl_element.text = g
    except:
        pass

    try:
        if hasattr(stats, 'unmatched_by_language') and len(stats.unmatched_by_language) > 0:
            # Count how many languages each gloss appears in, to flag repeated ones.
            gloss_lang_count = collections.Counter()
            for language, glosses in stats.unmatched_by_language.items():
                for g in glosses:
                    gloss_lang_count[g] += 1
            unmatched_by_language = ET.SubElement(root, 'unmatched_by_language')
            for language in sorted(stats.unmatched_by_language):
                lg_element = ET.SubElement(unmatched_by_language, 'lg', attrib={'id': language})
                for g in sorted(stats.unmatched_by_language[language]):
                    gl_element = ET.SubElement(lg_element, 'gl')
                    gl_element.text = g
                    if gloss_lang_count[g] > 1:
                        gl_element.set('repeated', 'true')
    except:
        pass

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(ET.tostring(root, pretty_print=True, encoding='unicode'))


def serialize_evaluation(stats, filename, languages):
    root = ET.Element('stats', attrib={'project': 'foo'})
    ET.SubElement(root, 'createdat').text = run_date

    entry = ET.SubElement(root, 'totals')
    for k, v in stats.items():
        if 'sets_' == k[:5]:
            # if this is one of the 'sets' elements, make it a child of the root (not <totals>)
            element = ET.SubElement(root, k)
            render_sets(v, element, languages, k)
        elif k == 'graph':
            graph = stats['graph']
            refs = stats['refs']
            pfms = stats['pfms']

            # make the xml for the graph version
            element = ET.SubElement(root, 'graph')
            for node in graph:
                xnode = ET.SubElement(element, 'node')
                ET.SubElement(xnode, 'ref').set('value', node)
                for node2 in graph[node]:
                    ET.SubElement(xnode, 'pfm').set('value', node2)

            # make a json file of the graph version
            nodes = []
            links = []
            seen = set()
            # make a table of the overlapping sets
            for node in graph:
                nodes.append({'id': node, 'radius': len(graph[node]), 'group': 'rfx'})
                for node2 in graph[node]:
                    if node2 not in seen:
                        nodes.append({'id': node2, 'radius': len(graph[node]), 'group': 'pfm'})
                        seen.add(node2)
                    links.append({'source': node2, 'target': node, 'value': 2})

            with open(filename.replace('.xml', '.json'), 'w', encoding='utf-8') as f:
                f.write(json.dumps({'nodes': nodes, 'links': links}, indent=2))

            # for now, just handle the first 200 reflexes and first 100 protoforms for the table version
            refs = refs[:200]
            pset = set()
            [[pset.add(p) for p in graph[r]] for r in graph]
            pfms = list(pset)
            pfms = pfms[:100]

            # make the table version
            element = ET.SubElement(root, 'matrix')

            # make a table of the overlapping sets
            header = ET.SubElement(element, 'header')
            ET.SubElement(header, 'th').text = 'reflex'
            for p in pfms:
                ET.SubElement(header, 'th').text = p

            table = ET.SubElement(element, 'table')
            for i in range(len(refs)):
                tr = ET.SubElement(table, 'tr')
                ET.SubElement(tr, 'th').text = refs[i]
                for j in range(len(pfms)):
                    if pfms[j] in graph[refs[i]]:
                        ET.SubElement(tr, 'td').text = 'X'
                    else:
                        ET.SubElement(tr, 'td').text = ''

        elif k in 'pfms refs list_of_sf'.split(' '):
            pass
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
        entry = ET.SubElement(root, 'mel', attrib={'id': 'x' + str(number + 1).zfill(4)})
        for m in mel.glosses:
            ET.SubElement(entry, 'gl').text = m
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(ET.tostring(root, pretty_print=True, encoding='unicode'))


def serialize_isolates_and_failures(re_items, re_element, item_name):
    ET.SubElement(re_element, 'createdat').text = run_date

    number = 0
    for (number, form) in enumerate(re_items):
        add_entry(re_element, form, number)

    print(f'number of "{item_name}" {number}')

    return


def serialize_isolates_dict(isolates_dict, re_element):
    """Serialize isolates with pfm/rcn from the dict returned by extract_isolates."""
    ET.SubElement(re_element, 'createdat').text = run_date
    print(f'number of "isolates" {len(isolates_dict)}')
    for number, (form, proto_forms) in enumerate(
            sorted(isolates_dict.items(), key=lambda x: x[0].language)):
        rfx = ET.SubElement(re_element, 'rfx')
        if isinstance(form, RE.ModernForm):
            rfx.set('id', form.id)
            ET.SubElement(rfx, 'lx').text = form.glyphs
        elif isinstance(form, RE.FuzzyForm):
            rfx.set('id', form.actual.id)
            ET.SubElement(rfx, 'lx').text = form.actual.glyphs
            ET.SubElement(rfx, 'lxf').text = form.glyphs
        ET.SubElement(rfx, 'lg').text = form.language
        try:
            ET.SubElement(rfx, 'gl').text = form.gloss
        except Exception:
            ET.SubElement(rfx, 'gl').text = 'missing'
        if proto_forms:
            pf = proto_forms[0]
            ET.SubElement(rfx, 'pfm').text = pf.glyphs
            ET.SubElement(rfx, 'rcn').text = RE.correspondences_as_ids(
                pf.correspondences).strip()
        reason = getattr(form, '_isolate_reason', '')
        if reason:
            ET.SubElement(rfx, 'reason').text = reason
