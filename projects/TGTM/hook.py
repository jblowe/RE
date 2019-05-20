import read
import os

base_dir = os.path.dirname(__file__)

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

def fuzzy_lexicons(mapping, attested_lexicons):
    print('fuzzying in-memory lexicons')
    for (language, lexicon) in attested_lexicons.items():
        specific_mapping = {representative: target
                            for ((language1, representative), target) in mapping.items()
                            if language == language1}
        if specific_mapping:
            for form in lexicon.forms:
                form.glyphs = fuzzy_string(specific_mapping, form.glyphs)

def run_load_hooks(settings, attested_lexicons):
    if 'fuzzy' in settings.other:
        return
        # KLUDGE: Modifies the forms in attested_lexicons in
        # place... Hence does not preserve the source form!
        fuzzy_lexicons(read.read_fuzzy_file(os.path.join(base_dir, settings.other['fuzzy'])),
                       attested_lexicons)
    else:
        return
