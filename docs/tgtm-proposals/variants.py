# -*- coding: utf-8 -*-
"""Variant matching for the merged TGTM MELs: is gloss A just a plural / singular / accent / punctuation / spacing variant of gloss B?

Used ONLY by make_merged_mels.py to decide which MEL a stray gloss belongs to; no gloss is ever rewritten and the engine is unchanged.
Two kinds of variant, never combined (a plural AND an accent change at once is too loose: 'près' -> 'pres' -> 'press'):
  spelling  same letters up to case, accents, punctuation and spacing:  key(g) = folded key  ('rice-field' ~ '*rice field', 'ail' ~ 'aïl')
  number    plural <-> singular with the accents kept:                  plural_keys(g) over key_a(g)  ('brèdes' ~ 'brède', 'chevaux' ~ 'cheval')
key_a(g) keeps accents; key(g) removes them.  Both are for *comparison* only, no gloss is rewritten.
Over-generation of plural partners is harmless because a variant only matters if it equals the key of a gloss that really is in some MEL.
"""
import re, unicodedata

def fold(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s.lower().strip()) if unicodedata.category(c) != 'Mn')
def key(s):
    return re.sub(r'[^a-z0-9]+', ' ', fold(s)).strip()

_IRREG = [('man', 'men'), ('woman', 'women'), ('child', 'children'), ('foot', 'feet'), ('tooth', 'teeth'), ('goose', 'geese'),
          ('mouse', 'mice'), ('louse', 'lice'), ('ox', 'oxen'), ('person', 'people'), ('wife', 'wives'), ('knife', 'knives'),
          ('life', 'lives'), ('leaf', 'leaves'), ('wolf', 'wolves'), ('half', 'halves'), ('shelf', 'shelves'),
          ('oeil', 'yeux'), ('os', 'os'), ('ciel', 'cieux'), ('travail', 'travaux')]
_PAIR = {}
for a, b in _IRREG:
    _PAIR.setdefault(a, set()).add(b); _PAIR.setdefault(b, set()).add(a)

def word_variants(w):
    """plural/singular partners of one folded word (English + French); may include non-words"""
    out = set(_PAIR.get(w, ()))
    if len(w) < 3: return out
    # ---- to the singular
    if w.endswith('ies') and len(w) > 4: out.add(w[:-3] + 'y')
    if w.endswith('ves') and len(w) > 4: out |= {w[:-3] + 'f', w[:-3] + 'fe'}
    if w.endswith(('ses', 'xes', 'zes', 'ches', 'shes', 'oes')) : out.add(w[:-2])
    if w.endswith('aux') and len(w) > 4: out.add(w[:-3] + 'al')
    if w.endswith('eaux'): out.add(w[:-1])
    if w.endswith('eux'): out.add(w[:-1])
    if w.endswith('oux'): out.add(w[:-1])
    if w.endswith('s') and not w.endswith(('ss', 'us', 'is')): out.add(w[:-1])
    if w.endswith('x') and not w.endswith('ex') : out.add(w[:-1])
    # ---- to the plural
    if w.endswith('y') and w[-2] not in 'aeiou': out.add(w[:-1] + 'ies')
    if w.endswith(('s', 'x', 'z', 'ch', 'sh', 'o')): out.add(w + 'es')
    if w.endswith('f'): out.add(w[:-1] + 'ves')
    if w.endswith('fe'): out.add(w[:-2] + 'ves')
    if w.endswith('al'): out.add(w[:-2] + 'aux')
    if w.endswith(('eau', 'eu', 'ou')): out.add(w + 'x')
    out.add(w + 's')
    out.discard(w)
    return out

def key_a(s):                      # accents kept (for the plural test)
    return re.sub(r"[\W_]+", ' ', s.lower()).strip()

def compact(k):
    return k.replace(' ', '')

def plural_keys(g):
    """plural / singular partners of g (accent-preserving), for the last word and, for 'pieds nus'-type phrases, the first"""
    words = key_a(g).split()
    if not words: return set()
    out = set()
    for v in word_variants(words[-1]): out.add(' '.join(words[:-1] + [v]))
    if len(words) > 1:
        for v in word_variants(words[0]): out.add(' '.join([v] + words[1:]))
    out.discard(key_a(g))
    return out
