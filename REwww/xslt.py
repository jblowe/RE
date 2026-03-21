"""REwww/xslt.py – XSLT/XML rendering helpers for the Flask front-end."""

import collections
import copy
import os

import lxml.etree as ET

# Set by app.py after import:  xslt.STYLES_DIR = STYLES_DIR
STYLES_DIR: str = ''


def xml_to_html_from_tree(tree, stylesheet_name: str) -> str:
    """Apply a named XSLT stylesheet to an already-parsed lxml ElementTree.
    Returns an HTML fragment (body inner content only)."""
    xsl_path = os.path.join(STYLES_DIR, stylesheet_name)
    if not os.path.isfile(xsl_path):
        return f'<p class="text-danger">Stylesheet not found: <code>{stylesheet_name}</code></p>'
    try:
        result    = ET.XSLT(ET.parse(xsl_path))(tree)
        html_root = ET.HTML(bytes(result), parser=ET.HTMLParser(encoding='utf-8'))
        if html_root is not None:
            body = html_root.find('.//body')
            if body is not None:
                parts = [body.text or '']
                for child in body:
                    parts.append(ET.tostring(child, encoding='unicode', method='html'))
                return ''.join(parts)
        return str(result)
    except Exception as exc:
        return f'<pre class="text-danger">XSLT error ({stylesheet_name}):\n{exc}</pre>'


def xml_to_html(xml_path: str, stylesheet_name: str) -> str:
    """Apply a named XSLT stylesheet to an XML file; return HTML fragment.

    The XSLT stylesheets produce full HTML pages (html/head/body).  We extract
    only the body's inner content so the fragment can be safely injected into a
    div without duplicate html/head/body wrappers or stray <link> elements that
    confuse the browser's CSS loader.
    """
    xsl_path = os.path.join(STYLES_DIR, stylesheet_name)
    if not os.path.isfile(xml_path):
        return f'<p class="text-danger">File not found: <code>{xml_path}</code></p>'
    if not os.path.isfile(xsl_path):
        return f'<p class="text-danger">Stylesheet not found: <code>{stylesheet_name}</code></p>'
    try:
        dom    = ET.parse(xml_path)
        xslt   = ET.parse(xsl_path)
        result = ET.XSLT(xslt)(dom)

        # Parse output as HTML and pull out <body> inner content.
        # Pass explicit UTF-8 parser so that IPA / special chars survive
        # (lxml's default HTML parser assumes ISO-8859-1 when there is no
        # charset meta tag, which turns UTF-8 bytes into mojibake).
        html_root = ET.HTML(bytes(result),
                            parser=ET.HTMLParser(encoding='utf-8'))
        if html_root is not None:
            body = html_root.find('.//body')
            if body is not None:
                parts = [body.text or '']
                for child in body:
                    parts.append(ET.tostring(child, encoding='unicode',
                                             method='html'))
                return ''.join(parts)

        return str(result)          # fallback: full page as-is
    except Exception as exc:
        return f'<pre class="text-danger">XSLT error ({stylesheet_name}):\n{exc}</pre>'


def compute_corr_freq(sets_path: str, corr_path: str):
    """Return a deep-copied corr ElementTree with freq stamped on every <corr> and <modern>.

    Each <corr freq="N"> carries row-level frequency (how many sets used that rule).
    Each <modern freq="N"> carries cell-level frequency (how many sets used that rule
    AND had a member from that dialect).
    """
    row_freq  = collections.Counter()   # corr_num -> count
    cell_freq = collections.Counter()   # (corr_num, dialect) -> count

    for s in ET.parse(sets_path).getroot().iter('set'):
        rcn_el = s.find('rcn')
        if rcn_el is None or not rcn_el.text:
            continue
        nums     = rcn_el.text.split()          # keep as strings — num values may be non-integer
        dialects = [lg.text for lg in s.findall('.//rfx/lg') if lg.text]
        row_freq.update(nums)
        for num in nums:
            cell_freq.update((num, d) for d in dialects)

    tree = copy.deepcopy(ET.parse(corr_path))
    for corr_el in tree.getroot().findall('corr'):
        num = corr_el.get('num', '')
        corr_el.set('freq', str(row_freq.get(num, 0)))
        for modern_el in corr_el.findall('modern'):
            dialect = modern_el.get('dialecte', '')
            modern_el.set('freq', str(cell_freq.get((num, dialect), 0)))
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
