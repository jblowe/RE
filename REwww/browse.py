"""REwww/browse.py – the Browse pane.

Lists the XML files in a project's directory, grouped by type, and renders a
chosen one with the standard stylesheet for its type. Only the project
directory itself is read (not its runs/ folder), and only .xml files.

A file's type comes from its root element, not from its name, so files named
in older ways (DIS.classes.xml, fromMM.xml, ...) are recognised too. An XML
file whose root is not one of the known ones is listed under "Other XML" and
shown as indented source. That includes class files (root <parameters>, e.g.
DIS.classes.xml): the one stylesheet named for parameters,
params2html-view.xsl, matches a different, older root (<params>).
"""

import html as _html
import os

import lxml.etree as ET

import browse_diff
import xslt


# (key, group label, root element, standard stylesheet, alternative views)
# Group order is the order of this list. A view is (key, label, stylesheet);
# the first view is the default and is the type's standard rendering.
TYPES = [
    ('toc',        'Tables of correspondences', 'tableOfCorr',    'toc2html-view.xsl',     []),
    ('lexicon',    'Lexicons',                  'lexicon',        'lexicon2html.xsl',
        [('paragraph', 'Paragraph', 'lexicon2html.xsl'),
         ('table',     'Table',     'lexicon2table.xsl')]),
    ('mel',        'MELs',                      'semantics',      'mel2html.xsl',          []),
    ('fuzzy',      'Fuzzy rules',               'fuzzy',          'fuzzy2html.xsl',        []),
    ('sets',       'Sets',                      'reconstruction', 'sets2html.xsl',
        [('paragraph', 'Paragraph', 'sets2html.xsl'),
         ('table',     'Table',     'sets2tabular.xsl')]),
]
OTHER_KEY   = 'other'
OTHER_LABEL = 'Other XML (shown as source)'

_BY_ROOT = {t[2]: t for t in TYPES}
_ORDER   = {t[0]: i for i, t in enumerate(TYPES)}
_ORDER[OTHER_KEY] = len(TYPES)

# Source view of unrecognised XML is cut off here, so a huge file cannot
# stall the browser.
MAX_SOURCE_CHARS = 1_000_000


def _root_name(path):
    """Local name of the file's root element, or None if it cannot be read
    as XML. Stops at the first element, so large files cost almost nothing."""
    try:
        for _event, el in ET.iterparse(path, events=('start',)):
            return ET.QName(el.tag).localname
    except (ET.XMLSyntaxError, OSError):
        return None
    return None


def _sets_views(path):
    """Isolates / failures views, offered only when the sets file has any."""
    try:
        root = ET.parse(path).getroot()
    except (ET.XMLSyntaxError, OSError):
        return []
    views = []
    if root.find('.//isolates/rfx') is not None:
        views.append(('isolates', 'Isolates', 'isolates2html.xsl'))
    if root.find('.//failures/rfx') is not None:
        views.append(('failures', 'Failures', 'failures2html.xsl'))
    return views


def classify(path):
    """(type key, group label, [view key/label dicts]) for an XML file."""
    root = _root_name(path)
    t = _BY_ROOT.get(root)
    if t is None:
        return OTHER_KEY, OTHER_LABEL, []
    key, label, _root, _xsl, views = t
    views = list(views)
    if key == 'sets':
        views += _sets_views(path)
    return key, label, [{'key': k, 'label': lab} for k, lab, _ in views]


def list_files(project_path):
    """The project directory's XML files, ordered by type and then name.

    Each entry: {name, type, group, size, views, diff}; diff is 'ready' if the
    file can be compared with an earlier commit, 'stub' if that is planned, or
    None (browse_diff.status).
    """
    entries = []
    try:
        names = os.listdir(project_path)
    except OSError:
        return []
    for name in names:
        full = os.path.join(project_path, name)
        if (name.startswith('.') or not name.lower().endswith('.xml')
                or not os.path.isfile(full)):
            continue
        key, group, views = classify(full)
        entries.append({'name': name, 'type': key, 'group': group,
                        'size': os.path.getsize(full), 'views': views,
                        'diff': browse_diff.status(key)})
    entries.sort(key=lambda e: (_ORDER[e['type']], e['name'].lower()))
    return entries


def resolve(project_path, name):
    """Absolute path of a listed file, or None.

    Only a bare file name directly inside the project directory is accepted:
    no sub-directories, no '..', nothing that resolves outside the project
    (symbolic links included), and only .xml files.
    """
    if (not name or os.path.basename(name) != name or name.startswith('.')
            or not name.lower().endswith('.xml')):
        return None
    root = os.path.realpath(project_path)
    full = os.path.realpath(os.path.join(project_path, name))
    if os.path.dirname(full) != root or not os.path.isfile(full):
        return None
    return full


def _source_html(path):
    try:
        text = ET.tostring(ET.parse(path), pretty_print=True,
                           encoding='unicode')
    except (ET.XMLSyntaxError, OSError) as exc:
        return (f'<p class="text-danger">Could not read '
                f'<code>{_html.escape(os.path.basename(path))}</code> as XML: '
                f'{_html.escape(str(exc))}</p>')
    note = ''
    if len(text) > MAX_SOURCE_CHARS:
        text = text[:MAX_SOURCE_CHARS]
        note = ('<p class="text-muted small">Shown up to the first '
                f'{MAX_SOURCE_CHARS:,} characters.</p>')
    return ('<p class="text-muted small">No stylesheet for this kind of XML; '
            'showing the source.</p>'
            f'{note}<pre class="browse-source">{_html.escape(text)}</pre>')


def render(path, view=None):
    """HTML for a file, from the standard stylesheet for its type.

    view picks one of the type's alternative views; an unknown or missing view
    gives the standard one.
    """
    key, _group, _views = classify(path)
    if key == OTHER_KEY:
        return _source_html(path)
    t = next(t for t in TYPES if t[0] == key)
    stylesheet = t[3]
    if key == 'sets':
        extra = {'isolates': 'isolates2html.xsl', 'failures': 'failures2html.xsl'}
        known = {k: s for k, _l, s in t[4]}
        known.update(extra)
        stylesheet = known.get(view, stylesheet)
    else:
        stylesheet = {k: s for k, _l, s in t[4]}.get(view, stylesheet)
    return xslt.xml_to_html(path, stylesheet)
