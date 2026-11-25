# -*- coding: utf-8 -*-
"""Decide the xml:lang (en / fr / und) of a MEL gloss.  Never alters the gloss itself (no accent folding).

Evidence, in order:
  1. DATA  -- which lexicons use the string as a whole gloss (or a ,;/-separated piece of one).  The TGTM lexicons have a
              known gloss language (mar, syang, tang = French; gha, pra, ris, sahu, tag, tuk, nar = English).
              Only English lexicons -> 'en'; only French -> 'fr'; both -> 'und' (a real homograph: place, table, sale ...).
  2. WORDS -- no data hit: NLTK stopwords (French/English function words) and accents, then WordNet (eng vs fra).
              A string WordNet knows in both languages -> 'und'.
  3. otherwise 'und'.
'und' is the BCP 47 code for "undetermined" (the repo's older placeholder was 'xx').
"""
import re, unicodedata, collections
from lxml import etree
from nltk.corpus import wordnet as wn, stopwords

DATA_DIR = '/Users/johnlowe/GitHub/RE-Tamangish-Files/TGTM/'
LEXICON_LANG = {'gha': 'en', 'pra': 'en', 'ris': 'en', 'sahu': 'en', 'tag': 'en', 'tuk': 'en', 'nar': 'en',
                'mar': 'fr', 'syang': 'fr', 'tang': 'fr'}
EN = set(stopwords.words('english'))
FR = set(stopwords.words('french')) | {'avoir', 'être'}
_PIECE = re.compile(r'\s*[,;/]\s*')
_PAREN = re.compile(r'\([^)]*\)|\[[^\]]*\]')
_WORD = re.compile(r"[^\W\d_]+(?:['’-][^\W\d_]+)*")

def _clean(s):
    return re.sub(r'\s+', ' ', _PAREN.sub(' ', s.replace('*', ''))).strip().lower()

def _data_evidence():
    ev = collections.defaultdict(collections.Counter)      # lower string -> {'en': n, 'fr': n}
    for lg, lang in LEXICON_LANG.items():
        try:
            tree = etree.parse(f'{DATA_DIR}TGTM.{lg}.data.xml')
        except OSError:
            continue
        for el in tree.iter('gl'):
            if not (el.text and el.text.strip()):
                continue
            whole = _clean(el.text)
            # the French lexicons carry some English glosses (and vice versa): trust the words when they are decisive
            own = _word_signal(whole)
            use = own if own in ('en', 'fr') else lang
            ev[whole][use] += 1
            for piece in _PIECE.split(whole):
                piece = re.sub(r'^(to|be|se) ', '', piece.strip())
                if piece:
                    ev[piece][use] += 1
    return ev
_EV = None

import functools
@functools.lru_cache(maxsize=None)
def _wn(w):
    return len(wn.synsets(w, lang='eng')), len(wn.synsets(w, lang='fra'))

def _data_signal(g):
    cand = {g, re.sub(r'^(to|be|se) ', '', g)}
    ev = collections.Counter()
    for c in cand:
        ev.update(_EV.get(c, {}))
    n = ev['en'] + ev['fr']
    if not n: return None
    if ev['fr'] <= 0.1 * n: return 'en'          # a few stray uses (typos, loans) do not make a word bilingual
    if ev['en'] <= 0.1 * n: return 'fr'
    return 'und'                                  # a real homograph: used as a gloss by English *and* French lexicons

def _word_signal(g):
    words = _WORD.findall(g)
    if not words: return None
    fr = sum(w in FR and w not in EN for w in words)
    en = sum(w in EN and w not in FR for w in words)
    if any(unicodedata.normalize('NFD', c) != c for c in g) and not en: return 'fr'
    if fr > en: return 'fr'
    if en > fr: return 'en'
    ne = nf = 0
    for w in words:
        a, b = _wn(w); ne += a; nf += b
    if not (ne or nf): return None
    if ne >= 3 * nf: return 'en'                  # WordNet-fra (OMW) lists many English words as French lemmas,
    if nf >= 3 * ne: return 'fr'                  # so ask which language is *predominant*, not merely present
    return 'und'

def lang_of(gloss, old=None):
    """-> (code, basis).  old = an existing xml:lang tag on the gloss, used as one more vote ('xx'/None ignored)."""
    global _EV
    if _EV is None:
        _EV = _data_evidence()
    g = _clean(gloss)
    d, w = _data_signal(g), _word_signal(g)
    o = old if old in ('en', 'fr') else None
    if d == 'und':
        return 'und', 'data-both'
    votes = collections.Counter(v for v in (d, w, o) if v in ('en', 'fr'))
    if not votes:
        return 'und', 'no-evidence' if w is None else 'wordnet-both'
    (a, na), *rest = votes.most_common()
    if rest and rest[0][1] == na:
        return 'und', 'conflict'
    basis = 'data' if d == a else 'words' if w == a else 'existing-tag'
    return a, basis


# ---- accent restoration (the MEL must hold the real French word, but the engine never folds accents) -------------
def _fold(x):
    return ''.join(c for c in unicodedata.normalize('NFD', x) if unicodedata.category(c) != 'Mn')

_ACC = None
def accented_forms(g):
    """Accented French spellings whose de-accented form is g (lower-case), from WordNet-fra lemmas and French-lexicon glosses."""
    global _ACC
    if _ACC is None:
        _ACC = collections.defaultdict(set)
        for lem in wn.all_lemma_names(lang='fra'):
            lem = lem.replace('_', ' ').lower()
            f = _fold(lem)
            if f != lem: _ACC[f].add(lem)
        for k, c in _EV.items():
            f = _fold(k)
            if f != k and c['fr'] and not c['en']: _ACC[f].add(k)
    return _ACC.get(g.lower(), set())

def valid_french_as_is(g):
    """g itself is a French word/gloss (so it is not merely a de-accented spelling)."""
    return bool(wn.synsets(g.replace(' ', '_'), lang='fra')) or (_EV is not None and _EV.get(g.lower(), {}).get('fr', 0) > 0)
