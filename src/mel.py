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

# Matches parenthetical or bracketed asides — e.g. "(of a person)", "[archaic]".
_PAREN_RE = re.compile(r'\([^)]*\)|\[[^\]]*\]|<[^>]*>')

# Grammar particles stripped from the *beginning* of a phrase when more words follow.
# "to give" → "give";  "be sick" → "sick";  "to be hungry" → "be hungry" → "hungry".
_PARTICLES = ('to', 'be')

def _strip_particles(phrase):
    for particle in _PARTICLES:
        words = phrase.split()
        if len(words) > 1 and words[0] == particle:
            phrase = ' '.join(words[1:])
    return phrase.strip()

# Split a gloss string into a tuple of normalised candidate glosses.
#
# Pipeline:
#   1. Remove parenthetical / bracketed asides and their delimiters.
#   2. Remove proto-form marker (*).
#   3. Handle Lexware | delimiter *before* splitting so variants are correct:
#      "water|rain" → ["waterrain", "water"]   (pipe removed / truncated).
#   4. Split each variant on alternative-gloss separators: / , ; :
#      Spaces are *within-phrase* and must NOT split — MEL glosses are stored
#      as multi-word phrases ("clay pot") and splitting on spaces would prevent
#      them from ever matching.
#      The colon is included because lexicon glosses often use it as a
#      clarification separator, e.g. "boiled grain: ideally rice".
#   5. Strip leading grammar particles ('to', 'be') from each phrase.
#   6. Also yield every individual *word* from each phrase as an additional
#      candidate.  This handles descriptive glosses such as
#      "boiled grain: ideally rice, but more frequently maize or"
#      where content words ("grain", "rice") appear as single-word MEL glosses
#      but the phrase itself never matches.  Function words ("but", "more",
#      "or", "ideally") are harmless because they will simply never appear in
#      any MEL gloss set.
#   7. Drop empty strings and deduplicate (preserving order: phrases first,
#      individual words after).
#
# Returns a tuple of normalized candidate strings.
def normalize_gloss(gloss):
    # 1. Strip parentheticals / brackets.
    gloss = _PAREN_RE.sub('', gloss)
    # 2. Strip lexware keyterm marker
    gloss = gloss.replace('*', '')

    # 3. Lexware | handling — produce variants before splitting on /,;:.
    if '|' in gloss:
        variants = [gloss.replace('|', ''), re.sub(r'\|.*', '', gloss)]
    else:
        variants = [gloss]

    # 4 & 5. Split on delimiter characters, strip trailing punctuation,
    #         and strip leading particles.
    seen = set()
    phrases = []
    for v in variants:
        for part in re.split(r'[/,;:]', v):
            part = part.strip().strip('?').rstrip('!.')
            part = _strip_particles(part.strip())
            if part and part not in seen:
                seen.add(part)
                phrases.append(part)

    # 6. Also add individual words from every phrase as additional candidates.
    for phrase in list(phrases):
        for word in phrase.split():
            word = word.strip()
            if word and word not in seen:
                seen.add(word)
                phrases.append(word)

    return tuple(phrases)


def _candidates_lower(gloss):
    """All lowercased comparison candidates for a gloss: the raw form plus all
    normalized variants."""
    return frozenset(c.lower() for c in (gloss,) + normalize_gloss(gloss))


# A gloss G is deemed to map to a mel if any of the mel glosses are
# present in the set of `normalized' glosses for G.
#
# This is the single gloss<->MEL matching pass for a run: call it once, over
# the complete universe of attested glosses (every gloss in every attested
# lexicon, known as soon as the lexicons are read), and reuse the resulting
# table everywhere a gloss needs to be resolved to a MEL -- at every level of
# the reconstruction tree, for coverage statistics, and for the annotated
# coverage report. Because each unique gloss is only ever normalized here,
# there is no need to cache normalize_gloss itself.
def compile_associated_mels(mels, glosses):
    '''Compile a mapping of glosses to mels.

    Each entry is itself a mapping mel -> set of that mel's own synonym
    glosses which caused the association, so callers that need to know
    *which* synonym matched (e.g. per-synonym usage counts for the coverage
    report) can recover it without a second matching pass -- see
    matched_synonyms() below.'''
    elapsed_time = time.time()
    if mels is None:
        return None
    association = collections.defaultdict(lambda: collections.defaultdict(set))

    # Invert: lowercased candidate → set of original glosses
    norm_to_glosses = collections.defaultdict(set)
    for gloss in glosses:
        for lc in _candidates_lower(gloss):
            norm_to_glosses[lc].add(gloss)

    # For each mel, associate directly and via normalized glosses.
    # MEL glosses are normalized with the same pipeline as reflex glosses so
    # that e.g. a MEL gloss "badigeonner (avec terre)" matches a reflex "badigeonner".
    for mel in mels:
        for mel_gloss in mel.glosses:
            association[mel_gloss][mel].add(mel_gloss)
            for lc in _candidates_lower(mel_gloss):
                for gloss in norm_to_glosses.get(lc, ()):
                    association[gloss][mel].add(mel_gloss)

    print('{:.2f} seconds to compile {} associated MELs.'.format(time.time() - elapsed_time, len(association)))
    return association

def associated_mels(association, gloss, only_with_mel):
    '''Lookup gloss in the table of MEL associations. Returns a list of Mels.'''
    entry = association.get(gloss) if association is not None else None
    if entry:
        return list(entry.keys())
    return [] if only_with_mel else [default_mel]

def matched_synonyms(association, gloss, mel):
    '''Return the set of *mel*'s own synonym glosses that matched *gloss*.'''
    if association is None:
        return frozenset()
    return association.get(gloss, {}).get(mel, frozenset())
