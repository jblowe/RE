"""REwww/diff_mel.py – annotate a MEL file (<semantics><mel id><gl>…</gl></mel>)
with its differences. Rendered by mel2html.xsl.

MELs are matched by their exact set of glosses (so a renumbered MEL is not a
change), then by shared glosses, then by id. Ids are often regenerated, so they
are the last resort. Summary statistics (<totals>) are compared too.
"""

import copy

from diff_common import (Overlap, attr, diff_list, diff_records, find,
                         new_count, summarize, text)

SECTIONS = ('mel', 'gl', 'stat')
_XML_LANG = '{http://www.w3.org/XML/1998/namespace}lang'
_SUB = ('gl',)


def _gl_sig(g):
    return (text(g), attr(g, 'pivot'), attr(g, 'singleton'), attr(g, _XML_LANG))


def _gl_shown(g):
    return text(g) + ''.join(f' [{a}]' for a in ('pivot', 'singleton') if g.get(a))


def _glosses(m):
    return [text(g) for g in m.findall('gl')]


def _diff_totals(old_root, new, count):
    old_t, new_t = find(old_root, 'totals'), find(new, 'totals')
    if new_t is None:
        return
    for c in new_t:
        o = old_t.find(c.tag) if old_t is not None else None
        if o is None:
            c.set('diff', 'added')
            count['stat']['added'] += 1
        elif attr(o, 'value') != attr(c, 'value'):
            c.set('diff', 'changed')
            c.set('diff_value', 'changed')
            c.set('old_value', attr(o, 'value'))
            count['stat']['changed'] += 1
    if old_t is not None:
        for o in old_t:
            if new_t.find(o.tag) is None:
                d = copy.deepcopy(o)
                d.set('diff', 'deleted')
                new_t.append(d)
                count['stat']['deleted'] += 1


def annotate(old_root, new_root):
    new = copy.deepcopy(new_root)
    count = new_count(SECTIONS)
    for tag in ('semantics', 'unmatched'):
        old_c, new_c = find(old_root, tag), find(new, tag)
        if new_c is None:
            continue
        diff_records(
            old_c, new_c, 'mel',
            [lambda m: tuple(sorted(_glosses(m))) or None,
             Overlap(_glosses, 0.3),
             lambda m: attr(m, 'id') or None],
            {}, count, 'mel',     # ids are regenerated: a new id alone is not a change
            on_match=lambda o, n: diff_list(o, n, 'gl', _gl_sig, _gl_shown,
                                            count, 'gl'),
            subtree_tags=_SUB)
    _diff_totals(old_root, new, count)
    return new, summarize(count, SECTIONS)
