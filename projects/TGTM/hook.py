import read
import serialize
import os
import sys
import collections
from utils import cd

base_dir = os.path.dirname(__file__)

print(f'base_dir {base_dir}')

def fuzzy_string(mapping, string):
    length = len(string)
    old_string = string
    new_string = []
    while string != '':
        (longest_candidate, its_target, its_len) = (None, None, 0)
        # Partition initials into most specific rules to be
        # chosen. The longer the initial, the more priority it gets.
        for (initial, target) in mapping.items():
            if string.startswith(initial) and len(initial) > its_len:
                (longest_candidate, its_target, its_len) = (initial, target, len(initial))
        if longest_candidate:
            new_string.append(its_target)
            string = string[its_len:]
        else:
            new_string.append(string[0])
            string = string[1:]
    return ''.join(new_string)

# map targets to representatives
def invert_fuzzy_map(mapping):
    invert = collections.defaultdict(list)
    for ((dialect, representative), target) in mapping.items():
        invert[(dialect, target)].append(representative)
    return invert

def fuzzy_table(mapping, settings):
    parameters = read.read_correspondence_file(os.path.join(settings.directory_path,
                                                            settings.proto_languages['tgtm']),
                                               '-------',
                                               list(settings.upstream['tgtm']),
                                               'tgtm',
                                               settings.mel_filename)
    print('fuzzying table of correspondences')
    invert = invert_fuzzy_map(mapping)
    for c in parameters.table.correspondences:
        modified = False
        for (language, reflexes) in c.daughter_forms.items():
            for reflex in reflexes:
                if (language, reflex) in invert:
                    modified = True
                    c.daughter_forms[language] = list(set(c.daughter_forms[language] + invert[(language, reflex)]))
        if modified:
            pass
            #c.id += '*'
    print('writing fuzzied table')
    new_table_file = 'fuzz' + settings.proto_languages['tgtm']
    serialize.serialize_correspondence_file(os.path.join(base_dir, new_table_file),
                                            parameters)
    # make settings use these instead.
    settings.proto_languages['tgtm'] = new_table_file

def fuzzy_lexicons(mapping, settings):
    attested_lexicons = read.read_attested_lexicons(settings)
    print('fuzzying lexicons')
    for (language, lexicon) in attested_lexicons.items():
        specific_mapping = {representative: target
                            for ((language1, representative), target) in mapping.items()
                            if language == language1}
        if specific_mapping:
            for form in lexicon.forms:
                form.glyphs = fuzzy_string(specific_mapping, form.glyphs)
    print('writing fuzzied lexicons')
    serialize.serialize_lexicons(attested_lexicons.values(), base_dir, '.fuzz.data.xml')
    # make settings use these instead.
    settings.attested = {lexicon.language: f'{lexicon.language}.fuzz.data.xml'
                         for lexicon in attested_lexicons.values()}

def generate_xml_data():
    print('running pipeline to generate data files')
    code_dir = os.path.join('..', '..', '..', 'src')
    with cd(os.path.join(base_dir)):
        with open('pipeline.sh', 'r', encoding='utf-8') as commands:
            for command in commands:
                if command[0] == '#':
                    # print(command.strip())
                    continue
                if 'perl' in command or 'python' in command:
                    command = command.replace('$1', code_dir)
                    # print(command.strip())
                    exit_code = os.system(command.strip())
                    if exit_code != 0:
                        sys.exit(exit_code)

def run_load_hooks(arg, settings):
    generate_xml_data()
    if arg.fuzzy is not None:
        print(f"fuzzying using {settings.other['fuzzies'][arg.fuzzy]}")
        fuzzy_table(read.read_fuzzy_file(os.path.join(base_dir, settings.other['fuzzies'][arg.fuzzy])),
                    settings)
    else:
        return
