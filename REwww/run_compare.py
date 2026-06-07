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

def _parse_sets(sets_path: str) -> list:
    """Parse a sets.xml file.

    Returns a list of set-info dicts (one per <set>, in document order).
    Each dict has: key (frozenset of rfx ids), pfm, rcn, mel, melid, lgs, reflexes.

    Unlike a dict keyed by frozenset, this preserves ALL sets — including
    cases where two distinct proto-forms cover exactly the same attested forms
    (same frozenset key, different pfm/rcn).  <multi> reconstructions within a
    single <set> are sorted by pfm for deterministic join order.
    """
    if not sets_path or not os.path.isfile(sets_path):
        return []
    root = ET.parse(sets_path).getroot()
    result = []
    for s in root.findall('.//sets/set'):
        rfx_list = []
        ids = []
        for rfx in s.findall('.//rfx'):
            rfx_id = rfx.findtext('id', '')
            if rfx_id:
                ids.append(rfx_id)
                rfx_list.append({
                    'id':  rfx_id,
                    'lg':  rfx.findtext('lg',  ''),
                    'lx':  rfx.findtext('lx',  ''),   # original form
                    'lxf': rfx.findtext('lxf', ''),   # fuzzied form (empty if none)
                    'gl':  rfx.findtext('gl',  ''),
                })
        if not ids:
            continue

        key   = frozenset(ids)
        multi = s.findall('multi')
        if multi:
            # Sort by pfm so the join order is deterministic across runs
            multi_sorted = sorted(multi, key=lambda m: m.findtext('pfm', ''))
            pfm = ' / '.join(m.findtext('pfm', '') for m in multi_sorted)
            rcn = ' / '.join(m.findtext('rcn', '') for m in multi_sorted)
        else:
            pfm = s.findtext('pfm', '')
            rcn = s.findtext('rcn', '')

        result.append({
            'key':      key,
            'pfm':      pfm,
            'rcn':      rcn,
            'mel':      s.findtext('mel',   ''),
            'melid':    s.findtext('melid', ''),
            'lgs':      sorted(set(r['lg'] for r in rfx_list if r['lg'])),
            'reflexes': rfx_list,
        })
    return result


def _count_lex_stats(sets_path: str):
    """Return (total_reflexes, rfx_by_lg, iso_by_lg, fail_by_lg)."""
    if not sets_path or not os.path.isfile(sets_path):
        return 0, {}, {}, {}
    try:
        root = ET.parse(sets_path).getroot()
    except Exception:
        return 0, {}, {}, {}

    rfx_by_lg  = collections.Counter()
    iso_by_lg  = collections.Counter()
    fail_by_lg = collections.Counter()

    for rfx in root.findall('.//sets//rfx'):
        lg = rfx.findtext('lg', '')
        if lg:
            rfx_by_lg[lg] += 1
    for rfx in root.findall('.//isolates/rfx'):
        lg = rfx.findtext('lg', '')
        if lg:
            iso_by_lg[lg] += 1
    for rfx in root.findall('.//failures/rfx'):
        lg = rfx.findtext('lg', '')
        if lg:
            fail_by_lg[lg] += 1

    return (sum(rfx_by_lg.values()),
            dict(rfx_by_lg), dict(iso_by_lg), dict(fail_by_lg))


def _bn(path: str) -> str:
    return os.path.basename(path) if path else ''


# ── Lost↔gained matching ────────────────────────────────────────────────────────

def _match_lost_gained(lost_items: list, gained_items: list):
    """Greedily pair lost (A) and gained (B) set-info dicts by Jaccard overlap.

    Returns (pairs: list[(lost_info, gained_info)],
             unmatched_lost:   list of info dicts,
             unmatched_gained: list of info dicts).

    Only pairs with at least one shared rfx ID are considered.
    Pairs are sorted by Jaccard descending so the best matches are taken first.
    """
    candidates = []
    for li, la in enumerate(lost_items):
        for gi, ga in enumerate(gained_items):
            lk = la['key']
            gk = ga['key']
            overlap = len(lk & gk)
            if overlap > 0:
                jaccard = overlap / len(lk | gk)
                candidates.append((jaccard, overlap, li, gi))

    # Best match first
    candidates.sort(key=lambda x: (-x[0], -x[1]))

    matched_lost   = set()
    matched_gained = set()
    pairs = []

    for _jaccard, _overlap, li, gi in candidates:
        if li not in matched_lost and gi not in matched_gained:
            matched_lost.add(li)
            matched_gained.add(gi)
            pairs.append((lost_items[li], gained_items[gi]))

    truly_lost   = [la for li, la in enumerate(lost_items)   if li not in matched_lost]
    truly_gained = [ga for gi, ga in enumerate(gained_items) if gi not in matched_gained]
    return pairs, truly_lost, truly_gained


# ── XML element builders ────────────────────────────────────────────────────────

def _run_el(label: str, rec: dict, sets_found: bool, reflexes: int) -> ET.Element:
    el = ET.Element('run')
    el.set('id',         label)
    el.set('run_id',     rec.get('run_id',   ''))
    el.set('run_name',   rec.get('run_name',  ''))
    el.set('sets_found', 'true' if sets_found else 'false')

    params = rec.get('params', {})
    for key in ('recon', 'mel', 'fuzzy', 'upstream'):
        val = params.get(key, '') or ''
        p = ET.SubElement(el, 'param')
        p.set('key',   key)
        p.set('value', _bn(val) if key != 'upstream' else val)
    for key in ('context_match_type', 'spec'):
        p = ET.SubElement(el, 'param')
        p.set('key',   key)
        p.set('value', params.get(key, '') or '')

    for key, value in (('sets',     str(rec.get('sets',     ''))),
                       ('reflexes', str(reflexes)),
                       ('isolates', str(rec.get('isolates', ''))),
                       ('failures', str(rec.get('failures', '')))):
        s = ET.SubElement(el, 'stat')
        s.set('key',   key)
        s.set('value', value)
    return el


def _diff_el(info_a, info_b, ids_a, ids_b):
    """Build a unified-diff <diff> element for a set pair (or one-sided set).

    info_a / info_b  : set info dicts (or None for one-sided diffs)
    ids_a  / ids_b   : frozensets of rfx IDs (pass frozenset() when absent)

    Each <rfx> child carries status="both|removed|added".
    Reflexes from A come first (both + removed), then B-only (added).
    """
    d = ET.Element('diff')

    both = ids_a & ids_b

    melid = ''
    if info_a:
        melid = info_a.get('melid', '') or ''
        ET.SubElement(d, 'pfm_a').text = info_a.get('pfm', '')
        ET.SubElement(d, 'rcn_a').text = info_a.get('rcn', '')
    if info_b:
        if not melid:
            melid = info_b.get('melid', '') or ''
        ET.SubElement(d, 'pfm_b').text = info_b.get('pfm', '')
        ET.SubElement(d, 'rcn_b').text = info_b.get('rcn', '')
    ET.SubElement(d, 'melid').text = melid

    rfxs_el = ET.SubElement(d, 'reflexes')
    emitted  = set()

    # A's reflexes first: both (unchanged) and removed
    for rfx in (info_a or {}).get('reflexes', []):
        if rfx['id'] in emitted:
            continue
        emitted.add(rfx['id'])
        re = ET.SubElement(rfxs_el, 'rfx')
        re.set('id',     rfx['id'])
        re.set('lg',     rfx['lg'])
        re.set('lx',     rfx['lx'])
        re.set('lxf',    rfx.get('lxf', ''))
        re.set('gl',     rfx['gl'])
        re.set('status', 'both' if rfx['id'] in both else 'removed')

    # B-only reflexes: added
    for rfx in (info_b or {}).get('reflexes', []):
        if rfx['id'] in emitted:
            continue
        emitted.add(rfx['id'])
        re = ET.SubElement(rfxs_el, 'rfx')
        re.set('id',     rfx['id'])
        re.set('lg',     rfx['lg'])
        re.set('lx',     rfx['lx'])
        re.set('lxf',    rfx.get('lxf', ''))
        re.set('gl',     rfx['gl'])
        re.set('status', 'added')

    return d


# ── Main entry point ───────────────────────────────────────────────────────────

def build_compare_xml(run_a: dict, run_b: dict) -> ET.Element:
    """Compare two run records; return a <compare> lxml Element."""
    sets_path_a = run_a.get('files', {}).get('sets', '')
    sets_path_b = run_b.get('files', {}).get('sets', '')
    sets_a      = _parse_sets(sets_path_a)
    sets_b      = _parse_sets(sets_path_b)

    rfx_a, rfx_by_lg_a, iso_by_lg_a, fail_by_lg_a = _count_lex_stats(sets_path_a)
    rfx_b, rfx_by_lg_b, iso_by_lg_b, fail_by_lg_b = _count_lex_stats(sets_path_b)

    # ── Match sets_a → sets_b ─────────────────────────────────────────────────
    # Group B sets by frozenset key for efficient lookup.
    b_by_key = collections.defaultdict(list)
    for j, sb in enumerate(sets_b):
        b_by_key[sb['key']].append(j)

    b_taken      = set()   # indices into sets_b already matched
    same         = 0
    changed_recon = []     # list of (info_a, info_b) – same members, different pfm/rcn
    unmatched_a  = []      # info dicts from A with no B match (for Jaccard matching)

    for sa in sets_a:
        key        = sa['key']
        candidates = [j for j in b_by_key.get(key, []) if j not in b_taken]

        if not candidates:
            # No B set shares this frozenset key → will try Jaccard matching later
            unmatched_a.append(sa)
            continue

        # Prefer an exact (pfm, rcn) match
        exact = next((j for j in candidates
                      if sets_b[j]['pfm'] == sa['pfm'] and sets_b[j]['rcn'] == sa['rcn']),
                     None)
        if exact is not None:
            same += 1
            b_taken.add(exact)
        else:
            # Same member set, different reconstruction → changed_recon
            j = candidates[0]
            changed_recon.append((sa, sets_b[j]))
            b_taken.add(j)

    unmatched_b = [sb for j, sb in enumerate(sets_b) if j not in b_taken]

    # Match unmatched A (lost) ↔ unmatched B (gained) by rfx-ID Jaccard overlap
    pairs, truly_lost, truly_gained = _match_lost_gained(unmatched_a, unmatched_b)

    # ── Root ──────────────────────────────────────────────────────────────────
    root = ET.Element('compare')
    root.set('project',    run_a.get('project',  ''))
    root.set('created',    time.strftime('%Y-%m-%dT%H:%M:%S'))
    root.set('run_name_a', run_a.get('run_name', ''))
    root.set('run_name_b', run_b.get('run_name', ''))

    # ── Parameter diffs ────────────────────────────────────────────────────────
    params_a = run_a.get('params', {})
    params_b = run_b.get('params', {})
    diffs_el = ET.SubElement(root, 'param_diffs')
    for key in ('recon', 'mel', 'fuzzy', 'upstream', 'context_match_type', 'spec'):
        va = _bn(params_a.get(key, '') or '') if key in ('recon', 'mel', 'fuzzy') \
             else (params_a.get(key, '') or '')
        vb = _bn(params_b.get(key, '') or '') if key in ('recon', 'mel', 'fuzzy') \
             else (params_b.get(key, '') or '')
        if va != vb:
            d = ET.SubElement(diffs_el, 'diff')
            d.set('key', key); d.set('value_a', va); d.set('value_b', vb)

    root.append(_run_el('a', run_a, bool(sets_a), rfx_a))
    root.append(_run_el('b', run_b, bool(sets_b), rfx_b))

    # ── Summary ────────────────────────────────────────────────────────────────
    summary = ET.SubElement(root, 'summary')
    summary.set('same',             str(same))
    summary.set('changed_recon',    str(len(changed_recon)))
    summary.set('changed_members',  str(len(pairs)))
    summary.set('unmatched_lost',   str(len(truly_lost)))
    summary.set('unmatched_gained', str(len(truly_gained)))

    # ── Lexicon statistics ─────────────────────────────────────────────────────
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

    # ── Changed reconstruction (same members, different pfm/rcn) ──────────────
    cr_el = ET.SubElement(root, 'diffs')
    cr_el.set('type', 'changed_recon')
    for a, b in sorted(changed_recon, key=lambda x: x[0]['pfm']):
        cr_el.append(_diff_el(a, b, a['key'], b['key']))

    # ── Membership diffs (matched lost↔gained pairs) ───────────────────────────
    cm_el = ET.SubElement(root, 'diffs')
    cm_el.set('type', 'changed_members')
    for a, b in sorted(pairs, key=lambda p: p[0]['pfm']):
        cm_el.append(_diff_el(a, b, a['key'], b['key']))

    # ── Unmatched lost (no overlapping gained set) ─────────────────────────────
    lo_el = ET.SubElement(root, 'diffs')
    lo_el.set('type', 'lost')
    for a in sorted(truly_lost, key=lambda x: x['pfm']):
        lo_el.append(_diff_el(a, None, a['key'], frozenset()))

    # ── Unmatched gained (no overlapping lost set) ─────────────────────────────
    ga_el = ET.SubElement(root, 'diffs')
    ga_el.set('type', 'gained')
    for b in sorted(truly_gained, key=lambda x: x['pfm']):
        ga_el.append(_diff_el(None, b, frozenset(), b['key']))

    return root
