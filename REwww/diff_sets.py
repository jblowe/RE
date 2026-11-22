"""REwww/diff_sets.py – annotate a cognate-sets file (<reconstruction> with
<sets>, <isolates>, <failures>) with its differences. Rendered by sets2tabular.xsl (and
sets-isolates-failures.xsl).

Set numbers are generated per run, so they never identify a set. Sets are matched
by (proto-form, member reflexes), then by the members they share (at least half
of the combined membership), and a set's number is not itself a difference.
Isolates and failures are matched by reflex id (the lexicon id, e.g. tag.4).
"""

import copy

import lxml.etree as ET

from diff_common import (Overlap, attr, diff_list, diff_records, find,
                         new_count, summarize, text)

SECTIONS = ('set', 'member', 'isolate', 'failure')
_MEMBER = ('rfx',)


def _pfm(s):
    multi = s.findall('multi')
    if multi:
        return ' / '.join(text(m.find('pfm')) for m in multi)
    return text(s.find('pfm'))


def _rcn(s):
    multi = s.findall('multi')
    if multi:
        return ' / '.join(' '.join(text(m.find('rcn')).split()) for m in multi)
    return ' '.join(text(s.find('rcn')).split())


def _member_ids(s):
    return [text(r.find('id')) for r in s.iter('rfx') if r.find('id') is not None]


_SET_FIELDS = {'pfm': _pfm, 'rcn': _rcn}


def _rfx_sig(r):
    return (text(r.find('lg')), text(r.find('id')), text(r.find('lx')),
            text(r.find('gl')))


def _rfx_shown(r):
    gl = text(r.find('gl'))
    return text(r.find('lx')) + (f' ({gl})' if gl else '')


def _rfx_id(r):
    return attr(r, 'id') or text(r.find('id'))


def _recons(r, part):
    return '; '.join(text(x.find(part)) if part == 'pfm'
                     else ' '.join(text(x.find(part)).split())
                     for x in r.findall('recon'))


_COMMON = {
    'lg': lambda r: text(r.find('lg')),
    'lx': lambda r: text(r.find('lx')),
    'gl': lambda r: text(r.find('gl')),
}
# the fields each table shows (see sets-isolates-failures.xsl)
_ISO_FIELDS = dict(_COMMON, pfm=lambda r: _recons(r, 'pfm'),
                   rcn=lambda r: _recons(r, 'rcn'))
_FAIL_FIELDS = dict(_COMMON, reasons=lambda r: '; '.join(
    text(x) for x in r.findall('reasons/reason')))


def _diff_section(old_root, new, tag, count, section, fields):
    old_s, new_s = find(old_root, tag), find(new, tag)
    if new_s is None:
        return
    diff_records(old_s, new_s, 'rfx',
                 [lambda r: _rfx_id(r) or None,
                  lambda r: (text(r.find('lg')), text(r.find('lx')))],
                 fields, count, section)


def _union_languages(old_root, new):
    old_l, new_l = find(old_root, 'languages'), find(new, 'languages')
    if new_l is None:
        return
    have = {text(x) for x in new_l.findall('lg')}
    for lg in (old_l.findall('lg') if old_l is not None else []):
        if text(lg) not in have:
            d = copy.deepcopy(lg)
            d.set('diff', 'deleted')
            new_l.append(d)


def annotate(old_root, new_root):
    new = copy.deepcopy(new_root)
    count = new_count(SECTIONS)
    _union_languages(old_root, new)
    old_sets, new_sets = find(old_root, 'sets'), find(new, 'sets')
    if new_sets is not None:
        def members(o, n):
            os_, ns = o.find('sf'), n.find('sf')
            if os_ is not None and ns is not None:
                diff_list(os_, ns, 'rfx', _rfx_sig, _rfx_shown, count, 'member')
        diff_records(
            old_sets, new_sets, 'set',
            [lambda s: (_pfm(s), tuple(sorted(_member_ids(s)))),
             Overlap(_member_ids, 0.5)],
            _SET_FIELDS, count, 'set', on_match=members,
            subtree_tags=_MEMBER)
    _diff_section(old_root, new, 'isolates', count, 'isolate', _ISO_FIELDS)
    _diff_section(old_root, new, 'failures', count, 'failure', _FAIL_FIELDS)
    return new, summarize(count, SECTIONS)
