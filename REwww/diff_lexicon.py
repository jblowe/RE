"""REwww/diff_lexicon.py – annotate a lexicon (<lexicon><entry id><hw/><gl/>
<ngl/></entry>) with its differences. Rendered by lexicon2table.xsl.

Entries are matched by (headword, glosses), then by headword alone (glosses
edited), then by id when the headword is similar. Ids are sequential, so
deleting an entry renumbers the rest: an id change alone is not a difference.
"""

import copy
import difflib

from diff_common import attr, diff_records, find, new_count, summarize, text

SECTIONS = ('entry',)


def _join(tag):
    return lambda e: '; '.join(text(x) for x in e.findall(tag))


_FIELDS = {'hw': lambda e: text(e.find('hw')), 'gl': _join('gl'), 'ngl': _join('ngl')}


def _similar(old, new):
    a, b = text(old.find('hw')), text(new.find('hw'))
    if difflib.SequenceMatcher(None, a, b).ratio() >= 0.5:
        return True
    return bool({text(g) for g in old.findall('gl')} & {text(g) for g in new.findall('gl')})


def annotate(old_root, new_root):
    new = copy.deepcopy(new_root)
    count = new_count(SECTIONS)
    old_lex, new_lex = find(old_root, 'lexicon'), find(new, 'lexicon')
    if new_lex is not None:
        diff_records(
            old_lex, new_lex, 'entry',
            [lambda e: (text(e.find('hw')), _FIELDS['gl'](e)),
             lambda e: text(e.find('hw')) or None,
             (lambda e: attr(e, 'id') or None, _similar)],
            _FIELDS, count, 'entry')
    return new, summarize(count, SECTIONS)
