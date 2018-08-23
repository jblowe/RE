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
                         read_mel_file(mel_filename))

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
            table.add_correspondence(Correspondence(
                row[0], row[4], row[2].split(','), row[3],
                dict(zip(names, (x.split(',') for x in row[5:])))))
    return table

# xml reading
def read_settings_file(filename):
    # for now we assume we don't want more than one proto-language
    upstream = {}
    downstream = []
    attested = {}
    proto_languages = {}
    for setting in ET.parse(filename).getroot():
        if setting.tag == 'action':
            if setting.attrib['name'] == 'upstream':
                if setting.attrib.get('target'):
                    target = setting.attrib.get('target')
                if setting.attrib.get('to'):
                    upstream[setting.attrib.get('to')] = \
                        setting.attrib.get('from').split(',')
            elif setting.attrib['name'] == 'downstram':
                downstream.append(setting.attrib['to'])
        elif setting.tag == 'proto_language':
            proto_languages[setting.attrib['name']] = \
                setting.attrib['correspondences']
        elif setting.tag == 'attested':
            attested[setting.attrib['name']] = setting.attrib['file']
        elif setting.tag == 'param':
            if setting.attrib['name'] == 'mel':
                mel_filename = setting.attrib.get('value')
    return RE.ProjectSettings(os.path.dirname(filename),
                              mel_filename,
                              attested,
                              proto_languages,
                              target,
                              upstream,
                              downstream)

# returns a generator returning the modern form and its gloss
def read_lexicon(xmlfile):
    tree = ET.parse(xmlfile)
    language = tree.getroot().attrib.get('dialecte')
    forms = [RE.ModernForm(language, entry.find('hw').text,
                           entry.find('gl').text)
             for entry in tree.iterfind('entry')]
    return RE.Lexicon(language, forms)

def read_lexicons(languages, base_dir, project):
    for language in languages:
        print('Reading lexicon: ', f'{base_dir}/{project}/{project}.{language}.data.xml')
        yield (language,
               list(read_lexicon(f'{base_dir}/{project}/{project}.{language}.data.xml')))

def read_tabular_lexicons(tablefile, delimiter='\t'):
    with open(tablefile, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter)
        # element of redundancy here, but we can't assume order
        names = [x.strip() for x in next_skipping_comment(reader)[1:]]
        forms_dict = {name: [] for name in names}
        for row in reader:
            gloss = row[0]
            for language, form in zip(names, row[1:]):
                form = form.strip()
                if form:
                    forms_dict[language].append(ModernForm(language, form, gloss))
        return forms_dict.items()

def read_mel_file(filename):
    tree = ET.parse(filename)
    return [mel.Mel([seg.text for seg in child.iterfind('gl')],
                    child.attrib.get('id'))
            for child in tree.iterfind('mel')]
