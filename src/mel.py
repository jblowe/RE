import re
import collections
import time
from nltk.corpus import stopwords as _nltk_stopwords
from nltk.corpus import wordnet as _wordnet

class Mel:
    def __init__(self, glosses, id, gloss_langs=None):
        self.glosses = glosses
        self.id = id
        # Optional {gloss_text: xml:lang value}, for glosses whose <gl> element
        # carried an xml:lang attribute in the MEL file. Not every gloss has
        # one, so this only covers the subset that do.
        self.gloss_langs = gloss_langs or {}

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

# Stopwords, keyed by the same xml:lang codes MEL/reflex <gl> elements use.
# Loaded once at import time (not memoized per-call -- there's nothing to
# memoize, this is a fixed linguistic resource, read once like the MEL file
# itself). Union used whenever a gloss's language is unknown -- see
# _stopwords_for.
_STOPWORDS_EN = frozenset(_nltk_stopwords.words('english'))
_STOPWORDS_FR = frozenset(_nltk_stopwords.words('french'))
_STOPWORDS_BY_LANG = {'en': _STOPWORDS_EN, 'fr': _STOPWORDS_FR}
_STOPWORDS_UNION = _STOPWORDS_EN | _STOPWORDS_FR

def _stopwords_for(lang):
    '''Stopword set for xml:lang code *lang*; the union of all known
    languages when *lang* is None/unrecognized (e.g. the "xx" placeholder
    code, or no xml:lang at all).'''
    return _STOPWORDS_BY_LANG.get(lang, _STOPWORDS_UNION)

# Particles that combine with a leading verb to form an English phrasal verb,
# e.g. "give" + "up" -> "give up". Not every combination is a real phrasal
# verb (that's confirmed via WordNet in _find_phrasal_verb) -- this list is
# just the set of candidate particles to try.
_PHRASAL_PARTICLES = {
    'en': frozenset('''about across after against along apart aside at away
        back behind by down for forth forward in into off on out over past
        round through to up upon with without'''.split()),
    # French particle list not yet available; add as {'fr': frozenset(...)}
    # once we have one -- _find_phrasal_verb already looks it up by lang.
}

def _find_phrasal_verb(phrase, lang):
    '''If *phrase* is <verb> <...> <particle> <...> and "verb_particle" is a
    real WordNet lemma (e.g. "give up" -> give_up), return (verb, particle),
    both lowercased. Otherwise None.

    Assumes the first word is the verb -- true for the dictionary-style,
    verb-first glosses used here ("give up the ship", not full sentences).
    WordNet is the actual arbiter of whether verb+particle is a genuine,
    distinct lexical entry; the particle list just supplies candidates fast
    enough not to look up every word pair in every gloss.
    '''
    particles = _PHRASAL_PARTICLES.get(lang or 'en')
    if not particles:
        return None
    words = phrase.split()
    if len(words) < 2:
        return None
    verb = words[0].lower()
    for w in words[1:]:
        particle = w.strip('.,;:!?').lower()
        if particle in particles and _wordnet.synsets(f'{verb}_{particle}'):
            return verb, particle
    return None

# ─────────────────────────────────────────────────────────────────────────────
# Previous pipeline, kept only for side-by-side comparison (see
# compare_normalize_gloss.py / GLOSS_NORMALIZATION.md) -- no longer called
# from normalize_gloss's callers (compile_associated_mels, filter_mel.py,
# etc; see normalize_gloss below for the pipeline actually in use).
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
def normalize_gloss_current(gloss):
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


# ─────────────────────────────────────────────────────────────────────────────
# The active pipeline -- used by compile_associated_mels/_candidates_lower
# (and so by everything that resolves a gloss to a MEL) and by
# filter_mel.py. Supersedes normalize_gloss_current above, which is kept
# only for comparison.
#
# Steps 1-5 are unchanged from normalize_gloss_current; adds two steps:
#   6. Detect an English phrasal verb at the head of the phrase (verb +
#      particle, confirmed as a real WordNet lemma -- see
#      _find_phrasal_verb) and add it as its own candidate, e.g.
#      "give up the ship" -> also yields "give up". The verb and particle
#      are excluded from the individual words below for *this* phrase, since
#      alone they usually mean something different ("give" != "give up").
#   7. Individual words drop stopwords (language-aware -- see
#      _stopwords_for; the union of all known languages when the gloss's
#      language isn't known).
#
# lang is the gloss's xml:lang code if known (e.g. 'en', 'fr'), else None.
# See GLOSS_NORMALIZATION.md for the full write-up and worked examples.
def normalize_gloss(gloss, lang=None):
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
    base_phrases = []             # phrase-level candidates only, for step 7
    consumed_by_phrase = {}       # base phrase -> {verb, particle} from step 6
    for v in variants:
        for part in re.split(r'[/,;:]', v):
            part = part.strip().strip('?').rstrip('!.')
            part = _strip_particles(part.strip())
            if not part or part in seen:
                continue
            seen.add(part)
            phrases.append(part)
            base_phrases.append(part)

            # 6. Phrasal verb detection.
            found = _find_phrasal_verb(part, lang)
            if found:
                verb, particle = found
                mwe = f'{verb} {particle}'
                if mwe not in seen:
                    seen.add(mwe)
                    phrases.append(mwe)
                consumed_by_phrase[part] = {verb, particle}

    # 7. Individual words, excluding ones consumed by a phrasal verb in this
    #    phrase and stopwords.
    stopwords_set = _stopwords_for(lang)
    for phrase in base_phrases:
        consumed = consumed_by_phrase.get(phrase, ())
        for word in phrase.split():
            word = word.strip()
            if not word:
                continue
            wl = word.lower()
            if wl in consumed or wl in stopwords_set:
                continue
            if word not in seen:
                seen.add(word)
                phrases.append(word)

    return tuple(phrases)


# ─────────────────────────────────────────────────────────────────────────────
# A verbatim port of the previous ("legacy") normalize_gloss from
# ~/GitHub/RE.dev/src/mel.py (an earlier, separate repo), kept only for
# side-by-side comparison against normalize_gloss / normalize_gloss_current
# on real data. Not wired into anything. No dependency on any other legacy
# code -- it only ever used `re`, already imported here, so it ports over
# unchanged.
#
# It is much cruder than the current pipeline: no parenthetical/bracket
# handling at all (those characters just stay glued to whatever word they're
# next to, since splitting is on '/', ' ', ',' only), no leading-particle
# stripping, and critically, it splits on *spaces* -- so multi-word phrases
# (e.g. a MEL gloss like "clay pot") never survive as their own candidate,
# only their individual words do. It also returns a plain list with no
# deduplication, unlike the tuple-of-deduplicated-candidates the other two
# functions return.
def normalize_gloss_legacy(gloss):
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
