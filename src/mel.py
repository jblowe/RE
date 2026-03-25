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
    if gloss in mel_glosses:
        return [gloss]
    return [g for g in glosses if g in mel_glosses]

# Matches parenthetical or bracketed asides — e.g. "(of a person)", "[archaic]".
_PAREN_RE = re.compile(r'\([^)]*\)|\[[^\]]*\]')

# Grammar particles stripped from the *beginning* of a phrase when more words follow.
# "to give" → "give";  "be sick" → "sick";  "to be hungry" → "be hungry" → "hungry".
_PARTICLES = ('to', 'be')

def _strip_particles(phrase):
    """Iteratively remove leading grammar particles from a phrase."""
    for particle in _PARTICLES:
        words = phrase.split()
        if len(words) > 1 and words[0] == particle:
            phrase = ' '.join(words[1:])
    return phrase.strip()

# Split a gloss string into a list of normalised candidate glosses.
#
# Pipeline:
#   1. Remove parenthetical / bracketed asides and their delimiters.
#   2. Remove proto-form marker (*).
#   3. Handle Lexware | delimiter *before* splitting so variants are correct:
#      "water|rain" → ["waterrain", "water"]   (pipe removed / truncated).
#   4. Split each variant on alternative-gloss separators: / , ;
#      Spaces are *within-phrase* and must NOT split — MEL glosses are stored
#      as multi-word phrases ("clay pot") and splitting on spaces would prevent
#      them from ever matching.
#   5. Strip leading grammar particles ('to', 'be') from each phrase.
#   6. Drop empty strings and deduplicate (preserving order).
def normalize_gloss(gloss):
    # 1. Strip parentheticals / brackets.
    gloss = _PAREN_RE.sub('', gloss)
    # 2. Strip proto-form marker.
    gloss = gloss.replace('*', '')

    # 3. Lexware | handling — produce variants before splitting on /,;.
    if '|' in gloss:
        variants = [gloss.replace('|', ''), re.sub(r'\|.*', '', gloss)]
    else:
        variants = [gloss]

    # 4 & 5. Split and strip particles.
    seen = set()
    result = []
    for v in variants:
        for part in re.split(r'[/,;]', v):
            part = _strip_particles(part.strip())
            if part and part not in seen:
                seen.add(part)
                result.append(part)
    return result
