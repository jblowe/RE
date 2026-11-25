# -*- coding: utf-8 -*-
"""Build the merged TGTM MELs: writes TGTM.broad.mel.xml and TGTM.conservative.mel.xml next to this script
(the <project>.<token>.mel.xml convention, so the tokens are 'broad' and 'conservative').

No accent folding anywhere in the output: every gloss is written as the real French / English word.  (fold() below is used
only to decide whether two *candidate* MELs duplicate each other; it never changes a gloss.)

Every <gl> carries
    xml:lang = en | fr | und       und = BCP 47 "undetermined": the string is a word in both languages (place, table, pot ...)
                                   or nothing says which -- see gloss_lang.py
    source   = core | extra        core  = curated by hand (either TGTM hand MEL);  extra = everything added by this script
    layer    = (extras only) why it is there:
                 enriched      glosses of TGTM.enriched2 for a hand MEL           (broad only)
                 extended      MELs of TGTM.hand-extended-v4 the hand MEL lacks   (data-driven)
                 pairs         docs/tgtm-proposals/TGTM.mel-additions.xml          (isolate pairs accepted by pooled evidence)
                 pairs-loose   ... -loose.xml                                       (borderline pairs, broad only)
                 accent        the real, accented spelling of a de-accented French gloss
                 variant       a plural / singular / accent / hyphen variant of a gloss another MEL already has, attached to that MEL
                               (a stray one-gloss MEL such as 'brèdes' joins the MEL that has 'brède'; an unmatched data gloss joins
                               the MEL of its singular).  Only when the target MEL is unique; ambiguous cases are listed, not merged.
                               See variants.py.  The engine is unchanged: the variant is written into the MEL as an exact gloss.
and later layers can add e.g. source="wordnet" / "concepticon".  Nothing here is read by the engine yet except xml:lang.

Layers (each keeps everything below it):
  CORE  union of the two hand MELs: TGTM94SETS/TGTM.hand.mel.xml (accented French) + the TGTM-only glosses of TGTM/TGTM.hand.mel.xml
  E2    TGTM.enriched2 glosses added to the hand MEL with the same id (only when the two share a gloss)
  E4    MELs of hand-extended-v4 not already covered by one MEL
  ADD   57 pair-derived MELs;  ADDL  17 loose ones
Noise removal (extras only, the core is never touched): see junk() and the size cap.
"""
import unicodedata, collections, re, sys, os
from lxml import etree
from nltk.corpus import wordnet as wn
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gloss_lang as GL
import variants as V

R = '/Users/johnlowe/GitHub/RE-Tamangish-Files/'
D = os.path.dirname(os.path.abspath(__file__)) + '/'
L = '{http://www.w3.org/XML/1998/namespace}lang'

def fold(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s.lower().strip()) if unicodedata.category(c) != 'Mn')
def key(s):                      # duplicate test only: accent-, case-, punctuation-insensitive
    return re.sub(r'[^a-z0-9]+', ' ', fold(s)).strip()

def load(path, only=None):
    out = []
    for m in etree.parse(path).getroot().findall('mel'):
        gl = [g.text.strip() for g in m.findall('gl') if g.text and g.text.strip()]      # empty <gl/> skipped
        if gl and (only is None or only(m.get('id'))):
            out.append((m.get('id'), gl, {g.text.strip(): g.get(L) for g in m.findall('gl') if g.text and g.get(L)}))
    return out

H94 = load(R + 'TGTM94SETS/TGTM.hand.mel.xml')
HT = load(R + 'TGTM/TGTM.hand.mel.xml')
ENRICHED = {n: {i: gl for i, gl, _ in load(R + 'TGTM/TGTM.%s.mel.xml' % n)} for n in ('enriched2', 'enriched3')}
E4 = load(R + 'TGTM/TGTM.hand-extended-v4.mel.xml')
ADD = load(D + 'TGTM.mel-additions.xml')
ADDL = load(D + 'TGTM.mel-additions-loose.xml', only=lambda i: i.startswith('q'))
OLDLANG = {}                                                 # tag already present in any source file: one vote for gloss_lang
for src in (H94, HT, E4, ADD, ADDL):
    for _, gl, langs in src:
        for g, l in langs.items():
            if l in ('en', 'fr'): OLDLANG.setdefault(g.lower(), l)

# ---------------------------------------------------------------------------------------------- noise
STOP = GL.EN | GL.FR
GENERIC = {'be', 'become', 'make', 'do', 'have', 'get', 'go', 'take', 'put', 'give', 'cause', 'cause to', 'come', 'use', 'set', 'to',
           'faire', 'être', 'etre', 'avoir', 'mettre', 'prendre', 'aller', 'donner', 'rendre', 'devenir', 'venir', 'se', 'auxiliaire',
           'esp. on colour terms', 'adjective suffix', 'thing', 'chose', 'something', 'quelque chose', 'verb', 'noun', 'suffix',
           'particle', 'also', 'even', 'only', 'same', 'such', 'too', 'etc.', 'etc', 'dat', 'loc', 'loc/dat', 'mare'}
def junk(g):
    k = g.lower().strip()
    toks = GL._WORD.findall(k)
    return (k in GENERIC or len(k) < 2 or not toks or len(k.split()) > 5 or any(c in g for c in '%|$')
            or k.startswith('(') or 'cf.' in k or all(t in STOP for t in toks))

# ---------------------------------------------------------------------------------------------- assemble
class G:                          # one gloss
    __slots__ = ('t', 'source', 'layer', 'lang', 'conf')
    def __init__(s, t, source, layer=None): s.t, s.source, s.layer, s.lang, s.conf = t, source, layer, None, None

def build(layers, cap=None, dead=False, reject=(), variant=True, enriched='enriched2', base='v4', wordnet=True, subsets=True, wn_min=None):
    E2 = ENRICHED[enriched]
    mels = []                                             # [id, [G]]
    byid = {}
    for i, gl, _ in H94:
        m = [i, [G(g, 'core') for g in gl]]; mels.append(m); byid[i] = m
    keys = lambda m: {key(g.t) for g in m[1]}
    # CORE: add what only the TGTM hand MEL has
    for i, gl, _ in HT:
        if i in byid:
            have = keys(byid[i])
            byid[i][1] += [G(g, 'core') for g in gl if key(g) not in have and not have.add(key(g))]
        else:
            k = {key(g) for g in gl}
            best = max(mels, key=lambda m: len(k & keys(m)))
            if len(k & keys(best)) >= min(2, len(k)):
                have = keys(best); best[1] += [G(g, 'core') for g in gl if key(g) not in have]
            else:
                m = [i, [G(g, 'core') for g in gl]]; mels.append(m); byid[i] = m
    if base == 'v4':
        # BASE = hand-extended-v4: every MEL of it, with its own id (m0001 ...).  The hand-union MELs built above say which glosses are
        # core: each hand MEL is claimed by the v4 MEL it shares most glosses with (ties: the same number), the hand glosses are written
        # first as core (so no hand gloss is ever lost, even where v4 split or reworded one), and the other glosses of the v4 MEL are
        # extras (layer 'extended').  A hand MEL no v4 MEL claims is kept under its hand id.  A v4 MEL no hand MEL claims is all extras.
        hand = {m[0]: m for m in mels}
        hk = {i: keys(m) for i, m in hand.items()}
        byk = collections.defaultdict(set)
        for i, k in hk.items():
            for x in k: byk[x].add(i)
        num = lambda i: re.sub(r'\D', '', i).lstrip('0')
        pairs = []
        for vid, gl, _ in E4:
            vk = {key(g) for g in gl}
            c = collections.Counter(h for x in vk for h in byk.get(x, ()))
            for h, o in c.items(): pairs.append((-o, 0 if num(vid) == num(h) else 1, vid, h))
        pairs.sort()
        claim_v, claim_h = {}, {}
        for _, _, vid, h in pairs:
            if vid not in claim_v and h not in claim_h: claim_v[vid] = h; claim_h[h] = vid
        newmels, byid = [], {}
        for vid, gl, _ in E4:
            h = claim_v.get(vid)
            core = [G(g.t, 'core') for g in hand[h][1]] if h else []
            have = {key(g.t) for g in core}
            ext = []
            for g in gl:
                if key(g) in have or junk(g): continue
                have.add(key(g)); ext.append(G(g, 'extra', 'extended'))
            if core or ext:
                m = [vid, core + ext]; newmels.append(m)
                if h: byid[h] = m
        unclaimed = [i for i in hand if i not in claim_h]
        for i in unclaimed: newmels.append(hand[i]); byid[i] = hand[i]
        mels = newmels
        build.rebase = dict(v4_mels=len(E4), hand_claimed=len(claim_h), hand_unclaimed=len(unclaimed))
    def add_mel(mid, gl, layer):
        gl = [g for g in gl if not junk(g)]
        k = {key(g) for g in gl}
        if not gl or any(k <= keys(m) for m in mels): return False
        mels.append([mid, [G(g, 'extra', layer) for g in gl]]); return True
    if 'E2' in layers:
        for i, m in list(byid.items()):
            if i in E2 and keys(m) & {key(g) for g in E2[i]}:
                have = keys(m)
                m[1] += [G(g, 'extra', 'enriched') for g in E2[i] if key(g) not in have and not junk(g) and not have.add(key(g))]
    if 'E4' in layers and base != 'v4':
        n = 0
        for i, gl, _ in E4:
            if add_mel('e%04d' % (n + 1), gl, 'extended'): n += 1
    if 'ADD' in layers:
        for i, gl, _ in ADD: add_mel(i, gl, 'pairs')
    if 'ADDL' in layers:
        for i, gl, _ in ADDL:
            if i not in reject: add_mel(i, gl, 'pairs-loose')
    if base == 'v4':
        # a v4 MEL that has no hand gloss and whose glosses are all in another MEL (typically a hand MEL that the enriched layer has
        # since grown) adds nothing: drop it, as step 3 of the v3 -> v4 maintenance does.  (A tie between two such MELs keeps the first.)
        ks = [keys(m) for m in mels]
        idx = collections.defaultdict(list)
        for n, k in enumerate(ks):
            for x in k: idx[x].append(n)
        drop = set()
        for n, m in enumerate(mels):
            if any(g.source == 'core' for g in m[1]) or not ks[n]: continue
            x = min(ks[n], key=lambda y: len(idx[y]))
            for o in idx[x]:
                if o != n and o not in drop and ks[n] <= ks[o] and (len(ks[o]) > len(ks[n]) or o < n or any(g.source == 'core' for g in mels[o][1])):
                    drop.add(n); break
        build.rebase['subset_mels_dropped'] = len(drop)
        mels = [m for n, m in enumerate(mels) if n not in drop]
    # de-duplicate inside each MEL (core first), language tags, accent restoration
    restored = []
    for m in mels:
        seen, out = set(), []
        for g in m[1]:
            if g.t.lower() in seen or (g.source != 'core' and key(g.t) in seen): continue
            seen.add(g.t.lower()); seen.add(key(g.t)); out.append(g)
        m[1] = out
        extra = []
        for g in m[1]:
            lang, why = GL.lang_of(g.t, OLDLANG.get(g.t.lower()))
            if why == 'no-evidence' and fold(g.t) == g.t:
                acc = GL.accented_forms(g.t.lower())
                if len(acc) == 1:                                # a de-accented French word: write the real one
                    a = next(iter(acc)); lang = 'fr'
                    restored.append((m[0], g.t, a, g.source))
                    if g.source == 'extra': g.t = a              # extras are corrected in place; the hand glosses are kept
                    else: extra.append(G(a, 'extra', 'accent'))  # (and the real spelling added beside them)
            g.lang = lang
        for e in extra:
            if key(e.t) not in {key(x.t) for x in m[1]} or e.t.lower() not in {x.t.lower() for x in m[1]}:
                e.lang = 'fr'; m[1].append(e)
    if dead:                                              # extras no lexicon can ever match
        for m in mels:
            m[1] = [g for g in m[1] if g.source == 'core' or support(g.t) > 0]
        mels = [m for m in mels if m[1]]
    wlog = []
    if wordnet:
        wlog = wordnet_layer(mels, wn_min)
    build.wlog = wlog
    vlog = []
    if variant:
        vlog = variant_layer(mels)
    slog = []
    if subsets:
        slog = subset_merge(mels)
    build.slog = slog
    # size cap: keep the core, then the extras with the most data support
    if cap:
        for m in mels:
            if len(m[1]) > cap:
                core = [g for g in m[1] if g.source == 'core']
                ext = sorted((g for g in m[1] if g.source != 'core'), key=lambda g: -support(g.t))
                m[1] = core + ext[:max(0, cap - len(core))]
    return mels, restored, vlog

sys.path.insert(0, os.path.dirname(os.path.dirname(D.rstrip('/'))) + '/src')
import mel as _mel                      # the engine's own gloss comparison (mel._candidates_lower)
_LEX = {}                                # lexicon -> set of comparison candidates of all its glosses
def _lexicons():
    # every project that may use these MELs: a gloss is dead only if NO lexicon of ANY of them can match it
    for proj in ('TGTM', 'TGTM94SETS', 'DEMO93'):
        for fn in sorted(os.listdir(R + proj)):
            if not fn.endswith('.data.xml'): continue
            c = _LEX.setdefault((proj, fn), set())
            for el in etree.parse(R + proj + '/' + fn).iter('gl'):
                if el.text and el.text.strip(): c |= set(_mel._candidates_lower(el.text.strip()))
_lexicons()
_SUP = {}
def support(g):
    """number of lexicons that have a gloss the engine would match to this MEL gloss (0 = the gloss can never fire)"""
    k = g.lower()
    if k not in _SUP:
        c = set(_mel._candidates_lower(g))
        _SUP[k] = sum(1 for lex in _LEX.values() if c & lex)
    return _SUP[k]


# ---------------------------------------------------------------------------------------------- wordnet layer
WN_K = 1            # a translation counts only when the synset is among the first WN_K senses (same part of speech) of the English word
WN_MAX_TARGETS = 12 # a gloss that would go into more MELs than this is only listed
def _wpos(s): return 'a' if s.pos() == 's' else s.pos()
def _lem(l): return l.replace('_', ' ').lower()
def _verb_fr(w): return len(w) > 3 and bool(re.search(r'(er|ir|oir|re)$', w))
def _first_senses(t, pos=None):
    return wn.synsets(t.replace(' ', '_'), pos=pos)[:WN_K]
def wn_translations(w, lang):
    """{translation: {synset names}} of w (lang 'fr' or 'en') through WordNet / the French WordNet (OMW).
    fr -> en: only synsets of the right part of speech (an infinitive is taken as a verb), only the synset's head lemma, and only when the
    synset is a first sense of that English word, so that the many synonyms and rare senses the French WordNet lists are not used.
    en -> fr: the French lemmas of the first senses of w."""
    out = collections.defaultdict(set)
    if lang == 'fr':
        for sy in wn.synsets(w.replace(' ', '_'), lang='fra'):
            if (sy.pos() == 'v') != _verb_fr(w): continue
            t = sy.lemmas()[0].name()                      # the synset's head lemma only ('fly', not its synonym 'wing')
            if sy in _first_senses(t, _wpos(sy)): out[_lem(t)].add(sy.name())
    else:
        for P in ('v', 'n', 'a', 'r'):
            for sy in _first_senses(w, P):
                for t in sy.lemma_names('fra'): out[_lem(t)].add(sy.name())
    return out
WN_NEAR = 0.25      # WordNet path similarity (1 / (1 + steps between the senses)): 0.33 = siblings (falcon, buzzard: both birds of prey)
def wn_share_sense(a, b):
    """do the English words a and b have a first sense in common, or first senses that are siblings or closer (same part of speech)?"""
    for P in ('v', 'n', 'a', 'r'):
        for x in _first_senses(a, P):
            for y in _first_senses(b, P):
                if x == y or (x.path_similarity(y) or 0) >= WN_NEAR: return True
    return False

# confidence of a WordNet addition.  The engine does not read it (it reads only xml:lang and source): it is for people and later tools.
WN_SHARE = 0.3      # the English sense must be at least this share of the word's SemCor sense counts (all parts of speech)
WN_REL = 0.5        # fr -> en: the translation's SemCor count must be at least this fraction of the strongest translation of the French word
def _lemcount(e, sy):
    n = e.replace(' ', '_').lower()
    return sum(l.count() for l in sy.lemmas() if l.name().lower() == n)
def _sense_share(e, sy):
    tot = sum(_lemcount(e, x) for x in wn.synsets(e.replace(' ', '_')))
    c = _lemcount(e, sy)
    return c, (c / tot if tot else 0.0)
def _wn_related(a, b):
    """two senses are the same, siblings or closer (path similarity), or derivationally related (steal / thief)"""
    if a == b or (a.path_similarity(b) or 0) >= WN_NEAR: return True
    da = {l.synset() for x in a.lemmas() for l in x.derivationally_related_forms()}
    return b in da or any((d.path_similarity(b) or 0) >= WN_NEAR for d in da)

def wordnet_layer(mels, min_conf=None):
    """Translate glosses the lexicons use, French -> English and English -> French, through WordNet, and add each to the MELs that hold its
    translation (source="wordnet").  e.g. 'voler' is added to the MELs with 'steal' (steal.v.01) as well as to the one with 'fly' (fly.v.01).
    Each addition gets confidence="high" or "low":  high = the English sense is a main sense of the English word (>= WN_SHARE of its SemCor
    counts), and for fr -> en also a strong translation of the French word (>= WN_REL of its strongest one) that is not contradicted by the other
    English glosses of the MEL (they are near the sense, or there are none).  Everything else is low; with min_conf='high' the low ones are not added.
    fr -> en: the gloss goes into every MEL that holds an English translation which the lexicons use (support > 0).
    en -> fr: likewise for the French translations, but only if the MEL has no English gloss, or one that shares a sense with the gloss
    (so 'steal' is not put into the MEL of 'fly' / 'voler').  Returns log rows."""
    log = []
    byid = {m[0]: m for m in mels}
    idx = collections.defaultdict(set)                     # normalized piece -> MEL ids
    def pieces(t): return {re.sub(r"^(to|se|s') ?", '', q.lower().strip()).strip() for q in _mel.normalize_gloss_phrases(t)} - {''}
    POSMARK = [(re.compile(r'\((n|noun)\.?\)'), 'n'), (re.compile(r'\((v|vb|verb)\.?\)|^\s*to '), 'v')]   # 'fly (n.)', 'to fly'
    def marked(t):
        for rx, P in POSMARK:
            if rx.search(t): return P
    for i, gl in mels:
        for g in gl:
            for q in pieces(g.t): idx[q].add(i)                         # only the glosses already there: a gloss added below never starts a new link
    marks = {i: {marked(g.t) for g in gl} - {None} for i, gl in mels}      # the MEL says it is about nouns ('fly (n.)') or verbs ('to fly')
    have = {i: {key(g.t) for g in gl} for i, gl in mels}
    src = {}                                               # lookup word -> language
    for d in sorted(data_glosses()):
        for q in pieces(d):
            if junk(q) or q in GENERIC or len(q) < 3 or len(q.split()) > 2 or q in src: continue
            lang = GL.lang_of(q, OLDLANG.get(q))[0]
            if lang in ('fr', 'en'): src[q] = lang
            else: log.append(['skipped-und', q, '', '', '', '', '', ''])
    for w in sorted(src):
        lang = src[w]; other = 'en' if lang == 'fr' else 'fr'
        tr = wn_translations(w, lang)
        tg = collections.defaultdict(list)                 # MEL id -> [translations it holds]
        for t in tr:
            if support(t) == 0 or t in GENERIC or junk(t): continue    # a translation no lexicon uses cannot make a link; nor can 'be', 'être', 'venir', 'faire' ...
            pos = {n.split('.')[1] for n in tr[t]}
            for i in idx.get(t, ()):
                if marks[i] and not (marks[i] & pos) and lang == 'fr': continue          # the 'fly (n.)' MEL is not for the verb voler
                if key(w) not in have[i] and t not in tg[i]: tg[i].append(t)
        ok = {}
        for i, ts in tg.items():
            if lang == 'en':
                en = [g.t for g in byid[i][1] if g.lang == 'en']
                if en and not any(wn_share_sense(w, x) for x in en):
                    log.append(['rejected-other-sense', w, lang + '>' + other, i, ','.join(ts), '', '', ' | '.join(g.t for g in byid[i][1][:8])]); continue
            ok[i] = ts
        if len(ok) > WN_MAX_TARGETS:
            log.append(['too-many-targets', w, lang + '>' + other, ','.join(sorted(ok)[:6]), str(len(ok)), '', '', '']); continue
        # strength of each French -> English translation among all of w's translations (SemCor count of the best synset)
        cnt = {t: max([_sense_share(t, wn.synset(n))[0] for n in tr[t]] + [0]) for t in tr} if lang == 'fr' else {}
        top = max(cnt.values()) if cnt else 0
        for i, ts in sorted(ok.items()):
            best_share, best_rel, coherent = 0.0, 0.0, True
            for t in ts:
                for n in tr[t]:
                    c, sh = _sense_share(t if lang == 'fr' else w, wn.synset(n))
                    if sh > best_share: best_share = sh
                    if lang == 'fr' and top and c / top > best_rel: best_rel = c / top
            if lang == 'fr':
                others = [g.t for g in byid[i][1] if g.lang == 'en' and g.source != 'wordnet' and not (pieces(g.t) & set(ts)) and len(g.t.split()) <= 2]
                if others:
                    sy = [wn.synset(n) for t in ts for n in tr[t]]
                    coherent = any(_wn_related(sx, y) for x in others for sx in wn.synsets(x.replace(' ', '_'))[:3] for y in sy)
            high = best_share >= WN_SHARE and (lang == 'en' or (best_rel >= WN_REL and coherent))
            if min_conf == 'high' and not high:
                log.append(['not-added-low-confidence', w, lang + '>' + other, i, ','.join(ts), '', 'low', ' | '.join(x.t for x in byid[i][1][:8])]); continue
            g = G(w, 'wordnet', 'wordnet'); g.lang = lang; g.conf = 'high' if high else 'low'
            byid[i][1].append(g); have[i].add(key(w))
            log.append(['added', w, lang + '>' + other, i, ','.join(ts), ','.join(sorted({y for t in ts for y in tr[t]})[:4]), g.conf, ' | '.join(x.t for x in byid[i][1][:8])])
    return log


# ---------------------------------------------------------------------------------------------- subset merge (last step)
POSMARK = [(re.compile(r'\((n|noun)\.?\)'), 'n'), (re.compile(r'\((v|vb|verb)\.?\)|^\s*to '), 'v')]     # 'fly (n.)', 'fly (v.)', 'to fly'
def pos_marks(t): return {P for rx, P in POSMARK if rx.search(t)}
def gloss_candidates(t):
    """the comparison strings the engine derives from a MEL gloss: mel.normalize_gloss(), lowercased (the raw string is added to the target
    by the merge, so it is not part of the comparison)"""
    return frozenset(c.lower() for c in _mel.normalize_gloss(t)) or frozenset([t.lower()])

def subset_merge(mels):
    """The last step.  A MEL whose normalized glosses (mel.normalize_gloss) are all among the normalized glosses of another MEL
    adds nothing for the engine: everything it matches, the larger MEL matches.  It is merged into that MEL (its glosses are appended to the target,
    so 'fly (v.)' and 'to fly' appear in the MEL of 'fly', 'voler') and removed.
      - the target is the single largest MEL that contains it; with two or more unrelated ones the MEL is left alone and listed (ambiguous);
      - a MEL that says it is about nouns ('fly (n.)') is not merged into one that does not say so, and a verb-marked one ('fly (v.)', 'to fly') never
        into a noun-marked one: a subset is not necessarily the same sense;
      - a MEL with hand (core) glosses may be merged away too, as long as it goes into a larger MEL; its glosses keep source="core".
    Repeats until nothing more merges (a merge can make a MEL a subset of another).  Returns log rows [kind, mel, target(s), mel glosses, target glosses]."""
    log = []
    for _round in range(5):
        N = [frozenset().union(*[gloss_candidates(g.t) for g in m[1]]) for m in mels]
        P = [set().union(*[pos_marks(g.t) for g in m[1]]) for m in mels]
        idx = collections.defaultdict(list)
        for n, k in enumerate(N):
            for x in k: idx[x].append(n)
        plan = {}
        for n, m in enumerate(mels):
            if not N[n]: continue
            rare = min(N[n], key=lambda y: len(idx[y]))
            cand = []
            for o in idx[rare]:
                if o == n or not N[n] <= N[o]: continue
                if len(N[o]) == len(N[n]) and o > n: continue                        # identical candidates: the earlier MEL is the target
                if P[n] and not (P[n] <= P[o] or ('v' in P[n] and 'n' not in P[o] and not P[o])): continue
                cand.append(o)
            if not cand: continue
            top = [o for o in cand if not any(o != q and N[o] < N[q] for q in cand)]
            plan[n] = top
        merged = {}
        for n, top in plan.items():
            if len(top) == 1: merged[n] = top[0]
            elif _round == 0:
                log.append(['ambiguous', mels[n][0], ','.join(mels[o][0] for o in top[:6]), ' | '.join(g.t for g in mels[n][1][:6]),
                            ' // '.join('%s: %s' % (mels[o][0], ' | '.join(g.t for g in mels[o][1][:5])) for o in top[:3])])
        if not merged: break
        # a MEL merged into a MEL that is itself being merged away waits for the next round
        merged = {n: t for n, t in merged.items() if t not in merged}
        for n, t in merged.items():
            have = {g.t.lower(): g for g in mels[t][1]}
            for g in mels[n][1]:
                if g.t.lower() not in have: mels[t][1].append(g); have[g.t.lower()] = g
                elif g.source == 'core' and have[g.t.lower()].source != 'core':         # a hand gloss keeps its tag when the target had it as an extra
                    h = have[g.t.lower()]; h.source, h.layer, h.conf = 'core', None, None
            log.append(['merged-hand' if any(g.source == 'core' for g in mels[n][1]) else 'merged', mels[n][0], mels[t][0], ' | '.join(g.t for g in mels[n][1][:6]), ' | '.join(g.t for g in mels[t][1][:6])])
        mels[:] = [m for n, m in enumerate(mels) if n not in merged]
    return log

# ---------------------------------------------------------------------------------------------- variant layer
def data_glosses():
    """distinct glosses of every lexicon of TGTM, TGTM94SETS and DEMO93, as the engine reads them (ngl, else gl)"""
    out = set()
    for proj in ('TGTM', 'TGTM94SETS', 'DEMO93'):
        for fn in sorted(os.listdir(R + proj)):
            if not fn.endswith('.data.xml'): continue
            for e in etree.parse(R + proj + '/' + fn).getroot().iter('entry'):
                n = e.find('ngl'); g = n if n is not None and n.text and n.text.strip() else e.find('gl')
                if g is not None and g.text and g.text.strip(): out.add(g.text.strip())
    return out

def in_french_dictionary(w):
    """a French word in WordNet-fra (the dictionary only: a spelling that merely occurs in a lexicon, like 'aïl', does not count)"""
    return bool(GL.wn.synsets(w.lower().replace(' ', '_'), lang='fra'))

def variant_layer(mels):
    """Attach stray glosses to the one MEL that already has their plural / singular / accent / hyphen variant.
    (a) a non-core MEL with a single gloss that another MEL already has verbatim is dropped (subsumed); one that another MEL has only
    as a variant is merged into that MEL;  (b) a data gloss no MEL matches is added to the MEL of its variant.
    Returns the log rows [kind, gloss, from_mel, target_mel, matched_gloss, target_glosses]."""
    log = []
    byid = {m[0]: m for m in mels}
    idxf = collections.defaultdict(set); idxa = collections.defaultdict(set); idxc = collections.defaultdict(set)    # folded / accented / compact key -> MEL ids
    def index(g, i):
        idxf[V.key(g)].add(i); idxa[V.key_a(g)].add(i); idxc[V.compact(V.key(g))].add(i)
    def unindex(g, i):
        idxf[V.key(g)].discard(i); idxa[V.key_a(g)].discard(i); idxc[V.compact(V.key(g))].discard(i)
    for i, gl in mels:
        for g in gl: index(g.t, i)
    def targets(text, own):
        """MEL id -> glosses there that `text` is a spelling or number variant of"""
        t = collections.defaultdict(list)
        for i in idxf.get(V.key(text), ()):                       # same letters up to case / accents / punctuation
            if i == own: continue
            for g in byid[i][1]:
                if V.key(g.t) != V.key(text): continue
                if (V.key_a(g.t) != V.key_a(text) and in_french_dictionary(g.t) and in_french_dictionary(text)):
                    continue                                      # two real French words that differ only by an accent (fatigue / fatigué)
                t[i].append(g.t)
        for i in idxc.get(V.compact(V.key(text)), ()):            # grand-mother ~ grandmother
            if i != own and i not in t and len(V.key(text).split()) <= 3:
                t[i] += [g.t for g in byid[i][1] if V.compact(V.key(g.t)) == V.compact(V.key(text)) and V.key(g.t) != V.key(text)]    # a real spacing difference
            if i in t and not t[i]: del t[i]
        for k in V.plural_keys(text):                             # plural <-> singular, accents kept
            for i in idxa.get(k, ()):
                if i != own and i not in t: t[i] += [g.t for g in byid[i][1] if V.key_a(g.t) == k]
        return t
    def desc(i): return ' | '.join(g.t for g in byid[i][1][:10])
    # (a) stray one-gloss extras
    for m in list(mels):
        if len(m[1]) != 1 or m[1][0].source == 'core': continue
        g = m[1][0]
        t = targets(g.t, m[0])
        same = [i for i, ms in t.items() if g.t.lower() in {x.lower() for x in ms}]    # the very same gloss is already in another MEL
        if same:                                          # nothing to add: the singleton duplicates a gloss of a larger MEL
            unindex(g.t, m[0]); m[1] = []
            log.append(['subsumed-singleton', g.t, m[0], ','.join(sorted(same)[:6]), g.t, desc(sorted(same)[0])])
            continue
        if len(t) == 1:
            tid, matched = next(iter(t.items()))
            g.layer = 'variant'
            byid[tid][1].append(g); m[1] = []
            unindex(g.t, m[0]); index(g.t, tid)
            log.append(['merged-singleton', g.t, m[0], tid, matched[0], desc(tid)])
        elif t:
            log.append(['ambiguous-singleton', g.t, m[0], ','.join(sorted(t)), '', ' // '.join('%s: %s' % (i, desc(i)) for i in sorted(t)[:4])])
    mels[:] = [m for m in mels if m[1]]
    # (b) data glosses that match no MEL at all
    cand = set()
    for _, gl in mels:
        for g in gl: cand |= set(_mel._candidates_lower(g.t))
    for d in sorted(data_glosses()):
        C = set(_mel._candidates_lower(d))
        if C & cand: continue
        for c in sorted(C):
            if junk(c) or c in GENERIC: continue
            t = targets(c, None)
            text = d if d.lower() == c else c
            if len(t) == 1:
                tid, matched = next(iter(t.items()))
                gg = G(text, 'extra', 'variant'); gg.lang = GL.lang_of(text, OLDLANG.get(text.lower()))[0]
                byid[tid][1].append(gg); index(text, tid); cand |= set(_mel._candidates_lower(text))
                log.append(['attached-data-gloss', text, '', tid, matched[0], desc(tid)])
                break
            elif t:
                log.append(['ambiguous-data-gloss', text, '', ','.join(sorted(t)), '', ' // '.join('%s: %s' % (i, desc(i)) for i in sorted(t)[:4])])
    return log

def sort_key(t):
    """alphabetical order for output only: case, accents and leading punctuation (the '*' of keyterms, '(' ...) are ignored; the gloss is not changed"""
    return (re.sub(r'^[^a-z0-9]+', '', fold(t)), t)

def final_ids(mels):
    """ids padded to four digits ('m0001', 'p0001', 'q0007').  A padded id that another MEL already has (the hand MEL 'm675' no v4 MEL claimed
    against v4's 'm0675') gets the next free number of its prefix.  Returns {old id: new id} for the ids that change."""
    pat = re.compile(r'^([A-Za-z]+)(\d+)$')
    used = {i for i, _ in mels if pat.match(i) and len(pat.match(i).group(2)) >= 4}
    top = collections.defaultdict(int)
    for i in used: top[pat.match(i).group(1)] = max(top[pat.match(i).group(1)], int(pat.match(i).group(2)))
    change = {}
    for i, _ in mels:
        m = pat.match(i)
        if not m or len(m.group(2)) >= 4: continue
        new = m.group(1) + m.group(2).zfill(4)
        if new in used:
            top[m.group(1)] += 1; new = m.group(1) + str(top[m.group(1)]).zfill(4)
        used.add(new); change[i] = new
    return change

def write(mels, tok):
    change = final_ids(mels)
    root = etree.Element('semantics')
    out = []
    for i, gl in mels:
        gl = sorted(gl, key=lambda g: sort_key(g.t))
        out.append((change.get(i, i), gl))
    out.sort(key=lambda x: (sort_key(x[1][0].t), x[0]))                     # MELs in alphabetical order of their first gloss
    for i, gl in out:
        m = etree.SubElement(root, 'mel', id=i)
        for g in gl:
            e = etree.SubElement(m, 'gl'); e.text = g.t
            e.set(L, g.lang); e.set('source', g.source)
            if g.layer: e.set('layer', g.layer)
            if g.conf: e.set('confidence', g.conf)
    open(D + 'TGTM.%s.mel.xml' % tok, 'wb').write(etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True))
    with open(D + 'mel-id-changes-%s.tsv' % tok, 'w', encoding='utf-8') as f:
        f.write('old_id\tnew_id\n')
        for o, n in change.items(): f.write('%s\t%s\n' % (o, n))
    n = sum(len(gl) for _, gl in mels)
    return len(mels), n

CANDS = {'broad': dict(layers=('E2', 'ADD', 'ADDL'), dead=True),            # base hand-extended-v4 + enriched glosses + the loose pairs (tagged pairs-loose)
         'conservative': dict(layers=('ADD',), dead=True)}                  # base hand-extended-v4 + pairs
CANDS_EXP = {'broad-e3': dict(layers=('E2', 'ADD', 'ADDL'), dead=True, enriched='enriched3'),                 # experiment: python make_merged_mels.py broad-e3
             'broad-hand': dict(layers=('E2', 'E4', 'ADD', 'ADDL'), dead=True, base='hand', wordnet=False),                  # the first design: the hand MELs as base, v4 as a layer
             'conservative-hand': dict(layers=('E4', 'ADD'), dead=True, base='hand', wordnet=False),
             'broad-nosub': dict(layers=('E2', 'ADD', 'ADDL'), dead=True, subsets=False),                     # without the last (subset merge) step
             'conservative-nosub': dict(layers=('ADD',), dead=True, subsets=False),
             'broad-wnhigh': dict(layers=('E2', 'ADD', 'ADDL'), dead=True, wn_min='high'),                    # WordNet layer with only the high-confidence glosses
             'conservative-wnhigh': dict(layers=('ADD',), dead=True, wn_min='high'),
             'broad-nown': dict(layers=('E2', 'ADD', 'ADDL'), dead=True, wordnet=False, subsets=False),                      # the same without the wordnet layer, for comparison
             'conservative-nown': dict(layers=('ADD',), dead=True, wordnet=False, subsets=False)}
if __name__ == '__main__':
    CANDS.update({t: CANDS_EXP[t] for t in sys.argv[1:] if t in CANDS_EXP})
    for tok, kw in ([(t, CANDS[t]) for t in sys.argv[1:] if t in CANDS] or CANDS.items()):
        mels, restored, vlog = build(**kw)
        wlog = build.wlog; slog = build.slog
        n, g = write(mels, tok)
        c = collections.Counter((x.source, x.lang) for _, gl in mels for x in gl)
        with open(D + 'mel-accent-restorations-%s.tsv' % tok, 'w', encoding='utf-8') as f:
            f.write('mel_id\tgloss_found\tspelling_added_or_used\tgloss_source\n')
            for r in restored: f.write('\t'.join(r) + '\n')
        with open(D + 'mel-variant-merges-%s.tsv' % tok, 'w', encoding='utf-8') as f:
            f.write('kind\tgloss\tfrom_mel\ttarget_mel(s)\tvariant_of\ttarget_glosses\n')
            for r in vlog: f.write('\t'.join(r) + '\n')
        with open(D + 'mel-wordnet-additions-%s.tsv' % tok, 'w', encoding='utf-8') as f:
            f.write('kind\tgloss\tdirection\ttarget_mel\ttranslation(s)\tsynset(s)\tconfidence\ttarget_glosses\n')
            for r in wlog: f.write('\t'.join(r) + '\n')
        with open(D + 'mel-subset-merges-%s.tsv' % tok, 'w', encoding='utf-8') as f:
            f.write('kind\tmel\ttarget_mel(s)\tmel_glosses\ttarget_glosses\n')
            for r in slog: f.write('\t'.join(r) + '\n')
        print(tok, 'subset-merge', collections.Counter(r[0] for r in slog))
        print(tok, 'wordnet', collections.Counter(r[0] for r in wlog))
        print(tok, getattr(build, 'rebase', None), collections.Counter(r[0] for r in vlog))
        print(tok, kw, n, 'MELs', g, 'glosses', 'avg %.2f' % (g / n), dict(c), 'restored', len(restored))
