"""REwww/xslt.py – XSLT/XML rendering helpers for the Flask front-end."""

import collections
import copy
import os

import lxml.etree as ET

# Set by app.py after import:  xslt.STYLES_DIR = STYLES_DIR
STYLES_DIR: str = ''


def xml_to_html_from_tree(tree, stylesheet_name: str) -> str:
    """Apply a named XSLT stylesheet to an already-parsed lxml ElementTree.
    Returns an HTML fragment string."""
    xsl_path = os.path.join(STYLES_DIR, stylesheet_name)
    if not os.path.isfile(xsl_path):
        return f'<p class="text-danger">Stylesheet not found: <code>{stylesheet_name}</code></p>'
    try:
        result = ET.XSLT(ET.parse(xsl_path))(tree)
        return bytes(result).decode('utf-8')
    except Exception as exc:
        return f'<pre class="text-danger">XSLT error ({stylesheet_name}):\n{exc}</pre>'


def xml_to_html(xml_path: str, stylesheet_name: str,
                params: dict | None = None) -> str:
    """Apply a named XSLT stylesheet to an XML file; return an HTML fragment.

    Optional *params* dict maps XSLT parameter names to string values.
    """
    xsl_path = os.path.join(STYLES_DIR, stylesheet_name)
    if not os.path.isfile(xml_path):
        return f'<p class="text-danger">File not found: <code>{xml_path}</code></p>'
    if not os.path.isfile(xsl_path):
        return f'<p class="text-danger">Stylesheet not found: <code>{stylesheet_name}</code></p>'
    try:
        dom = ET.parse(xml_path)
        xslt_kwargs = {k: ET.XSLT.strparam(v) for k, v in (params or {}).items()}
        result = ET.XSLT(ET.parse(xsl_path))(dom, **xslt_kwargs)
        return bytes(result).decode('utf-8')
    except Exception as exc:
        return f'<pre class="text-danger">XSLT error ({stylesheet_name}):\n{exc}</pre>'


def compute_corr_freq(sets_path: str, corr_path: str):
    """Return a deep-copied corr ElementTree with freq stamped on every <corr>, <modern>, and <seg>.

    Each <corr freq="N"> carries row-level frequency (how many sets used that rule).
    Each <modern freq="N"> carries cell-level frequency (how many sets used that rule
    AND had a member from that dialect).
    Each <seg freq="N"> carries per-value frequency, determined as follows:
      - Cells with a single seg: seg freq = cell freq (trivially correct).
      - Cells with multiple segs: longest-prefix matching of the actual <lx> value
        against the seg list identifies which variant was used.  When prefix matching
        yields no hits for a (rule, dialect) pair (e.g. the dialect uses a different
        tone notation), all segs in that cell fall back to the cell freq so they are
        not shown as falsely unused.

    Sets with multiple reconstructions (<multi> children instead of a direct <rcn>)
    are also counted: every unique rule number across all <multi><rcn> elements
    contributes once to row_freq / cell_freq for that set.
    """
    row_freq  = collections.Counter()   # corr_num -> count
    cell_freq = collections.Counter()   # (corr_num, dialect) -> count
    seg_freq  = collections.Counter()   # (corr_num, dialect, seg_value) -> count

    # Build seg lookup (longest-first for unambiguous prefix matching)
    corr_tree = ET.parse(corr_path)
    seg_lookup: dict[tuple, list] = {}   # (corr_num, dialect) -> [seg_val, ...]
    for corr_el in corr_tree.getroot().findall('corr'):
        num = corr_el.get('num', '')
        for modern_el in corr_el.findall('modern'):
            dialect = modern_el.get('dialecte', '')
            vals = [s.text for s in modern_el.findall('seg') if s.text]
            seg_lookup[(num, dialect)] = sorted(vals, key=len, reverse=True)

    for s in ET.parse(sets_path).getroot().iter('set'):
        # Collect rule numbers — handle both single-reconstruction sets (direct
        # <rcn> child) and multi-reconstruction sets (<multi><rcn> children).
        rcn_el = s.find('rcn')
        if rcn_el is not None and rcn_el.text:
            nums = rcn_el.text.split()
        else:
            # Multi-form set: gather unique rules from every <multi><rcn>
            seen: dict[str, None] = {}
            for multi in s.findall('multi'):
                m_rcn = multi.find('rcn')
                if m_rcn is not None and m_rcn.text:
                    for n in m_rcn.text.split():
                        seen[n] = None
            nums = list(seen)           # preserves insertion order, deduplicated
            if not nums:
                continue

        dialects = [lg.text for lg in s.findall('.//rfx/lg') if lg.text]
        row_freq.update(nums)
        for num in nums:
            cell_freq.update((num, d) for d in dialects)

        # Per-seg matching: longest-prefix match of the actual lx value
        # (use <lxf> when present — that is the fuzzied form actually parsed).
        for rfx in s.findall('.//rfx'):
            lg_el = rfx.find('lg')
            if lg_el is None or not lg_el.text:
                continue
            lxf_el = rfx.find('lxf')
            lx_el  = rfx.find('lx')
            form_text = (lxf_el.text if lxf_el is not None and lxf_el.text
                         else lx_el.text if lx_el is not None else None)
            if not form_text:
                continue
            lg = lg_el.text
            for num in nums:
                key = (num, lg)
                if key not in seg_lookup:
                    continue
                for seg_val in seg_lookup[key]:   # longest-first → unambiguous prefix match
                    if form_text.startswith(seg_val):
                        seg_freq[(num, lg, seg_val)] += 1
                        break

    tree = copy.deepcopy(corr_tree)
    for corr_el in tree.getroot().findall('corr'):
        num = corr_el.get('num', '')
        corr_el.set('freq', str(row_freq.get(num, 0)))
        for modern_el in corr_el.findall('modern'):
            dialect = modern_el.get('dialecte', '')
            cf = cell_freq.get((num, dialect), 0)
            modern_el.set('freq', str(cf))
            segs = modern_el.findall('seg')
            if len(segs) == 1:
                # Trivial: the one seg always carries the full cell frequency.
                segs[0].set('freq', str(cf))
            else:
                # Per-seg breakdown from prefix matching.
                per_seg = [seg_freq.get((num, dialect, (seg_el.text or '')), 0)
                           for seg_el in segs]
                if sum(per_seg) == 0 and cf > 0:
                    # Prefix matching found nothing (different notation system,
                    # non-initial rule, etc.).  Fall back to cell freq for all
                    # segs so none appear falsely red.
                    for seg_el in segs:
                        seg_el.set('freq', str(cf))
                else:
                    for seg_el, sf in zip(segs, per_seg):
                        seg_el.set('freq', str(sf))
    return tree


def stylesheet_for(filename: str, mode: str = 'paragraph') -> str | None:
    """Return the XSLT stylesheet name for a given filename / display mode."""
    if 'correspondences.xml' in filename:
        return 'toc2html-view.xsl'
    if 'parameters.xml' in filename:
        return 'params2html-view.xsl'
    if 'fuz.xml' in filename:
        return 'fuzzy2html.xsl'
    if 'data.xml' in filename:
        return 'lexicon2html.xsl' if mode == 'paragraph' else 'lexicon2table.xsl'
    if 'sets.xml' in filename:
        return 'sets2html.xsl' if mode == 'paragraph' else 'sets2tabular.xsl'
    if 'mel.xml' in filename:
        return 'mel2html.xsl'
    if 'statistics.xml' in filename:
        return 'stats2html.xsl'
    return None
