import xml.etree.ElementTree as ET
import csv
import os
import RE
import mel

def read_correspondence_file(filename, project_name, daughter_languages, name, mel_filename):
    "Return syllable canon and table of correspondences"
    tree = ET.parse(filename)
    return RE.Parameters(read_correspondences(tree.iterfind('corr'),
                                              project_name,
                                              daughter_languages),
                         read_syllable_canon(tree.find('parameters')),
                         name,
                         read_mel_file(mel_filename)
                         if mel_filename else None)

def read_syllable_canon(parameters):
    sound_classes = {}
    supra_segmentals = []
    for parameter in parameters:
        if parameter.tag == 'class':
            sound_classes[parameter.attrib.get('name')] = \
                [x.strip() for x in parameter.attrib.get('value').split(',')]
        if parameter.tag == 'canon':
            regex = parameter.attrib.get('value')
        if parameter.tag == 'spec':
            supra_segmentals = parameter.attrib.get('value').split(',')
    return RE.SyllableCanon(sound_classes, regex, supra_segmentals)

def read_correspondences(correspondences, project_name, daughter_languages):
    table = RE.TableOfCorrespondences(project_name, daughter_languages)
    for correspondence in correspondences:
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
    return table

def next_skipping_comment(reader):
    for row in reader:
        if '#' in row[0]:
            None
        else:
            return row

def read_csv_correspondences(filename, project_name, daughter_languages):
    table = RE.TableOfCorrespondences(project_name, daughter_languages)
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        # element of redundancy here, but we can't assume order
        names = next_skipping_comment(reader)[5:]
        for row in reader: 
            table.add_correspondence(RE.Correspondence(
                row[0], (None, None) if row[4] == '' else row[4], row[2].split(','), row[3],
                dict(zip(names, (x.split(',') for x in row[5:])))))
    return table

# xml reading
def read_settings_file(filename, mel='none', recon='default'):
    # for now we assume we don't want more than one proto-language
    upstream = {}
    downstream = []
    attested = {}
    proto_languages = {}
    mel_filenames = {}
    for setting in ET.parse(filename).getroot():
        if setting.tag == 'reconstruction' and setting.attrib['name'] == recon:
            for spec in setting:
                if spec.tag == 'action':
                    if spec.attrib['name'] == 'upstream':
                        if spec.attrib.get('target'):
                            target = spec.attrib.get('target')
                        if spec.attrib.get('to'):
                            upstream[spec.attrib.get('to')] = \
                                spec.attrib.get('from').split(',')
                    elif spec.attrib['name'] == 'downstram':
                        downstream.append(spec.attrib['to'])
                elif spec.tag == 'proto_language':
                    proto_languages[spec.attrib['name']] = \
                        spec.attrib['correspondences']
        elif setting.tag == 'attested':
            attested[setting.attrib['name']] = setting.attrib['file']
        elif setting.tag == 'mel':
            mel_filenames[setting.attrib['name']] = setting.attrib['file']
        elif setting.tag == 'param':
            pass
    return RE.ProjectSettings(os.path.dirname(filename),
                              None if mel == 'none' else mel_filenames[mel],
                              attested,
                              proto_languages,
                              target,
                              upstream,
                              downstream)

# returns a generator returning the modern form and its gloss
def read_lexicon(xmlfile):
    tree = ET.parse(xmlfile)
    language = tree.getroot().attrib.get('dialecte')
    forms = [RE.ModernForm(language,
                           get_element(language, entry, 'hw'),
                           # fallback to provided gloss if there is no
                           # 'normalized' gloss
                           get_element(language, entry, 'ngl')
                           if entry.find('ngl')
                           else get_element(language, entry, 'gl'))
             for entry in tree.iterfind('entry')]
    return RE.Lexicon(language, forms)

def read_attested_lexicons(settings):
    return {language: read_lexicon(os.path.join(settings.directory_path,
                                                settings.attested[language]))
            for language in settings.attested}

def read_tabular_lexicons(tablefile, columns, delimiter='\t'):
    (gloss_column, id_column, data_start_column) = columns
    with open(tablefile, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter)
        # element of redundancy here, but we can't assume order
        names = [x.strip() for x in next_skipping_comment(reader)[data_start_column:]]
        forms_dict = {name: [] for name in names}
        for row in reader:
            gloss = row[gloss_column]
            for language, form in zip(names, row[data_start_column:]):
                form = form.strip()
                if form:
                    forms_dict[language].append(RE.ModernForm(language, form, gloss))
        return [RE.Lexicon(language, forms) for language, forms in forms_dict.items()]

def read_mel_file(filename):
    tree = ET.parse(filename)
    return [mel.Mel([seg.text for seg in child.iterfind('gl')],
                    child.attrib.get('id'))
            for child in tree.iterfind('mel')]

def get_element(language, entry, field):
    # return element.text if element else ''
    element = entry.find(field)
    if element is None:
        id = entry.attrib['id']
        print(f'Missing {field} field: {language}, id: {id}')
        return ''
    else:
        return element.text
