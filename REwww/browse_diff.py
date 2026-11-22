"""REwww/browse_diff.py – the Browse pane's "Compare local with an earlier commit".

Plumbing:  find the git repository a project file lives in, list the commits
that touched the file, and fetch the file as it was at one of them (plain local
git; no network).

Rendering:  DIFFERS maps a Browse file type (see browse.TYPES) to the function
that annotates the file with its differences (diff_<type>.py) and the stylesheet
that renders the annotated tree. A type listed in STUBS is planned but has no
differ yet. Adding a type = write its diff_<type>.annotate(old_root, new_root)
-> (annotated_root, summary), teach its stylesheet to render the `diff`
attributes, and add it to DIFFERS.

This module does not import browse.py (browse.py imports it).
"""

import html as _html
import os
import re
import shutil
import subprocess

import lxml.etree as ET

import diff_fuzzy
import diff_lexicon
import diff_mel
import diff_sets
import diff_toc
import xslt

# type key -> (annotate function, stylesheet, summary labels)
DIFFERS = {
    'toc': (diff_toc.annotate, 'toc2html-view.xsl',
            [('corr', 'correspondences'), ('seg', 'segments'),
             ('class', 'classes'), ('control', 'controls'),
             ('rule', 'rules'), ('quirk', 'exceptions')]),
    'fuzzy': (diff_fuzzy.annotate, 'fuzzy2html.xsl',
              [('item', 'fuzzy items'), ('from', 'input values')]),
    'mel': (diff_mel.annotate, 'mel2html.xsl',
            [('mel', 'MELs'), ('gl', 'glosses'), ('stat', 'statistics')]),
    'lexicon': (diff_lexicon.annotate, 'lexicon2table.xsl',
                [('entry', 'entries')]),
    'sets': (diff_sets.annotate, 'sets2tabular.xsl',
             [('set', 'sets'), ('member', 'members'), ('isolate', 'isolates'),
              ('failure', 'failures')]),
}
# Planned, not written yet (the dropdown is shown disabled for these).
STUBS = {}

COMMIT_LIMIT = 50
_SHA = re.compile(r'^[0-9a-f]{7,40}$')
_GIT_TIMEOUT = 20


def status(type_key):
    """'ready', 'stub', or None for a Browse file type."""
    if type_key in DIFFERS:
        return 'ready'
    if type_key in STUBS:
        return 'stub'
    return None


# ── git ───────────────────────────────────────────────────────────────────────

class DiffError(Exception):
    """A problem to show the user (not a bug)."""


def _git(repo, *args):
    git = shutil.which('git')
    if not git:
        raise DiffError('git was not found on this computer.')
    try:
        return subprocess.run(
            [git, '-c', 'core.quotepath=off', '-C', repo, *args],
            capture_output=True, timeout=_GIT_TIMEOUT, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise DiffError(f'git failed: {exc}')


def locate(path):
    """(repository root, path of the file inside it) for a tracked file.
    Raises DiffError if git is missing, the file is in no repository, or the
    file is not tracked.

    The in-repository path comes from git itself (run in the file's own
    directory), not from comparing path strings: that breaks when the clone's
    directory name differs in case from how projects.toml spells it."""
    here = os.path.dirname(os.path.abspath(path))
    name = os.path.basename(path)
    r = _git(here, 'rev-parse', '--show-toplevel')
    if r.returncode != 0:
        raise DiffError('This project is not in a git repository.')
    top = r.stdout.decode('utf-8', 'replace').strip()
    r = _git(here, 'ls-files', '--full-name', '--error-unmatch', '--', name)
    if r.returncode != 0:
        raise DiffError('This file is not tracked by git yet, so it has no history.')
    rel = r.stdout.decode('utf-8', 'replace').strip()
    return top, rel


def commits(path, limit=COMMIT_LIMIT):
    """Commits that touched the file, newest first: dicts with sha, short, date
    (YYYY-MM-DD), author, subject and path (the file's name at that commit, which
    differs from today's after a rename)."""
    top, rel = locate(path)
    r = _git(top, 'log', '--follow', '-n', str(limit), '--name-status',
             '--format=%x1e%H%x1f%h%x1f%aI%x1f%an%x1f%s', '--', rel)
    if r.returncode != 0:
        raise DiffError('git log failed: ' + r.stderr.decode('utf-8', 'replace').strip())
    out = []
    for chunk in r.stdout.decode('utf-8', 'replace').split('\x1e'):
        if not chunk.strip():
            continue
        head, _, rest = chunk.partition('\n')
        parts = head.split('\x1f')
        if len(parts) < 5:
            continue
        # "M<TAB>path", "A<TAB>path", "R100<TAB>old<TAB>new", "D<TAB>path"
        change = next((ln.split('\t') for ln in rest.splitlines() if ln.strip()), None)
        if change is None or change[0].startswith('D'):
            continue                    # no file at that commit (deleted or moved aside)
        out.append({'sha': parts[0], 'short': parts[1], 'date': parts[2][:10],
                    'author': parts[3], 'subject': parts[4],
                    'path': change[-1]})
    return out


def _old_tree_root(path, sha):
    """(commit dict, root element of the file as it was at that commit)."""
    if not _SHA.match(sha or ''):
        raise DiffError('Not a valid commit id.')
    top, _rel = locate(path)
    found = next((c for c in commits(path, limit=500)
                  if c['sha'].startswith(sha)), None)
    if found is None:
        raise DiffError('That commit did not touch this file (or is too old to list).')
    r = _git(top, 'show', f"{found['sha']}:{found['path']}")
    if r.returncode != 0:
        raise DiffError('The file does not exist at that commit.')
    try:
        return found, ET.fromstring(r.stdout)
    except ET.XMLSyntaxError as exc:
        raise DiffError(f'The file at {found["short"]} is not valid XML: {exc}')


# ── rendering ─────────────────────────────────────────────────────────────────

def _summary_html(summary, labels):
    parts = []
    for key, label in labels:
        s = summary.get(key) or {}
        bits = [f'{s[k]} {k}' for k in ('added', 'deleted', 'changed') if s.get(k)]
        if bits:
            parts.append(f'{label}: ' + ', '.join(bits))
    if not parts:
        return '<span class="text-success">No differences.</span>'
    return '; '.join(_html.escape(p) for p in parts)


def _check(type_key):
    """Raise DiffError unless type_key has a differ."""
    st = status(type_key)
    if st is None:
        raise DiffError('Diff is not available for this kind of file.')
    if st == 'stub':
        raise DiffError(f'Diff for {STUBS[type_key]} is not implemented yet.')


def _render(path, type_key, old_root, what):
    """The local file compared with old_root: a header (what is compared, legend,
    summary, close button) and the annotated rendering. `what` is the header's
    description of the old side (HTML, already escaped)."""
    annotate, stylesheet, labels = DIFFERS[type_key]
    try:
        new_root = ET.parse(path).getroot()
    except (ET.XMLSyntaxError, OSError) as exc:
        raise DiffError(f'Could not read {os.path.basename(path)} as XML: {exc}')
    annotated, summary = annotate(old_root, new_root)
    body = xslt.xml_to_html_from_tree(ET.ElementTree(annotated), stylesheet)
    esc = _html.escape
    header = (
        '<div id="browse-diff">'
        '<div class="diff-header">'
        f'<div><b>{esc(os.path.basename(path))}</b> compared with {what}</div>'
        '<div class="diff-legend">'
        '<span class="diff-added">added</span> '
        '<span class="diff-deleted">deleted</span> '
        '<span class="diff-changed">changed</span></div>'
        f'<div class="small">{_summary_html(summary, labels)}</div>'
        '<div class="diff-controls">'
        '<button type="button" class="btn btn-sm btn-outline-secondary" '
        'id="browse-diff-close">Close diff</button></div>'
        '</div>')
    return header + body + '</div>'


def render_diff(path, type_key, sha):
    """The local file compared with its version at commit sha."""
    _check(type_key)
    commit, old_root = _old_tree_root(path, sha)
    esc = _html.escape
    what = (f'<b>{esc(commit["short"])}</b> · {esc(commit["date"])} · '
            f'{esc(commit["author"])} · {esc(commit["subject"])}')
    return _render(path, type_key, old_root, what)


def render_diff_files(path, other_path, type_key):
    """The local file compared with another local file of the same type
    (the other file is the baseline: "added" means in `path` only)."""
    _check(type_key)
    try:
        old_root = ET.parse(other_path).getroot()
    except (ET.XMLSyntaxError, OSError) as exc:
        raise DiffError(f'Could not read {os.path.basename(other_path)} as XML: {exc}')
    what = f'<b>{_html.escape(os.path.basename(other_path))}</b> (local file)'
    return _render(path, type_key, old_root, what)
