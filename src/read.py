import xml.etree.ElementTree as ET
import csv
import os
import RE
import mel
import pickle

def read_correspondence_file(filename, name, mel_filename, fuzzy_filename):
    "Return syllable canon and table of correspondences"
    tree = ET.parse(filename)
    return RE.Parameters(read_correspondences(tree),
                         read_syllable_canon(tree.find('parameters')),
                         name,
                         read_mel_file(mel_filename)
                         if mel_filename else None,
                         read_fuzzy_file(fuzzy_filename)
                         if fuzzy_filename else None)


def read_syllable_canon(parameters):
    sound_classes = {}
    supra_segmentals = []
    regex = None
    context_match_type = 'constituent'
    for parameter in parameters:
        if parameter.tag == 'class':
            sound_classes[parameter.attrib.get('name')] = \
                [x.strip() for x in parameter.attrib.get('value').split(',')]
        if parameter.tag == 'canon':
            regex = parameter.attrib.get('value')
        if parameter.tag == 'spec':
            supra_segmentals = parameter.attrib.get('value').split(',')
        if parameter.tag == 'context_match_type':
            context_match_type = parameter.attrib.get('value')
    return RE.SyllableCanon(sound_classes, regex, supra_segmentals, context_match_type)

# Compute all daughter languages referenced in the correspondence
# section of tree.
def all_daughter_languages(tree):
    # dicts are now guaranteed to be sorted by Python
    daughter_languages = dict()
    for correspondence in tree.iterfind('corr'):
        for dialect in correspondence.iterfind('modern'):
            daughter_languages[dialect.attrib.get('dialecte')] = True
    return list(daughter_languages.keys())

def read_correspondences(tree):
    daughter_languages = all_daughter_languages(tree)
    table = RE.TableOfCorrespondences(daughter_languages)
    for correspondence in tree.iterfind('corr'):
        daughter_forms = {name: '' for name in daughter_languages}
        for dialect in correspondence.iterfind('modern'):
            daughter_forms[dialect.attrib.get('dialecte')] = \
                list(map(lambda seg: seg.text, dialect.iterfind('seg')))
        proto_form_info = correspondence.find('proto')
        contextL = proto_form_info.attrib.get('contextL')
        contextR = proto_form_info.attrib.get('contextR')
        context = ([x.strip() for x in contextL.split(',')]
                   if contextL else None,
                   [x.strip() for x in contextR.split(',')]
                   if contextR else None)
        table.add_correspondence(
            RE.Correspondence(
                correspondence.attrib.get('num'),
                context,
                [x.strip() for x
                 in proto_form_info.attrib.get('syll').split(',')],
                proto_form_info.text,
                daughter_forms))
    for rule in tree.iterfind('rule'):
        daughter_forms = {name: '' for name in daughter_languages}
        input_info = rule.find('input')
        contextL = input_info.attrib.get('contextL')
        contextR = input_info.attrib.get('contextR')
        context = ([x.strip() for x in contextL.split(',')]
                   if contextL else None,
                   [x.strip() for x in contextR.split(',')]
                   if contextR else None)
        outcome_info = rule.find('outcome')
        languages = [x.strip() for x in outcome_info.attrib.get('languages').split(',')]
        table.add_rule(
            RE.Rule(
                rule.attrib.get('num'),
                context,
                input_info.text,
                [x.strip() for x
                 in outcome_info.text.split(',')],
                languages,
                int(rule.attrib.get('stage'))))
    for quirk in tree.iterfind('quirk'):
        table.add_quirk(
            RE.Quirk(quirk.attrib.get('id') or '',
                     quirk.find('source_id').text or '',
                     quirk.find('lg').text or '',
                     quirk.find('lx').text or '',
                     quirk.find('gl').text or '',
                     quirk.find('alternative').text or '',
                     quirk.find('analysis_slot').text or '',
                     quirk.find('analysis_value').text or '',
                     [q.text for q in quirk.findall('note')]))
    return table

def skip_comments(reader):
    for row in reader:
        if '#' in row[0]:
            continue
        else:
            yield row


def read_csv_correspondences(filename, daughter_languages):
    table = RE.TableOfCorrespondences(daughter_languages)
    with open(filename, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        # element of redundancy here, but we can't assume order
        n1 = list(skip_comments(reader))
        names = [x.strip() for x in n1[0][5:]]
        for row in n1[1:]:
            row = [r.replace('=',',') for r in row]
            reordered_row = [row[0], row[4], row[2], row[3]] + row[5:]
            table.add_correspondence(
                RE.Correspondence.from_row(reordered_row, names))
    return table

# xml reading
def read_settings_file(filename, mel=None, recon=None, fuzzy=None):
    # for now we assume we don't want more than one proto-language
    upstream = {}
    downstream = []
    attested = {}
    proto_languages = {}
    mel_filenames = {}
    reconstructions = {}
    fuzzy_filenames = {}
    other = {}
    target = None
    for setting in ET.parse(filename).getroot():
        if setting.tag == 'reconstruction':
            reconstructions[setting.attrib['name']] = setting
            if setting.attrib['name'] == recon:
                for spec in setting:
                    if spec.tag == 'action':
                        if spec.attrib['name'] == 'upstream':
                            if spec.attrib.get('target'):
                                target = spec.attrib.get('target')
                            if spec.attrib.get('to'):
                                upstream[spec.attrib.get('to')] = \
                                    spec.attrib.get('from').split(',')
                        elif spec.attrib['name'] == 'downstream':
                            downstream.append(spec.attrib['to'])
                    elif spec.tag == 'proto_language':
                        proto_languages[spec.attrib['name']] = \
                            spec.attrib['correspondences']
        elif setting.tag == 'attested':
            attested[setting.attrib['name']] = setting.attrib['file']
        elif setting.tag == 'mel':
            mel_filenames[setting.attrib['name']] = setting.attrib['file']
        elif setting.tag == 'fuzzy':
            fuzzy_filenames[setting.attrib['name']] = setting.attrib['file']
        elif setting.tag == 'param':
            other[setting.attrib['name']] = setting.attrib['value']
    other['mels'] = mel_filenames
    other['fuzzies'] = fuzzy_filenames
    other['reconstructions'] = reconstructions
    return RE.ProjectSettings(os.path.dirname(filename),
                              None if mel is None else mel_filenames[mel],
                              attested,
                              proto_languages,
                              target,
                              upstream,
                              downstream,
                              other,
                              None if fuzzy is None else fuzzy_filenames[fuzzy])


# returns a generator returning the modern form and its gloss
def read_lexicon(xmlfile):
    tree = ET.parse(xmlfile)
    language = tree.getroot().attrib.get('dialecte')
    forms = [RE.ModernForm(language,
                           entry.find('hw').text
                           if entry.find('hw') is not None
                           else '',
                           # fallback to provided gloss if there is no
                           # 'normalized' gloss
                           entry.find('ngl').text
                           if entry.find('ngl') is not None
                           else entry.find('gl').text,
                           entry.attrib.get('id')
                           )
             for entry in tree.iterfind('entry')]
    return RE.Lexicon(language, forms, [])

# returns a generator returning the modern form and its gloss
def create_lexicon_from_parms(language_forms):
    lexicons = {}
    for language,form in language_forms:
        forms = [RE.ModernForm(language,form,'','')]
        lexicons[language] = RE.Lexicon(language, forms, [])
    return lexicons


def read_attested_lexicons(settings):
    return {language: read_lexicon(os.path.join(settings.directory_path,
                                                settings.attested[language]))
            for language in settings.attested}


def read_tabular_lexicons(filename, columns, delimiter='\t'):
    (gloss_column, id_column, data_start_column) = columns
    with open(filename, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter)
        # element of redundancy here, but we can't assume order
        n1 = list(skip_comments(reader))
        names = [x.strip() for x in n1[0][data_start_column:]]
        #names = [x.strip() for x in list(skip_comments(reader))[data_start_column:]]
        forms_dict = {name: [] for name in names}
        for row in n1[1:]:
            gloss = row[gloss_column]
            id = row[id_column]
            for language, form in zip(names, row[data_start_column:]):
                form = form.strip()
                if form:
                    forms_dict[language].append(RE.ModernForm(language, form, gloss, id))
        return [RE.Lexicon(language, forms, []) for language, forms in forms_dict.items()]


def read_header_line(filename, delimiter='\t'):
    with open(filename, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter)
        # return first row (header)
        return skip_comments(reader)


def read_mel_file(filename):
    try:
        tree = ET.parse(filename)
        return [mel.Mel([seg.text for seg in child.iterfind('gl')],
                        child.attrib.get('id'))
                for child in tree.iterfind('mel')]
    except:
        print(f'could not process mel file: {filename}')
        return []


def get_element(language, entry, field):
    # return element.text if element else ''
    element = entry.find(field)
    if element is None:
        id = entry.attrib['id']
        print(f'Missing {field} field: {language}, id: {id}')
        return ''
    else:
        return element.text


# Return a map from representatives to the class they map to.
def read_fuzzy_file(filename):
    mapping = dict()
    for child in ET.parse(filename).iterfind('item'):
        dialect = child.attrib.get('dial')
        target = child.attrib.get('to')
        for representative in child:
            previous_target = mapping.get(representative, False)
            if previous_target:
                raise Exception(f'ambiguous fuzzing for {representative}',
                                'it maps to both {target} and {previous_target}')
            else:
                mapping[(dialect, representative.text)] = target
    return mapping

def read_proto_lexicon(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)
