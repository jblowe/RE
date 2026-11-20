"""REwww/xslt.py – XSLT/XML rendering helpers for the Flask front-end."""

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


def compute_corr_freq(stats_path: str, corr_path: str):
    """Return a deep-copied corr ElementTree with freq stamped on every <corr>,
    <modern> and <seg>, or None when the run's statistics file has no usage
    counts for this table (runs made before counts were recorded).

    The counts are written at run time by the engine (RE.tally_set_usage ->
    serialize.serialize_stats, <toc_usage>) and count REFLEXES IN COGNATE SETS,
    each reflex at most once per item:
      - <corr freq>   reflexes whose derivation uses this correspondence;
      - <modern freq> of those, the reflexes of this language;
      - <seg freq>    of those, the reflexes where this particular variant
                      (identified by its position in the cell) matched.
    Anything the run did not record is 0. Isolates and failures never count.
    """
    usage_root = ET.parse(stats_path).getroot().find('toc_usage')
    if usage_root is None:
        return None
    base = os.path.basename(corr_path)
    levels = usage_root.findall('level')
    level = next((l for l in levels if l.get('file') == base), None)
    if level is None:
        return None

    row_freq, cell_freq, seg_freq = {}, {}, {}
    for corr in level.findall('corr'):
        num = corr.get('num', '')
        row_freq[num] = corr.get('uses', '0')
        for modern in corr.findall('modern'):
            lg = modern.get('dialecte', '')
            cell_freq[(num, lg)] = modern.get('uses', '0')
            for seg in modern.findall('seg'):
                seg_freq[(num, lg, int(seg.get('idx', '0')))] = seg.get('uses', '0')

    tree = copy.deepcopy(ET.parse(corr_path))
    for corr_el in tree.getroot().findall('corr'):
        num = corr_el.get('num', '')
        corr_el.set('freq', row_freq.get(num, '0'))
        for modern_el in corr_el.findall('modern'):
            lg = modern_el.get('dialecte', '')
            modern_el.set('freq', cell_freq.get((num, lg), '0'))
            for idx, seg_el in enumerate(modern_el.findall('seg')):
                seg_el.set('freq', seg_freq.get((num, lg, idx), '0'))
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
