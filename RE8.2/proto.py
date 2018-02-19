import xml.etree.ElementTree as ET
import sys
import re

class SyllableCanon:
    def __init__(self, sound_classes, syllable_regex):
        self.sound_classes = sound_classes
        self.regex = re.compile('^' + syllable_regex + '$')

class Correspondence:
    # daughter forms indexed by language
    daughter_forms = {}
    def __init__(self, id, context, syllable_type, proto_form, daughter_forms):
        self.id = id
        # context is a tuple of left and right contexts
        self.context = context
        self.syllable_type = syllable_type
        self.proto_form = proto_form
        self.daughter_forms = daughter_forms

    def __repr__(self):
        return f'Correspondence({self.id}, {self.syllable_type}, {self.proto_form[0]})'

def correspondences_as_proto_form_string(cs):
    return ''.join(str(c.proto_form) for c in cs)

# imperative interface
class TableOfCorrespondences:
    correspondences = []
    def __init__(self, family_name, daughter_languages):
        self.family_name = family_name
        self.daughter_languages = daughter_languages

    def add_correspondence(self, correspondence):
        self.correspondences.append(correspondence)

class Parameters:
    def __init__(self, table, syllable_canon):
        self.table = table
        self.syllable_canon = syllable_canon

class ModernForm:
    def __init__(self, language, form, gloss):
        self.language = language
        self.form = form
        self.gloss = gloss

    def __repr__(self):
        return f'{self.language} {self.form}: {self.gloss}'

# xml reading
def read_correspondence_file(filename, family_name, daughter_languages):
    "Return syllable canon and table of correspondences"
    tree = ET.parse(filename)
    return Parameters(read_correspondences(tree.iterfind('corr'),
                                           family_name,
                                           daughter_languages),
                      read_syllable_canon(tree.find('parameters')))

def read_syllable_canon(parameters):
    sound_classes = {}
    for parameter in parameters:
        if parameter.tag == 'class':
            sound_classes[parameter.attrib.get('name')] = \
                parameter.attrib.get('value')
        if parameter.tag == 'canon':
            regex = parameter.attrib.get('value')
    return SyllableCanon(sound_classes, regex)

def read_correspondences(correspondences, family_name, daughter_languages):
    table = TableOfCorrespondences(family_name, daughter_languages)
    for correspondence in correspondences:
        daughter_forms = {}
        for dialect in correspondence.iterfind('modern'):
            daughter_forms[dialect.attrib.get('dialecte')] = \
                list(map(lambda seg: seg.text, dialect.iterfind('seg')))
        proto_form_info = correspondence.find('proto')
        context = (proto_form_info.attrib.get('contextL'),
                   proto_form_info.attrib.get('contextR'))
        for syllable_type in proto_form_info.attrib.get('syll').split(','):
            table.add_correspondence(
                Correspondence(correspondence.attrib.get('num'),
                               context,
                               syllable_type,
                               proto_form_info.text,
                               daughter_forms))
    return table

# tokenize an input string and return the set of all parses
# which also conform to the syllable canon
def tokenize(form, parameters, accessor):
    parses = set()
    def gen(form, parse, syllable_parse):
        if form == '' and parameters.syllable_canon.regex.match(syllable_parse):
            parses.add(tuple(parse))
        for i in range(1, len(form) + 1):
            for c in parameters.table.correspondences:
                if form[:i] in accessor(c):
                    gen(form[i:], parse + [c], syllable_parse + c.syllable_type)
    gen(form, [], '')
    return parses

# returns a generator returning the modern form and its gloss
def read_lexicon(xmlfile):
    tree = ET.parse(xmlfile)
    language = tree.getroot().attrib.get('dialecte')
    for entry in tree.iterfind('entry'):
        yield ModernForm(language, entry.find('hw').text,
                         entry.find('gl').text)

def read_lexicons(languages, family):
    for language in languages:
        yield (language,
               list(read_lexicon(f'RE7/DATA/{family}/{family}.{language}.data.xml')))

# Returns a mapping from reconstructions to its supporting forms
def project_back(lexicons, parameters):
    reconstructions = {}
    for (language, lexicon) in lexicons:
        daughter_form = lambda c: c.daughter_forms[language]
        count = 0
        for modern_form in lexicon:
            for cs in iter(tokenize(modern_form.form, parameters, daughter_form)):
                count += 1
                reconstructions.setdefault(cs, []).append(modern_form)
        print('{}: {} forms, {} reconstructions'
              .format(language, len(lexicon), count))
    return reconstructions

def filter_sets(projections):
    cognate_sets = set()
    for reconstruction, support in projections.items():
        if len(support) > 1:
            cognate_sets.add((reconstruction, frozenset(support)))
    print('only {} sets with more than 1 supporting form'.format(len(cognate_sets)))
    return cognate_sets

# throw away sets whose supporting forms are a subset of another's
def filter_subsets(cognate_sets):
    losers = set()
    for cognate_set in cognate_sets:
        (c1, supporting_forms1) = cognate_set
        for (c2, supporting_forms2) in cognate_sets:
            if supporting_forms1 < supporting_forms2:
                losers.add(cognate_set)
                continue
    print('threw away {} subsets'.format(len(losers)))
    return cognate_sets - losers

# pick a representative from sets with the same surface protoform string
def unique_surface_forms(cognate_sets):
    uniques = set()
    for cognate_set in cognate_sets:
        proto_form = correspondences_as_proto_form_string(cognate_set[0])
        if not any(proto_form == correspondences_as_proto_form_string(c2) for (c2, _) in uniques):
            uniques.add(cognate_set)
    print('{} unique surface forms'.format(len(uniques)))
    return uniques
            
def batch_upstream(lexicons, params):
    return unique_surface_forms(filter_subsets((filter_sets(project_back(lexicons, params)))))

def print_sets(sets):
    for (cs, supporting_forms) in sets:
        print(correspondences_as_proto_form_string(cs) + ' ' +
              ' '.join([c.id for c in cs]))
        print('\n'.join([repr(modern_form) for modern_form in supporting_forms]))
        print('\n')

def dump_sets(sets, filename):
    out = sys.stdout
    with open(filename, 'w') as sys.stdout:
        print_sets(sets)
    sys.stdout = out

# example lexicon and parameters
demo93_names = ['gha', 'ris', 'sahu', 'man', 'mar', 'syang', 'tag', 'tuk']
demo93 = list(read_lexicons(demo93_names, 'DEMO93'))
params = read_correspondence_file('RE7/DATA/DEMO93/DEMO93.C794DEM.corrs.xml', 'DEMO93', demo93_names)
