import re
import collections
import time

class Mel:
    def __init__(self, glosses, id):
        self.glosses = glosses
        self.id = id
        
    def __repr__(self):
        return f'<Mel({self.id}, {self.glosses})>'

    def __str__(self):
        return f'mel {self.id}: [{self.glosses[0]}])>'

class DefaultMel(Mel):
    def __repr__(self):
        return '<DefaultMel>'

    def __str__(self):
        return 'No mel'

default_mel = DefaultMel([], '')

# A gloss G is deemed to map to a mel if any of the mel glosses are
# present in the set of `normalized' glosses for G.
def compile_associated_mels(mels, glosses):
    '''Compile a mapping of glosses to mels.'''
    elapsed_time = time.time()
    if mels is None:
        return None
    association = collections.defaultdict(set)
    # Precompute normalized glosses for each gloss.
    gloss_to_norm = {gloss: normalize_gloss(gloss) for gloss in glosses}

    # Invert: normalized gloss -> set of original glosses
    norm_to_glosses = collections.defaultdict(set)
    for gloss, normalized_glosses in gloss_to_norm.items():
        for normalized_gloss in normalized_glosses:
            norm_to_glosses[normalized_gloss].add(gloss)

    # For each mel, associate directly and via normalized glosses
    for mel in mels:
        mel_glosses = mel.glosses
        for gloss in mel_glosses:
            association[gloss].add(mel)
        for mel_gloss in mel_glosses:
            if mel_gloss in norm_to_glosses:
                for gloss in norm_to_glosses[mel_gloss]:
                    association[gloss].add(mel)
    print('{:.2f} seconds to compile {} associated MELs.'.format(time.time() - elapsed_time, len(association)))
    return association

default_mel_singleton = [default_mel]

def associated_mels(association, gloss, only_with_mel):
    '''Lookup gloss in the table of MEL associations.'''
    default = [] if only_with_mel else default_mel_singleton
    return association.get(gloss, default)

def search_mels(gloss, mel_glosses):
    glosses = normalize_gloss(gloss)
    return any((mel_gloss in glosses
                for mel_gloss in mel_glosses))

# Split a gloss into a list of `normalized' glosses.
def normalize_gloss(gloss):
    glosses = re.split(r'[/ ,]', gloss.replace('*', ''))
    if '|' in gloss:
        for i, g in enumerate(glosses):
            # handle lexware | delimiter: replace gloss with two term -- one trimmed, one with | removed
            if '|' in g:
                glosses.append(g.replace('|', ''))
                glosses.append(re.sub(r'\|.*', '', g))
                del glosses[i]
    glosses = [g for g in glosses if g != '']
    return glosses
