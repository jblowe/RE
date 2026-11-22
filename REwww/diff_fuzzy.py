"""REwww/diff_fuzzy.py – annotate a fuzzy-rules file (<fuzzy><item dial to>
<from>…</from></item>) with its differences. Rendered by fuzzy2html.xsl.

Items are matched by (dialect, `to` value), then by (dialect, set of `from`
values), so an item whose `to` was edited shows as changed, not deleted + added.
"""

import copy

from diff_common import (attr, diff_list, diff_records, find, new_count,
                         summarize, text)

SECTIONS = ('item', 'from')

_FIELDS = {'dial': lambda i: attr(i, 'dial'), 'to': lambda i: attr(i, 'to')}


def _froms(item):
    return tuple(sorted(text(f) for f in item.findall('from')))


def annotate(old_root, new_root):
    new = copy.deepcopy(new_root)
    count = new_count(SECTIONS)
    old_parent, new_parent = find(old_root, 'fuzzy'), find(new, 'fuzzy')
    if new_parent is not None:
        diff_records(
            old_parent, new_parent, 'item',
            [lambda i: (attr(i, 'dial'), attr(i, 'to')),
             lambda i: (attr(i, 'dial'), _froms(i))],
            _FIELDS, count, 'item',
            on_match=lambda o, n: diff_list(o, n, 'from', text, text, count, 'from'),
            subtree_tags=('from',))
    return new, summarize(count, SECTIONS)
