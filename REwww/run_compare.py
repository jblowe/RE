"""REwww/compare.py – Set-level diff between two upstream runs."""

import html as _html
import os

import lxml.etree as ET


# ── XML parsing ───────────────────────────────────────────────────────────────

def _parse_sets(sets_path: str) -> dict:
    """Parse a sets.xml file.

    Returns a dict keyed by frozenset-of-rfx-ids (the unique identity of a
    cognate set) mapping to a small info dict with pfm, rcn, mel, lgs.
    """
    if not sets_path or not os.path.isfile(sets_path):
        return {}
    root = ET.parse(sets_path).getroot()
    result = {}
    for s in root.findall('.//set'):
        # Collect all modern-form IDs from this set (child <id> of every <rfx>)
        ids = frozenset(
            el.text for el in s.findall('.//rfx/id') if el.text
        )
        if not ids:
            continue

        # Handle competing reconstructions (<multi> blocks) vs direct pfm/rcn
        multi = s.findall('multi')
        if multi:
            pfm = ' / '.join(m.findtext('pfm', '') for m in multi)
            rcn = ' / '.join(m.findtext('rcn', '') for m in multi)
        else:
            pfm = s.findtext('pfm', '')
            rcn = s.findtext('rcn', '')

        mel = s.findtext('mel', '')
        lgs = sorted(set(el.text for el in s.findall('.//rfx/lg') if el.text))
        result[ids] = {'pfm': pfm, 'rcn': rcn, 'mel': mel, 'lgs': lgs}
    return result


# ── HTML helpers ──────────────────────────────────────────────────────────────

def _h(s) -> str:
    return _html.escape(str(s) if s is not None else '')

def _bn(path: str) -> str:
    return os.path.basename(path) if path else '—'


# ── Sub-tables ────────────────────────────────────────────────────────────────

def _params_table(a: dict, b: dict) -> str:
    pa, pb = a.get('params', {}), b.get('params', {})
    rows = [
        ('Run',      a.get('run_name', ''),           b.get('run_name', '')),
        ('Recon',    _bn(pa.get('recon',  '')),        _bn(pb.get('recon',  ''))),
        ('MEL',      _bn(pa.get('mel',    '')),        _bn(pb.get('mel',    ''))),
        ('Fuzzy',    _bn(pa.get('fuzzy',  '')),        _bn(pb.get('fuzzy',  ''))),
        ('Upstream', pa.get('upstream', '') or '—',   pb.get('upstream', '') or '—'),
    ]
    lines = [
        '<h5>Parameters</h5>',
        '<table class="table table-sm table-bordered" style="max-width:660px">',
        '<thead><tr><th>Param</th><th>Run A</th><th>Run B</th></tr></thead><tbody>',
    ]
    for label, va, vb in rows:
        cls = ' class="table-warning"' if va != vb else ''
        lines.append(
            f'<tr{cls}><td>{_h(label)}</td>'
            f'<td>{_h(va)}</td><td>{_h(vb)}</td></tr>'
        )
    lines += ['</tbody></table>']
    return '\n'.join(lines)


def _stats_table(a: dict, b: dict) -> str:
    keys = [('sets', 'Sets'), ('isolates', 'Isolates'), ('failures', 'Failures')]
    lines = [
        '<h5>Statistics</h5>',
        '<table class="table table-sm table-bordered" style="max-width:440px">',
        '<thead><tr><th>Stat</th><th>Run A</th><th>Run B</th><th>Δ</th>'
        '</tr></thead><tbody>',
    ]
    for key, label in keys:
        va = a.get(key, '?')
        vb = b.get(key, '?')
        try:
            delta     = int(vb) - int(va)
            delta_str = ('+' if delta > 0 else '') + str(delta)
            dcls      = ('text-success' if delta > 0
                         else 'text-danger' if delta < 0
                         else 'text-muted')
        except (TypeError, ValueError):
            delta_str, dcls = '?', 'text-muted'
        lines.append(
            f'<tr><td>{label}</td><td>{va}</td><td>{vb}</td>'
            f'<td class="{dcls}">{_h(delta_str)}</td></tr>'
        )
    lines += ['</tbody></table>']
    return '\n'.join(lines)


def _changed_table(changed: list) -> str:
    lines = [
        '<table class="table table-sm table-striped table-bordered table-hover sortable">',
        '<thead><tr><th>MEL</th><th>pfm (A)</th><th>rcn (A)</th>'
        '<th>pfm (B)</th><th>rcn (B)</th><th>languages</th>'
        '</tr></thead><tbody>',
    ]
    for _, a, b in sorted(changed, key=lambda x: x[1]['pfm']):
        pcls = ' class="table-warning"' if a['pfm'] != b['pfm'] else ''
        lgs  = _h(', '.join(a['lgs']))
        lines.append(
            f'<tr><td>{_h(a["mel"] or "—")}</td>'
            f'<td{pcls}>{_h(a["pfm"])}</td><td>{_h(a["rcn"])}</td>'
            f'<td{pcls}>{_h(b["pfm"])}</td><td>{_h(b["rcn"])}</td>'
            f'<td style="font-size:.8em">{lgs}</td></tr>'
        )
    lines += ['</tbody></table>']
    return '\n'.join(lines)


def _single_table(items: list) -> str:
    lines = [
        '<table class="table table-sm table-striped table-bordered table-hover sortable">',
        '<thead><tr><th>MEL</th><th>pfm</th><th>rcn</th><th>languages</th>'
        '</tr></thead><tbody>',
    ]
    for _, s in items:
        lgs = _h(', '.join(s['lgs']))
        lines.append(
            f'<tr><td>{_h(s["mel"] or "—")}</td>'
            f'<td>{_h(s["pfm"])}</td><td>{_h(s["rcn"])}</td>'
            f'<td style="font-size:.8em">{lgs}</td></tr>'
        )
    lines += ['</tbody></table>']
    return '\n'.join(lines)


# ── Main entry point ──────────────────────────────────────────────────────────

def compare_runs(run_a: dict, run_b: dict) -> str:
    """Compare two run records; return an HTML fragment."""
    sets_a = _parse_sets(run_a.get('files', {}).get('sets', ''))
    sets_b = _parse_sets(run_b.get('files', {}).get('sets', ''))

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

    parts = [_params_table(run_a, run_b), _stats_table(run_a, run_b)]

    parts.append(
        f'<h5 style="margin-top:1.2rem">Set differences '
        f'<small class="text-muted" style="font-size:.8em;font-weight:normal">'
        f'{same} identical &nbsp;·&nbsp; {len(changed)} changed reconstruction'
        f' &nbsp;·&nbsp; {len(lost)} lost &nbsp;·&nbsp; {len(gained)} gained'
        f'</small></h5>'
    )

    if not sets_a and not sets_b:
        parts.append(
            '<p class="text-warning">Sets files not found for one or both runs.</p>'
        )
    else:
        if changed:
            parts.append(
                f'<h6>Changed reconstruction '
                f'<small class="text-muted">(n={len(changed)})</small></h6>'
            )
            parts.append(_changed_table(changed))
        if lost:
            items = sorted(
                [(k, sets_a[k]) for k in lost], key=lambda x: x[1]['pfm'])
            parts.append(
                f'<h6>Lost sets '
                f'<small class="text-muted">(in A only, n={len(lost)})</small></h6>'
            )
            parts.append(_single_table(items))
        if gained:
            items = sorted(
                [(k, sets_b[k]) for k in gained], key=lambda x: x[1]['pfm'])
            parts.append(
                f'<h6>Gained sets '
                f'<small class="text-muted">(in B only, n={len(gained)})</small></h6>'
            )
            parts.append(_single_table(items))

    return '\n'.join(parts)
