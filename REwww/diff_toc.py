"""REwww/diff_toc.py – annotate a table of correspondences with its differences.

annotate(old_root, new_root) returns (a copy of new_root annotated as described
in diff_common.py, a summary of counts). Rendered by toc2html-view.xsl.

The annotated tree also gets a <diff_dialects> element listing every dialect in
the old or new version, so the table has a column for each.

<corr>s are matched by content (proto form + syllable position + contexts), then
by number, so renumbering or inserting a correspondence does not make everything
after it look changed. The number, and the other fields, are marked when they
differ (diff_num / old_num, ...).
"""

import copy

import lxml.etree as ET

from diff_common import (attr, diff_list, diff_records, insert_deleted,
                         mark_subtree, new_count, pair, summarize, text)

SECTIONS = ('corr', 'seg', 'class', 'control', 'rule', 'quirk')
_SUB = ('modern', 'seg')            # marked along with an added / deleted <corr>


# ── <corr> ────────────────────────────────────────────────────────────────────

_CORR_FIELDS = {
    'num':      lambda c: attr(c, 'num'),
    'proto':    lambda c: text(c.find('proto')),
    'syll':     lambda c: attr(c.find('proto'), 'syll'),
    'contextL': lambda c: attr(c.find('proto'), 'contextL'),
    'contextR': lambda c: attr(c.find('proto'), 'contextR'),
}


def _corr_key(c):
    p = c.find('proto')
    return (text(p), attr(p, 'syll'), attr(p, 'contextL'), attr(p, 'contextR'))


def _seg_sig(s):
    return (text(s), attr(s, 'statut'))


def _seg_shown(s):
    """A seg as the table shows it (a doubtful one is prefixed with =)."""
    t, st = _seg_sig(s)
    return ('=' if st == 'doute' else '') + t


def _diff_corr_moderns(old_c, new_c, count):
    olds = old_c.findall('modern')
    news = new_c.findall('modern')
    new_to_old, deleted = pair(olds, news, lambda m: m.get('dialecte'))
    for j, n in enumerate(news):
        if j not in new_to_old:
            mark_subtree(n, 'added', _SUB)
        else:
            diff_list(olds[new_to_old[j]], n, 'seg', _seg_sig, _seg_shown,
                      count, 'seg')
    for c in insert_deleted(new_c, olds, news, new_to_old, deleted):
        mark_subtree(c, 'deleted', _SUB)


# ── parameters (controls, classes) ────────────────────────────────────────────

CONTROL_TAGS = ('canon', 'spec', 'context_match_type')


def _diff_parameters(old_p, new_p, count):
    value = {'value': lambda e: attr(e, 'value')}
    diff_records(old_p, new_p, 'class', [lambda e: e.get('name')], value,
                 count, 'class')
    for tag in CONTROL_TAGS:
        diff_records(old_p, new_p, tag, [lambda e: ''], value, count, 'control')


# ── rules and quirks ──────────────────────────────────────────────────────────

_RULE_FIELDS = {
    'num':       lambda r: attr(r, 'num'),
    'input':     lambda r: text(r.find('input')),
    'outcome':   lambda r: text(r.find('outcome')),
    'contextL':  lambda r: attr(r.find('input'), 'contextL'),
    'contextR':  lambda r: attr(r.find('input'), 'contextR'),
    'stage':     lambda r: attr(r, 'stage'),
    'languages': lambda r: attr(r.find('outcome'), 'languages'),
}


def _rule_key(r):
    return tuple(_RULE_FIELDS[k](r) for k in
                 ('input', 'outcome', 'contextL', 'contextR', 'languages'))


def _analysis(q):
    slot, val = text(q.find('analysis_slot')), text(q.find('analysis_value'))
    return slot + ('=' + val if val else '')


_QUIRK_FIELDS = {
    'id':          lambda q: attr(q, 'id'),
    'source_id':   lambda q: text(q.find('source_id')),
    'lg':          lambda q: text(q.find('lg')),
    'lx':          lambda q: text(q.find('lx')),
    'gl':          lambda q: text(q.find('gl')),
    'alternative': lambda q: text(q.find('alternative')),
    'analysis':    _analysis,
    'notes':       lambda q: '; '.join(text(n) for n in q.findall('note')),
}


def _quirk_key(q):
    return tuple(_QUIRK_FIELDS[k](q) for k in ('lg', 'lx', 'gl', 'alternative'))


# ── entry point ───────────────────────────────────────────────────────────────

def _dialects(root):
    seen = []
    for m in root.iter('modern'):
        d = m.get('dialecte')
        if d and d not in seen:
            seen.append(d)
    return seen


def annotate(old_root, new_root):
    new = copy.deepcopy(new_root)
    count = new_count(SECTIONS)

    old_p, new_p = old_root.find('parameters'), new.find('parameters')
    if new_p is None and old_p is not None:
        new_p = ET.SubElement(new, 'parameters')
    if new_p is not None:
        _diff_parameters(old_p, new_p, count)

    diff_records(old_root, new, 'corr',
                 [_corr_key, lambda c: attr(c, 'num') or None],
                 _CORR_FIELDS, count, 'corr',
                 on_match=lambda o, n: _diff_corr_moderns(o, n, count),
                 subtree_tags=_SUB)
    diff_records(old_root, new, 'rule',
                 [_rule_key, lambda r: attr(r, 'num') or None],
                 _RULE_FIELDS, count, 'rule')
    diff_records(old_root, new, 'quirk',
                 [_quirk_key, lambda q: attr(q, 'id') or None],
                 _QUIRK_FIELDS, count, 'quirk')

    cols = ET.Element('diff_dialects')
    for d in _dialects(new):
        ET.SubElement(cols, 'd').set('dialecte', d)
    new.insert(0, cols)
    return new, summarize(count, SECTIONS)
