"""REwww/diff_common.py – helpers shared by the per-type differs (diff_*.py).

A differ takes the old and new root elements of an XML file and returns a copy
of the new tree annotated with attributes that a stylesheet renders:

    diff="added"     the element is new
    diff="deleted"   the element was in the old version only (a copy of it is
                     placed at its old position)
    diff="changed"   the element is in both versions but differs

and, on a row element, one set per changed field:

    diff_<field>="changed"   old_<field>="<old value>"   [norm_<field>="1"]

For list items (a <seg>, <from>, <gl>, ...): old="<old value>" [norm="1"].
norm marks a change that is only a Unicode normalization difference (NFC vs
NFD), which looks identical on screen.

Records are matched by key, not position (see pair()), so renumbering or
inserting a record does not make everything after it look changed.
"""

import copy
import difflib
import unicodedata
from collections import Counter, defaultdict

KINDS = ('added', 'deleted', 'changed')


# ── small helpers ─────────────────────────────────────────────────────────────

def text(el):
    """All the text of el (including inside child elements, e.g. a headword
    with a <suffix>), stripped; '' for a missing element."""
    return ''.join(el.itertext()).strip() if el is not None else ''


def attr(el, name):
    return (el.get(name) or '') if el is not None else ''


def nfc(s):
    return unicodedata.normalize('NFC', s)


def find(root, tag):
    """root itself if it is <tag>, else its first <tag> descendant, else None."""
    if root.tag == tag:
        return root
    return root.find('.//' + tag)


def mark_subtree(el, kind, tags=()):
    """Mark el, and the descendants named in tags, with kind."""
    el.set('diff', kind)
    if tags:
        for sub in el.iter(*tags):
            sub.set('diff', kind)


def has_diff(el):
    """True if el or anything inside it carries a diff annotation."""
    for e in el.iter():
        if any(k == 'diff' or k.startswith('diff_') for k in e.attrib):
            return True
    return False


def new_count(sections):
    return {s: defaultdict(int) for s in sections}


def summarize(count, sections):
    """{section: {added, deleted, changed}} from a new_count() tally."""
    return {s: {k: count[s][k] for k in KINDS} for s in sections}


# ── matching ──────────────────────────────────────────────────────────────────

class Overlap:
    """A pairing rule: match items that share members, best Jaccard overlap
    first, provided it is at least min_ratio. items(el) -> iterable of hashables."""
    def __init__(self, items, min_ratio=0.5):
        self.items = items
        self.min_ratio = min_ratio


def pair(olds, news, *rules):
    """Match old items to new items.

    Each rule is tried in order on whatever is still unmatched. A rule is
      - a function key(el) -> hashable (None never matches); items with the same
        key pair up in document order;
      - (key, guard): as above, but an old item only pairs if guard(old, new);
      - an Overlap.

    Returns ({new index: old index}, [indexes of unmatched old items])."""
    new_to_old = {}
    used = set()
    for rule in rules:
        if isinstance(rule, Overlap):
            _pair_overlap(olds, news, rule, new_to_old, used)
            continue
        key, guard = rule if isinstance(rule, tuple) else (rule, None)
        buckets = defaultdict(list)
        for i, o in enumerate(olds):
            if i not in used:
                k = key(o)
                if k is not None:
                    buckets[k].append(i)
        for j, n in enumerate(news):
            if j in new_to_old:
                continue
            k = key(n)
            if k is None:
                continue
            cands = buckets.get(k) or []
            for pos, i in enumerate(cands):
                if guard is None or guard(olds[i], n):
                    new_to_old[j] = i
                    used.add(i)
                    del cands[pos]
                    break
    return new_to_old, [i for i in range(len(olds)) if i not in used]


def _pair_overlap(olds, news, rule, new_to_old, used):
    index = defaultdict(list)
    old_items = {}
    for i, o in enumerate(olds):
        if i in used:
            continue
        items = set(rule.items(o))
        old_items[i] = items
        for it in items:
            index[it].append(i)
    for j, n in enumerate(news):
        if j in new_to_old:
            continue
        items = set(rule.items(n))
        votes = Counter()
        for it in items:
            for i in index.get(it, ()):
                if i not in used:
                    votes[i] += 1
        best, best_ratio = None, 0.0
        for i, shared in votes.items():
            ratio = shared / len(items | old_items[i])
            if ratio > best_ratio or (ratio == best_ratio and best is not None and i < best):
                best, best_ratio = i, ratio
        if best is not None and best_ratio >= rule.min_ratio:
            new_to_old[j] = best
            used.add(best)


def insert_deleted(parent, olds, news, new_to_old, deleted):
    """Put copies of the deleted old items into parent, each after the new item
    matched to its nearest preceding surviving old item (or before the first new
    item when there is none). Returns the copies, in order."""
    old_to_new = {i: j for j, i in new_to_old.items()}
    copies = []
    last_after = {}                      # anchor element -> last copy placed after it
    for i in deleted:
        anchor = None
        for k in range(i - 1, -1, -1):
            if k in old_to_new:
                anchor = news[old_to_new[k]]
                break
        c = copy.deepcopy(olds[i])
        c.tail = None
        if anchor is not None:
            ref = last_after.get(anchor, anchor)
            parent.insert(parent.index(ref) + 1, c)
            last_after[anchor] = c
        elif news:
            ref = last_after.get(None)
            pos = parent.index(ref) + 1 if ref is not None else parent.index(news[0])
            parent.insert(pos, c)
            last_after[None] = c
        else:
            parent.append(c)
        copies.append(c)
    return copies


# ── diffing ───────────────────────────────────────────────────────────────────

def compare_fields(old, new, fields):
    """Mark the fields (name -> function(element) -> str) that differ."""
    for name, fn in fields.items():
        a, b = fn(old), fn(new)
        if a != b:
            new.set('diff_' + name, 'changed')
            new.set('old_' + name, a)
            if nfc(a) == nfc(b):
                new.set('norm_' + name, '1')


def diff_records(old_parent, new_parent, tag, rules, fields, count, section,
                 on_match=None, subtree_tags=()):
    """Diff the <tag> children of two parents, matched by rules (see pair()),
    marking added / deleted / changed. on_match(old, new) is called for each
    matched pair first (to diff what is inside). Deleted records are copied
    into new_parent at their old position."""
    olds = old_parent.findall(tag) if old_parent is not None else []
    news = new_parent.findall(tag)
    new_to_old, deleted = pair(olds, news, *rules)
    for j, n in enumerate(news):
        if j not in new_to_old:
            mark_subtree(n, 'added', subtree_tags)
            count[section]['added'] += 1
            continue
        o = olds[new_to_old[j]]
        compare_fields(o, n, fields)
        if on_match:
            on_match(o, n)
        if has_diff(n):
            n.set('diff', 'changed')
            count[section]['changed'] += 1
    for c in insert_deleted(new_parent, olds, news, new_to_old, deleted):
        mark_subtree(c, 'deleted', subtree_tags)
        count[section]['deleted'] += 1
    return news


def diff_list(old_parent, new_parent, tag, sig, shown, count, section):
    """Diff the ordered <tag> children of two matched parents (the <seg>s of a
    cell, the <from>s of a fuzzy item, the <gl>s of a MEL, ...).

    sig(el) -> hashable decides whether two items are equal; shown(el) -> str
    is what a changed item's old value is displayed as. Marks the parent
    diff="changed" when anything inside differs."""
    olds = old_parent.findall(tag)
    news = new_parent.findall(tag)
    sm = difflib.SequenceMatcher(None, [sig(s) for s in olds],
                                 [sig(s) for s in news], autojunk=False)
    after_last = [0]

    def place(seg, before_index):
        """Insert a deleted copy before news[before_index], or at the end."""
        c = copy.deepcopy(seg)
        c.tail = None
        c.set('diff', 'deleted')
        if before_index < len(news):
            new_parent.insert(new_parent.index(news[before_index]), c)
        elif news:
            new_parent.insert(new_parent.index(news[-1]) + 1 + after_last[0], c)
            after_last[0] += 1
        else:
            new_parent.append(c)
        count[section]['deleted'] += 1

    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'equal':
            continue
        if op == 'delete':
            for i in range(i1, i2):
                place(olds[i], j1)
            continue
        paired = min(i2 - i1, j2 - j1) if op == 'replace' else 0
        for k in range(paired):
            o, n = olds[i1 + k], news[j1 + k]
            n.set('diff', 'changed')
            n.set('old', shown(o))
            if nfc(text(o)) == nfc(text(n)) and text(o) != text(n):
                n.set('norm', '1')
            count[section]['changed'] += 1
        for j in range(j1 + paired, j2):
            news[j].set('diff', 'added')
            count[section]['added'] += 1
        for i in range(i1 + paired, i2):
            place(olds[i], j2)
    if any(s.get('diff') for s in new_parent.findall(tag)):
        new_parent.set('diff', 'changed')
