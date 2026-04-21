import xml.etree.ElementTree as ET
import csv
import os
import RE
import mel
import pickle
import json
from utils import *

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
                [nfc(x.strip()) for x in parameter.attrib.get('value').split(',')]
        if parameter.tag == 'canon':
            regex = nfc(parameter.attrib.get('value'))
        if parameter.tag == 'spec':
            supra_segmentals = [nfc(x) for x in parameter.attrib.get('value').split(',')]
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
                list(map(lambda seg: nfc(seg.text), dialect.iterfind('seg')))
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
                nfc(proto_form_info.text),
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
                nfc(input_info.text),
                [x.strip() for x
                 in nfc(outcome_info.text).split(',')],
                languages,
                int(rule.attrib.get('stage'))))
    for quirk in tree.iterfind('quirk'):
        table.add_quirk(
            RE.Quirk(quirk.attrib.get('id') or '',
                     nfc(quirk.find('source_id').text) or '',
                     nfc(quirk.find('lg').text) or '',
                     nfc(quirk.find('lx').text) or '',
                     nfc(quirk.find('gl').text) or '',
                     nfc(quirk.find('alternative').text) or '',
                     nfc(quirk.find('analysis_slot').text) or '',
                     nfc(quirk.find('analysis_value').text) or '',
                     [nfc(q.text) for q in quirk.findall('note')]))
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
def parse_upstream(upstream_str):
    result = {}
    for u in upstream_str.split(';'):
        u = u.strip()
        if not u:
            continue
        [pl, lgs] = u.split(':')
        pl = pl.strip()
        lgs = [l.strip() for l in lgs.split(',')]
        result[pl] = lgs
    return result

def read_settings(project_path, project_code, recon_token, mel_token=None, fuzzy_token=None, upstream=None):
# f read_settings(filename, mel=None, recon=None, fuzzy=None):

    """Build RE.ProjectSettings from project directory and parameters."""
    languages = None
    # downstream = []
    proto_language = None
    proto_languages = None
    mel_filenames = {}
    reconstructions = {}
    fuzzy_filenames = {}
    other = {}
    upstream_map = None
    if upstream is not None:
        upstream_map = parse_upstream(upstream)
        proto_lang_keys = set(upstream_map.keys())
        languages = [lg for lgs in upstream_map.values() for lg in lgs if lg not in proto_lang_keys]
    # 1) correspondences
    recon_file = resolve_file(project_path, project_code, recon_token, '.correspondences.xml')
    if recon_file is None and upstream is None:
        raise Exception(f"Could not find correspondences file for -t/--recon '{recon_token}' in {project_path}")
    elif upstream_map is not None:
        proto_languages = {}
        for pl in upstream_map.keys():
            pl_recon_file = resolve_file(project_path, project_code, pl, '.correspondences.xml')
            if pl_recon_file is not None:
                # Each proto-language has its own correspondences file — use it.
                print(f'using {pl} correspondences: {pl_recon_file}')
            elif recon_file is not None:
                # Fall back to the -t/--recon file for this level.
                pl_recon_file = recon_file
                print(f'using -t/--recon {recon_token} for {pl}: {recon_file}')
            else:
                raise Exception(
                    f"No correspondences file found for proto-language '{pl}' in {project_path}. "
                    f"Expected {project_code}.{pl}.correspondences.xml")
            proto_languages[pl] = pl_recon_file
    else:
        proto_language = read_protolanguage_from_correspondences(os.path.join(project_path, recon_file))
        if proto_language is None:
            proto_language = project_code.capitalize()[:4]
            print(f"Could not determine protolanguage for {recon_file}.")
            print(f"Using 1st 4 letters of project, title case: {proto_language}")
        else:
            print(f'using protolanguage {proto_language} from {recon_file}')
        proto_languages = {proto_language: recon_file}

    upstream_target = next(iter(proto_languages))

    # 2) languages / attested lexicons
    if languages is None:
        languages = list_attested_languages(project_path)
    if not languages:
        raise Exception(f'No attested lexicons found in {project_path} (expected *.<LANG>.data.xml)')

    attested = {}
    for lg in languages:
        fn = resolve_file(project_path, project_code, lg, '.data.xml')
        if not fn:
            raise Exception(f"Language '{lg}' requested, but file not found: *.{lg}.data.xml")
        attested[lg] = fn

    # 3) MEL / fuzzy
    mel_file = resolve_file(project_path, project_code, mel_token, '.mel.xml')
    if mel_token is not None and mel_file is None:
        raise Exception(f"--mel '{mel_token}' does not resolve to an existing file in {project_path} (expected {project_code}.{mel_token}.mel.xml)")

    fuzzy_file = resolve_file(project_path, project_code, fuzzy_token, '.fuz.xml')
    if fuzzy_token is not None and fuzzy_file is None:
        raise Exception(
            f"--fuzzy '{fuzzy_token}' does not resolve to an existing file in {project_path}. "
            f"Tried {project_code}.{fuzzy_token}.fuz.xml and {project_code}.{fuzzy_token}.xml")

    # 4) action graph
    upstream_graph = upstream_map if upstream_map is not None else {upstream_target: languages}
    downstream = []
    other = {
        'title': f'{project_code} reconstruction ({recon_token or upstream_target})',
        'mels': {},
        'fuzzies': {},
        'reconstructions': {},
    }

    return RE.ProjectSettings(
        project_path,
        mel_file,
        attested,
        proto_languages,
        upstream_target,
        upstream_graph,
        downstream,
        other,
        fuzzy_filename=fuzzy_file,
    )


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
        target = nfc(child.attrib.get('to'))
        for representative in child:
            previous_target = mapping.get(representative, False)
            if previous_target:
                raise Exception(f'ambiguous fuzzing for {representative}',
                                'it maps to both {target} and {previous_target}')
            else:
                mapping[(dialect, nfc(representative.text))] = target
    return mapping

def read_proto_lexicon(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)
