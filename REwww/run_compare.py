"""REwww/run_compare.py – Set-level diff between two upstream runs.

Produces a <compare> XML document for persistence and XSLT rendering.
Call build_compare_xml(run_a, run_b) to get an lxml Element; the caller
(routes.py) serialises it to disk and transforms it with compare2html.xsl.
"""

import collections
import os
import time

import lxml.etree as ET


# ── XML parsing ────────────────────────────────────────────────────────────────

def _parse_sets(sets_path: str) -> dict:
    """Parse a sets.xml file.

    Returns a dict keyed by frozenset-of-rfx-ids (the unique identity of a
    cognate set) mapping to an info dict: pfm, rcn, mel, melid, lgs.
    """
    if not sets_path or not os.path.isfile(sets_path):
        return {}
    root = ET.parse(sets_path).getroot()
    result = {}
    for s in root.findall('.//set'):
        ids = frozenset(
            el.text for el in s.findall('.//rfx/id') if el.text
        )
        if not ids:
            continue

        multi = s.findall('multi')
        if multi:
            pfm = ' / '.join(m.findtext('pfm', '') for m in multi)
            rcn = ' / '.join(m.findtext('rcn', '') for m in multi)
        else:
            pfm = s.findtext('pfm', '')
            rcn = s.findtext('rcn', '')

        mel   = s.findtext('mel',   '')
        melid = s.findtext('melid', '')
        lgs   = sorted(set(el.text for el in s.findall('.//rfx/lg') if el.text))
        result[ids] = {'pfm': pfm, 'rcn': rcn, 'mel': mel, 'melid': melid, 'lgs': lgs}
    return result


def _count_lex_stats(sets_path: str):
    """Parse a sets.xml file; return per-language reflex/isolate/failure counts.

    Returns a 4-tuple:
      (total_reflexes: int,
       rfx_by_lg:  dict[str, int],   # reflexes in cognate sets, by language
       iso_by_lg:  dict[str, int],   # isolates, by language
       fail_by_lg: dict[str, int])   # failures, by language

    Returns (0, {}, {}, {}) when the file is missing or unreadable.
    """
    if not sets_path or not os.path.isfile(sets_path):
        return 0, {}, {}, {}
    try:
        root = ET.parse(sets_path).getroot()
    except Exception:
        return 0, {}, {}, {}

    rfx_by_lg  = collections.Counter()
    iso_by_lg  = collections.Counter()
    fail_by_lg = collections.Counter()

    # Reflexes in cognate sets (all <rfx> at any depth inside <sets>)
    for rfx in root.findall('.//sets//rfx'):
        lg = rfx.findtext('lg', '')
        if lg:
            rfx_by_lg[lg] += 1

    # Isolates (direct <rfx> children of <isolates>)
    for rfx in root.findall('.//isolates/rfx'):
        lg = rfx.findtext('lg', '')
        if lg:
            iso_by_lg[lg] += 1

    # Failures (direct <rfx> children of <failures>)
    for rfx in root.findall('.//failures/rfx'):
        lg = rfx.findtext('lg', '')
        if lg:
            fail_by_lg[lg] += 1

    return (sum(rfx_by_lg.values()),
            dict(rfx_by_lg), dict(iso_by_lg), dict(fail_by_lg))


def _bn(path: str) -> str:
    """Return the basename of a path, or empty string."""
    return os.path.basename(path) if path else ''


# ── XML element builders ───────────────────────────────────────────────────────

def _run_el(label: str, rec: dict, sets_found: bool, reflexes: int) -> ET.Element:
    """Build a <run id="a|b"> element from a run record dict."""
    el = ET.Element('run')
    el.set('id',          label)
    el.set('run_id',      rec.get('run_id',   ''))
    el.set('run_name',    rec.get('run_name',  ''))
    el.set('sets_found',  'true' if sets_found else 'false')

    params = rec.get('params', {})
    for key in ('recon', 'mel', 'fuzzy', 'upstream'):
        val = params.get(key, '') or ''
        p = ET.SubElement(el, 'param')
        p.set('key',   key)
        p.set('value', _bn(val) if key != 'upstream' else val)

    # Stats: sets first, then reflexes (total forms in sets), then isolates/failures
    for key, value in (('sets',      str(rec.get('sets',      ''))),
                       ('reflexes',  str(reflexes)),
                       ('isolates',  str(rec.get('isolates',  ''))),
                       ('failures',  str(rec.get('failures',  '')))):
        s = ET.SubElement(el, 'stat')
        s.set('key',   key)
        s.set('value', value)

    return el


def _set_el_changed(ids_key: frozenset,
                    info_a: dict, info_b: dict) -> ET.Element:
    """Build a <set> element for the changed-sets section."""
    s = ET.Element('set')
    ET.SubElement(s, 'melid').text = info_a.get('melid') or info_b.get('melid') or ''
    ET.SubElement(s, 'pfm_a').text = info_a.get('pfm', '')
    ET.SubElement(s, 'rcn_a').text = info_a.get('rcn', '')
    ET.SubElement(s, 'pfm_b').text = info_b.get('pfm', '')
    ET.SubElement(s, 'rcn_b').text = info_b.get('rcn', '')
    lgs_el = ET.SubElement(s, 'languages')
    for lg in info_a.get('lgs', []):
        ET.SubElement(lgs_el, 'lg').text = lg
    mem_el = ET.SubElement(s, 'members')
    for m in sorted(ids_key):
        ET.SubElement(mem_el, 'm').text = m
    return s


def _set_el_single(ids_key: frozenset, info: dict) -> ET.Element:
    """Build a <set> element for the lost/gained sections."""
    s = ET.Element('set')
    ET.SubElement(s, 'melid').text = info.get('melid', '')
    ET.SubElement(s, 'pfm').text   = info.get('pfm',   '')
    ET.SubElement(s, 'rcn').text   = info.get('rcn',   '')
    lgs_el = ET.SubElement(s, 'languages')
    for lg in info.get('lgs', []):
        ET.SubElement(lgs_el, 'lg').text = lg
    mem_el = ET.SubElement(s, 'members')
    for m in sorted(ids_key):
        ET.SubElement(mem_el, 'm').text = m
    return s


# ── Main entry point ───────────────────────────────────────────────────────────

def build_compare_xml(run_a: dict, run_b: dict) -> ET.Element:
    """Compare two run records; return a <compare> lxml Element.

    The element can be serialised to disk with ET.ElementTree(...).write(...)
    and then rendered via compare2html.xsl.
    """
    sets_path_a = run_a.get('files', {}).get('sets', '')
    sets_path_b = run_b.get('files', {}).get('sets', '')
    sets_a      = _parse_sets(sets_path_a)
    sets_b      = _parse_sets(sets_path_b)

    # Per-language reflex / isolate / failure counts
    rfx_a, rfx_by_lg_a, iso_by_lg_a, fail_by_lg_a = _count_lex_stats(sets_path_a)
    rfx_b, rfx_by_lg_b, iso_by_lg_b, fail_by_lg_b = _count_lex_stats(sets_path_b)

    keys_a = set(sets_a)
    keys_b = set(sets_b)
    shared = keys_a & keys_b
    lost   = keys_a - keys_b   # in A, not in B
    gained = keys_b - keys_a   # in B, not in A

    changed, same = [], 0
    for k in shared:
        a, b = sets_a[k], sets_b[k]
        if a['pfm'] != b['pfm'] or a['rcn'] != b['rcn']:
            changed.append((k, a, b))
        else:
            same += 1

    # ── Root element ──────────────────────────────────────────────────────────
    root = ET.Element('compare')
    root.set('project',    run_a.get('project',  ''))
    root.set('created',    time.strftime('%Y-%m-%dT%H:%M:%S'))
    root.set('run_name_a', run_a.get('run_name', ''))
    root.set('run_name_b', run_b.get('run_name', ''))

    root.append(_run_el('a', run_a, bool(sets_a), rfx_a))
    root.append(_run_el('b', run_b, bool(sets_b), rfx_b))

    summary = ET.SubElement(root, 'summary')
    summary.set('same',    str(same))
    summary.set('changed', str(len(changed)))
    summary.set('lost',    str(len(lost)))
    summary.set('gained',  str(len(gained)))

    # ── Lexicon statistics (union of all languages across both runs) ───────────
    all_langs = sorted(
        set(rfx_by_lg_a) | set(rfx_by_lg_b) |
        set(iso_by_lg_a) | set(iso_by_lg_b) |
        set(fail_by_lg_a) | set(fail_by_lg_b)
    )
    lex_el = ET.SubElement(root, 'lexicon_stats')
    for lg in all_langs:
        lg_el = ET.SubElement(lex_el, 'lang')
        lg_el.set('name', lg)
        ET.SubElement(lg_el, 'rfx_a').text  = str(rfx_by_lg_a.get(lg,  0))
        ET.SubElement(lg_el, 'iso_a').text  = str(iso_by_lg_a.get(lg,  0))
        ET.SubElement(lg_el, 'fail_a').text = str(fail_by_lg_a.get(lg, 0))
        ET.SubElement(lg_el, 'rfx_b').text  = str(rfx_by_lg_b.get(lg,  0))
        ET.SubElement(lg_el, 'iso_b').text  = str(iso_by_lg_b.get(lg,  0))
        ET.SubElement(lg_el, 'fail_b').text = str(fail_by_lg_b.get(lg, 0))

    # ── Changed sets ──────────────────────────────────────────────────────────
    ch_el = ET.SubElement(root, 'changed')
    for k, a, b in sorted(changed, key=lambda x: x[1]['pfm']):
        ch_el.append(_set_el_changed(k, a, b))

    # ── Lost sets (in A, not in B) ────────────────────────────────────────────
    lost_el = ET.SubElement(root, 'lost')
    for k, info in sorted(
            [(k, sets_a[k]) for k in lost], key=lambda x: x[1]['pfm']):
        lost_el.append(_set_el_single(k, info))

    # ── Gained sets (in B, not in A) ─────────────────────────────────────────
    gained_el = ET.SubElement(root, 'gained')
    for k, info in sorted(
            [(k, sets_b[k]) for k in gained], key=lambda x: x[1]['pfm']):
        gained_el.append(_set_el_single(k, info))

    return root
