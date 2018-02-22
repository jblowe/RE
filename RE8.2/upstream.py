import itertools
import read
import regex as re
import sys
import serialize

class SyllableCanon:
    def __init__(self, sound_classes, syllable_regex):
        self.sound_classes = sound_classes
        self.regex = re.compile(syllable_regex)

class Correspondence:
    def __init__(self, id, context, syllable_type, proto_form, daughter_forms):
        self.id = id
        # context is a tuple of left and right contexts
        self.context = context
        self.syllable_type = syllable_type
        self.proto_form = proto_form
        # daughter forms indexed by language
        self.daughter_forms = daughter_forms

    def __repr__(self):
        return f'<Correspondence({self.id}, {self.syllable_type}, {self.proto_form[0]}>)'

def correspondences_as_proto_form_string(cs):
    return ''.join(str(c.proto_form) for c in cs)

# imperative interface
class TableOfCorrespondences:
    def __init__(self, family_name, daughter_languages):
        self.correspondences = []
        self.family_name = family_name
        self.daughter_languages = daughter_languages

    def add_correspondence(self, correspondence):
        self.correspondences.append(correspondence)

class Parameters:
    def __init__(self, table, syllable_canon):
        self.table = table
        self.syllable_canon = syllable_canon

    def serialize(self, filename):
        serialize.serialize_correspondence_file(filename, self)

class ModernForm:
    def __init__(self, language, form, gloss):
        self.language = language
        self.form = form
        self.gloss = gloss

    def __str__(self):
        return f'{self.language} {self.form}: {self.gloss}'

class ProjectSettings:
    def __init__(self, correspondence_file, upstream, downstream):
        self.correspondence_file = correspondence_file
        self.upstream = upstream
        self.downstream = downstream

# tokenize an input string and return the set of all parses
# which also conform to the syllable canon
def tokenize(form, parameters, accessor):
    parses = set()
    regex = parameters.syllable_canon.regex
    def gen(form, parse, syllable_parse):
        if form == '' and regex.fullmatch(syllable_parse):
            parses.add(tuple(parse))
        # we can abandon parses that we know can't be completed
        # to satisfy the syllable canon. for DEMO93 this cuts the
        # number of branches from 182146 to 61631
        if regex.fullmatch(syllable_parse, partial=True) is None:
            return
        for i in range(1, len(form) + 1):
            for c in parameters.table.correspondences:
                if form[:i] in accessor(c):
                    gen(form[i:], parse + [c], syllable_parse + c.syllable_type)
    gen(form, [], '')
    return parses

# set of all possible forms for a daughter language given correspondences
def postdict_forms_for_daughter(correspondences, daughter):
    return frozenset(''.join(token) for token in
                     itertools.product(*[c.daughter_forms[daughter]
                                         for c in correspondences]))

# return a mapping from daughter language to all possible forms given a proto-form
def postdict_daughter_forms(proto_form, parameters):
    postdict = {}  # pun?
    # big speed difference between [c.proto_form] vs c.proto_form
    # c.proto_form does lots of slow substring comparisons. [c.proto_form]
    # parallels the usage of the other daughter form accessors
    for cs in iter(tokenize(proto_form, parameters, lambda c: [c.proto_form])):
        for language in parameters.table.daughter_languages:
            postdict[language] = postdict_forms_for_daughter(cs, language)
    return postdict

# return a mapping from reconstructions to its supporting forms
def project_back(lexicons, parameters):
    reconstructions = {}
    for (language, lexicon) in lexicons:
        daughter_form = lambda c: c.daughter_forms[language]
        count = 0
        for modern_form in lexicon:
            for cs in iter(tokenize(modern_form.form, parameters, daughter_form)):
                count += 1
                reconstructions.setdefault(cs, []).append(modern_form)
        print(f'{language}: {len(lexicon)} forms, {count} reconstructions')
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
                break
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
              ' '.join(c.id for c in cs))
        print('\n'.join(map(str, supporting_forms)))
        print('\n')

def dump_sets(sets, filename):
    out = sys.stdout
    with open(filename, 'w') as sys.stdout:
        print_sets(sets)
    sys.stdout = out


if __name__ == "__main__":

    base_dir = "../RE7/DATA"
    # lexicons and parameters
    try:
        project = sys.argv[1]
        try:
            settings_type = sys.argv[2]
        except:
            settings_type = 'default'
            try:
                run = sys.argv[3]
            except:
                run = 'default'
    except:
        print('no project specified. Try "DEMO93" if you like')
        sys.exit(1)

    settings = read.read_settings_file(f'{base_dir}/{project}/{project}.{settings_type}.parameters.xml')
    lexicons = list(read.read_lexicons(settings.upstream, base_dir, project))
    params = read.read_correspondence_file(f'{base_dir}/{project}/{settings.correspondence_file}', project, settings.upstream)

    B = batch_upstream(lexicons, params)
    #print_sets(B)
    dump_sets(B, f'{base_dir}/{project}/{project}.{run}.sets.txt')
