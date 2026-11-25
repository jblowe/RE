# -*- coding: utf-8 -*-
"""Propose additions to TGTM.hand.mel.xml from sound-only (no-MEL) sets.

For every sound-only set, every pair of members whose glosses are not already
linked by the hand MEL is scored on independent evidence:
  E  the two glosses share a normalized candidate  (mel._candidates_lower, the engine's own normalizer)
  W  they share a WordNet synset (English + French via OMW), top-3 senses only
  M  they co-occur in a small (<=15 glosses) MEL from another source file
A pair is ACCEPTED when E, or W+M, or M in >=2 different source files.
Accepted pairs are merged into proposed MEL entries (connected components of glosses).
"""
import sys, re, glob, itertools, collections
sys.path.insert(0, '/Users/johnlowe/GitHub/RE2/src')
from lxml import etree
import an
from mel import _candidates_lower
from nltk.corpus import wordnet as wn

SB = 'sandbox2/TGTM/'
RUN = sys.argv[1] if len(sys.argv) > 1 else 'r3_nomel'
OTHER = ['hand-extended-v4', 'clics', 'wordnet', 'es-reduced']
SMALL = 15
an.RUNS = an.RUNS.replace('sandbox/TGTM', 'sandbox2/TGTM')

def read_mels(path):
    return [[g.text for g in m.findall('gl') if g.text] for m in etree.parse(path).getroot().findall('mel')]

hand = read_mels(SB + 'TGTM.hand.mel.xml')
from mel import normalize_gloss
prim_cache = {}
def P(g):
    """primary comparison glosses: each comma/semicolon alternative, plus its normalized head -- never sub-tokens of a phrase"""
    if g not in prim_cache:
        out = set()
        for alt in re.split(r'[;,/]', g):
            alt = alt.strip().lower()
            if not alt: continue
            out.add(alt)
            n = normalize_gloss(alt)
            if n: out.add(n[0].lower())
        prim_cache[g] = frozenset(x for x in out if len(x) > 1)
    return prim_cache[g]
cand_cache = {}
def C(g):
    if g not in cand_cache:
        cand_cache[g] = frozenset(c for c in _candidates_lower(g) if len(c) > 1)
    return cand_cache[g]

# gloss(candidate) -> hand mels
hand_idx = collections.defaultdict(set)
for i, m in enumerate(hand):
    for g in m:
        for c in C(g): hand_idx[c].add(i)
def hand_linked(g1, g2):
    a = set().union(*[hand_idx.get(c, set()) for c in C(g1)]) if C(g1) else set()
    b = set().union(*[hand_idx.get(c, set()) for c in C(g2)]) if C(g2) else set()
    return bool(a & b)

# other small MELs: candidate -> {(file, i)}
other_idx = collections.defaultdict(set)
for f in OTHER:
    try: mels = read_mels('sandbox/TGTM/TGTM.%s.mel.xml' % f)
    except Exception as e: print('skip', f, e); continue
    for i, m in enumerate(mels):
        if len(m) > SMALL: continue
        for g in m:
            for c in C(g): other_idx[c].add((f, i))
def M_files(g1, g2):
    a = set().union(*[other_idx.get(c, set()) for c in P(g1)]) if P(g1) else set()
    b = set().union(*[other_idx.get(c, set()) for c in P(g2)]) if P(g2) else set()
    return {f for f, i in (a & b)}

syn_cache = {}
def syns(c):
    if c not in syn_cache:
        w = c.replace(' ', '_')
        s = set(wn.synsets(w, lang='eng')[:3]) | set(wn.synsets(w, lang='fra')[:3])
        syn_cache[c] = s
    return syn_cache[c]
def W(g1, g2):
    s1 = set().union(*[syns(c) for c in P(g1) if c.count(' ') <= 1]) if C(g1) else set()
    s2 = set().union(*[syns(c) for c in P(g2) if c.count(' ') <= 1]) if P(g2) else set()
    return bool(s1 & s2)

def evidence(g1, g2):
    e = bool(P(g1) & P(g2))
    w = W(g1, g2)
    m = M_files(g1, g2)
    ok = e or (w and m) or len(m) >= 2
    border = (not ok) and (w or bool(m))
    return ok, e, w, sorted(m), border

d, sets = an.load(RUN)
rows = []; accepted = []; borderline = []; stats = collections.Counter()
for sid, s in sets.items():
    mem = [d[m] for m in s['mem']]
    for a, b in itertools.combinations(mem, 2):
        if a['lg'] == b['lg']: continue
        ga, gb = (a['gl'] or ''), (b['gl'] or '')
        if not ga or not gb: continue
        if hand_linked(ga, gb): stats['hand-linked'] += 1; continue
        ok, e, w, m, border = evidence(ga, gb)
        stats['pairs'] += 1
        if ok:
            stats['accepted'] += 1
            accepted.append((sid, s['pfm'], a, b, e, w, m))
        elif border:
            stats['borderline'] += 1
            borderline.append((sid, s['pfm'], a, b, e, w, m))
print(stats)
import pickle
pickle.dump((accepted, borderline, stats), open('accepted.pkl', 'wb'))
