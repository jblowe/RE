"""REwww/routes.py – Flask Blueprint: all HTTP route handlers."""

import copy
import html as _html
import os
import re as _re
import sys
import threading
import time
import traceback
import uuid
from types import SimpleNamespace

import lxml.etree as ET
from flask import (Blueprint, abort, jsonify, render_template,
                   request, Response)

import xslt
import projects as proj_module
import runlog
import run_compare
from utils import (find_candidates, spec_display, spec_for_storage,
                   read_protolanguage_from_correspondences,
                   list_attested_languages)

bp = Blueprint('main', __name__)

# ── In-memory run store  { run_id -> run_info dict } ──────────────────────────
_runs: dict = {}
_runs_lock  = threading.Lock()


# ── PROJECTS_TOML path (set by app.py after import) ───────────────────────────
PROJECTS_TOML: str = ''


# ── Upstream suggestion ────────────────────────────────────────────────────────

def _upstream_suggestion(project_path, project_name):
    """Return a suggested upstream string inferred from the project directory.

    Walks the project directory to find the first correspondences file,
    reads the proto-language name from it (falling back to the first four
    capitalised characters of the project name), then discovers the attested
    daughter-language codes from *.data.xml filenames.

    Returns a string of the form  "ProtoLg: Lg1, Lg2, ..., LgN"
    or an empty string if the project has no usable data.
    """
    try:
        recon_file = None
        for root_dir, _dirs, files in os.walk(project_path):
            for f in sorted(files):
                if f.endswith('correspondences.xml'):
                    recon_file = os.path.join(root_dir, f)
                    break
            if recon_file:
                break

        proto = read_protolanguage_from_correspondences(recon_file) if recon_file else None
        if not proto:
            proto = project_name.capitalize()[:4]

        langs = list_attested_languages(project_path)
        if langs:
            return f'{proto}: {", ".join(langs)}'
    except Exception:
        pass
    return ''


# ── Fuzzy annotation for ToC views ───────────────────────────────────────────

def _annotate_fuzzy(tree, fuzzy_path, fuzzy_cov_path=None):
    """Append <fuzz lang=… from=… to=… count=…/> children to matching <corr>
    elements in an lxml correspondence tree.

    Uses the coverage file (which carries actual usage counts per <from> rule)
    when available; falls back to the raw fuzzy file with count=0 for all rules.
    Both used (count>0) and defined-but-unused (count=0) rules are annotated so
    the XSLT can render distinct indicators for each.
    """
    # Choose source
    src = (fuzzy_cov_path if fuzzy_cov_path and os.path.isfile(fuzzy_cov_path)
           else fuzzy_path)
    if not src or not os.path.isfile(src):
        return tree

    try:
        fuz_root = ET.parse(src).getroot()
    except Exception:
        return tree

    # Build index: (lang, to_str) → {from_str: count}
    groups: dict = {}
    for item in fuz_root.iterfind('item'):
        lang   = item.get('dial', '')
        to_str = item.get('to',   '')
        if not lang or not to_str:
            continue
        for from_el in item.iterfind('from'):
            from_str = (from_el.text or '').strip()
            count    = int(from_el.get('uses', '0'))
            if from_str:
                groups.setdefault((lang, to_str), {})[from_str] = count

    if not groups:
        return tree

    # Annotate each <modern> element with <fuzz from count/> children —
    # one per from-form that maps to any of the cell's <seg> values.
    root = tree.getroot()
    for corr in root.iterfind('corr'):
        for modern in corr.iterfind('modern'):
            lang  = modern.get('dialecte', '')
            added: set = set()   # from_strs already appended to this <modern>
            for seg in modern.iterfind('seg'):
                to_str = (seg.text or '').strip()
                entries = groups.get((lang, to_str), {})
                # used (count>0) first, then unused, each group alphabetically
                for from_str, count in sorted(entries.items(),
                                              key=lambda kv: (0 if kv[1] > 0 else 1, kv[0])):
                    if from_str not in added:
                        added.add(from_str)
                        fuzz_el = ET.SubElement(modern, 'fuzz')
                        fuzz_el.set('to',    to_str)    # which seg this maps from
                        fuzz_el.set('from',  from_str)
                        fuzz_el.set('count', str(count))
    return tree


# ── Interactive process-pane HTML builder ────────────────────────────────────

def _failure_reason_class(reason):
    """Return the CSS class for a failure reason string."""
    if reason.startswith('Syllable canon:'):    return 'fail-syllable-canon'
    if reason.startswith('Syllable structure'): return 'fail-syllable-final'
    if 'word-final'  in reason:                return 'fail-word-final'
    if 'Panini'      in reason:                return 'fail-panini'
    if ': left context'  in reason:            return 'fail-left-context'
    if ': right context' in reason:            return 'fail-right-context'
    if reason.startswith('Constituent '):      return 'fail-constituent'
    if reason.startswith(('…', '...')):        return 'fail-more'
    return 'fail-constituent'   # safe default


def _parse_steps_str(steps_str):
    """Parse a steps string like  'char1' c4 + 'char2' c146  into [(char, corrId), …].

    Returns a list (possibly empty) or None if the format is unrecognised.
    """
    if not steps_str:
        return []
    result = []
    for part in steps_str.split(' + '):
        part = part.strip()
        if part in ("''", '""', ''):
            continue
        m = _re.match(r"^'(.+)'\s+(c\d+)$", part)
        if m:
            result.append((m.group(1), m.group(2)))
        else:
            return None   # unrecognised
    return result


def _render_parse_success_tree(parse_rows, esc):
    """Render successful parses as a parse-tree table.

    parse_rows – list of (rcn, proto, syll, steps_list) where steps_list
                 is [(char, corrId), …] or [] when step data is absent.

    Columns = one per parse position, then proto and syll.
    Common prefixes are dimmed so branching points stand out.
    Returns an HTML string or '' when nothing can be rendered.
    """
    structured = []
    for rcn, proto, syll, steps in parse_rows:
        if steps is None:
            steps = []
        structured.append(dict(steps=steps, proto=proto, syll=syll, rcn=rcn))

    if not structured:
        return ''

    # Sort by step path so shared prefixes are adjacent
    structured.sort(key=lambda r: tuple(r['steps']))

    max_cols = max((len(r['steps']) for r in structured), default=0)
    if max_cols == 0:
        return ''

    html = [
        '<table class="table table-sm table-bordered process-tree-table">',
        '<thead class="thead-light"><tr>',
    ]
    for col in range(max_cols):
        html.append(f'<th class="process-tree-pos-hdr">pos&nbsp;{col}</th>')
    html.append('<th style="font-size:.72em">proto</th>')
    html.append('<th style="font-size:.72em">syll</th>')
    html.append('</tr></thead><tbody>')

    prev_steps = []
    for r in structured:
        cur_steps = r['steps']
        html.append('<tr>')
        for col in range(max_cols):
            if col < len(cur_steps):
                char, cid = cur_steps[col]
                shared = (
                    col < len(prev_steps) and
                    prev_steps[col] == cur_steps[col] and
                    prev_steps[:col] == cur_steps[:col]
                )
                if shared:
                    html.append(
                        f'<td class="process-tree-shared">'
                        f'<code>{esc(char)}</code> {esc(cid)}'
                        f'</td>'
                    )
                else:
                    html.append(
                        f'<td class="process-tree-step">'
                        f'<code>{esc(char)}</code>'
                        f' <a class="rcn-link" href="#"'
                        f' data-corr-id="{esc(cid)}">{esc(cid)}</a>'
                        f'</td>'
                    )
            else:
                html.append('<td></td>')

        html.append(f'<td style="font-size:.82em">*{esc(r["proto"])}</td>')
        if r['syll']:
            html.append(
                f'<td><span class="badge badge-secondary"'
                f' style="font-size:.7em">{esc(r["syll"])}</span></td>'
            )
        else:
            html.append('<td></td>')
        html.append('</tr>')
        prev_steps = cur_steps

    html.append('</tbody></table>')
    return '\n'.join(html)


def _parse_failure_for_tree(msg):
    """Parse a structured failure message into tree-table components.

    Recognised format (built by _context_desc / gen()):
        {left_steps} + {failing_ids} '{char}' + '{right}' : {desc}
    where left_steps is zero or more  'char' cN  terms joined by ' + '.

    Returns a dict on success:
      steps        – [(char_text, corr_id), …]   — left-side parse steps
      failing_ids  – [corr_id, …]                — IDs of blocked correspondences
      failing_char – str or None                 — actual character tried
      right        – str                         — remaining unconsumed form
      desc         – str                         — context failure description
    Returns None when the message is not in the expected format (syllable
    canon, Constituent not found, Panini, etc.) — those are rendered as
    spanning flat rows in the table.
    """
    if ' + ' not in msg or ' : ' not in msg:
        return None
    colon_idx = msg.rfind(' : ')
    if colon_idx < 0:
        return None
    before = msg[:colon_idx]
    desc   = msg[colon_idx + 3:]

    parts = before.split(' + ')
    if len(parts) < 2:
        return None

    steps        = []
    failing_ids  = []
    failing_char = None
    right        = None

    for i, raw in enumerate(parts):
        part    = raw.strip()
        is_last = (i == len(parts) - 1)

        if is_last:
            # Last segment is the right-side quoted text
            if part in ("''", '""', ''):
                right = ''
            elif part.startswith("'") and part.endswith("'"):
                right = part[1:-1]
            else:
                right = part
            continue

        # Empty '' = start-of-form marker; no step
        if part in ("''", '""', ''):
            continue

        # Left step: 'char' cN
        m = _re.match(r"^'(.+)'\s+(c\d+)$", part)
        if m:
            steps.append((m.group(1), m.group(2)))
            continue

        # Failing element: cN1, cN2, … 'char'
        m = _re.match(r"^(c\d+(?:,\s*c\d+)*)\s+'(.*)'$", part)
        if m:
            failing_ids  = [x.strip() for x in m.group(1).split(',')]
            failing_char = m.group(2)
            continue

        return None   # unrecognised segment

    if right is None:
        return None

    return dict(steps=steps, failing_ids=failing_ids,
                failing_char=failing_char, right=right, desc=desc)


def _render_tree_table(depth_reasons, esc):
    """Build an HTML parse-tree table from all-depths failure data.

    Layout: one column per parse position (0 … max_depth), spreading left
    to right; one row per unique parse path.  The failing element is
    highlighted; cells that repeat the same prefix as the row above are
    shown in muted grey so the branching point is visually obvious.
    Unstructured messages (syllable canon, Panini, etc.) are appended as
    full-width spanning rows below the tree rows.

    Returns an HTML string, or '' if there is nothing to render.
    """
    if not depth_reasons:
        return ''

    parsed_rows = []   # structured context / word-final paths
    raw_rows    = []   # everything else (syllable, not-found, etc.)

    for pos in sorted(depth_reasons.keys()):
        for msg in depth_reasons[pos]:
            p = _parse_failure_for_tree(msg)
            if p:
                parsed_rows.append(dict(pos=pos, raw=msg, **p))
            else:
                raw_rows.append(dict(pos=pos, raw=msg))

    if not parsed_rows and not raw_rows:
        return ''

    # Sort parsed rows so paths with a common prefix appear adjacent,
    # producing a visually coherent left-to-right tree.
    parsed_rows.sort(key=lambda r: tuple(r['steps']))

    # Number of position columns = deepest path + 1 (for the failing column)
    max_cols = max(
        (len(r['steps']) + (1 if r['failing_ids'] or r['failing_char'] is not None else 0)
         for r in parsed_rows),
        default=0,
    )
    if max_cols == 0 and not raw_rows:
        return ''
    max_cols = max(max_cols, 1)

    html = [
        '<table class="table table-sm table-bordered process-tree-table">',
        '<thead class="thead-light"><tr>',
    ]
    for col in range(max_cols):
        html.append(
            f'<th class="process-tree-pos-hdr">pos&nbsp;{col}</th>'
        )
    html.append('<th style="font-size:.72em">Reason</th>')
    html.append('</tr></thead><tbody>')

    prev_steps = []
    for r in parsed_rows:
        cur_steps = r['steps']
        html.append('<tr>')

        for col in range(max_cols):
            if col < len(cur_steps):
                char, cid = cur_steps[col]
                # Dim the cell when this step is the same as the row above
                # AND the entire prefix up to col is identical (= shared path).
                shared = (
                    col < len(prev_steps) and
                    prev_steps[col] == cur_steps[col] and
                    prev_steps[:col] == cur_steps[:col]
                )
                if shared:
                    html.append(
                        f'<td class="process-tree-shared">'
                        f'<code>{esc(char)}</code>'
                        f' {esc(cid)}'
                        f'</td>'
                    )
                else:
                    html.append(
                        f'<td class="process-tree-step">'
                        f'<code>{esc(char)}</code>'
                        f' <a class="rcn-link" href="#"'
                        f' data-corr-id="{esc(cid)}">{esc(cid)}</a>'
                        f'</td>'
                    )

            elif col == len(cur_steps) and (r['failing_ids'] or
                                             r['failing_char'] is not None):
                # The failing element at this position
                ids_html = ', '.join(
                    f'<a class="rcn-link" href="#"'
                    f' data-corr-id="{esc(c)}">{esc(c)}</a>'
                    for c in r['failing_ids']
                )
                char_part = (f'&nbsp;<code>{esc(r["failing_char"])}</code>'
                             if r['failing_char'] else '')
                html.append(
                    f'<td class="process-tree-fail">'
                    f'{ids_html}{char_part}</td>'
                )
            else:
                html.append('<td></td>')

        cls = _failure_reason_class(r['raw'])
        html.append(
            f'<td><span class="iso-badge iso-fail-reason {cls}"'
            f' style="font-size:.78em;white-space:normal">'
            f'{esc(r["desc"])}</span></td>'
        )
        html.append('</tr>')
        prev_steps = cur_steps

    # Flat rows for unstructured messages (syllable canon, Panini, etc.)
    for r in raw_rows:
        cls = _failure_reason_class(r['raw'])
        html.append(
            f'<tr><td colspan="{max_cols + 1}">'
            f'<span class="iso-badge iso-fail-reason {cls}">'
            f'{esc(r["raw"])}</span></td></tr>'
        )

    html.append('</tbody></table>')
    return '\n'.join(html)


def _build_process_html(debug_notes, notes, failed_parses=None):
    """Build HTML for the Interactive Process pane.

    debug_notes / notes come from B.statistics.
    failed_parses is B.failures (list of ModernForm objects with .failure_reasons).
    Failure reasons are shown as a depth-grouped table beneath each failed form.
    """
    import html as _html
    esc = _html.escape

    # (language, glyphs) → all-depths {pos: [reasons]} for the full tree table.
    # Falls back to the deepest-only flat list when all_failure_reasons is absent.
    all_fail_map  = {}
    flat_fail_map = {}
    for form in (failed_parses or []):
        key = (form.language, form.glyphs)
        if key not in all_fail_map:
            all_fail_map[key]  = getattr(form, 'all_failure_reasons', None) or {}
            flat_fail_map[key] = form.failure_reasons or []

    n_parsing = sum(1 for n in debug_notes if n.startswith('!Parsing '))
    parts = ['<div class="interactive-process-body">']
    if not n_parsing:
        parts.append('<p class="text-warning small">No per-form debug notes collected.</p>')

    # Mutable state accumulated across notes
    cur = {'lang': None, 'glyphs': None, 'gloss': None, 'parses': []}

    def flush():
        if cur['lang'] is None:
            return
        label = f'<strong>{esc(cur["lang"])}</strong> {esc(cur["glyphs"])}'
        if cur['gloss']:
            label += f' <em class="text-secondary">{esc(cur["gloss"])}</em>'
        parts.append(
            f'<div class="process-form-block">'
            f'<div class="process-form-label">{label}</div>'
        )
        if cur['parses']:
            # Separate successful parses (with step data) from failed attempts
            success_rows = [(rcn, proto, syll, steps)
                            for (rcn, proto, syll, success, steps) in cur['parses']
                            if success]
            failed_rows  = [(rcn, proto, syll)
                            for (rcn, proto, syll, success, steps) in cur['parses']
                            if not success]
            tree_html = _render_parse_success_tree(success_rows, esc)
            if tree_html:
                parts.append(tree_html)
            else:
                # Fallback: flat table (no step data available)
                parts.append(
                    '<table class="table table-sm table-bordered process-parse-table">'
                    '<thead class="thead-light"><tr>'
                    '<th style="width:30%">Reflex</th>'
                    '<th style="width:40%">rcn</th>'
                    '<th>Reconstruction</th>'
                    '</tr></thead><tbody>'
                )
                for (rcn, proto, syll, _steps) in success_rows:
                    recon = f'*{esc(proto)}'
                    if syll:
                        recon += (f' <span class="badge badge-secondary"'
                                  f' style="font-size:.7em">{esc(syll)}</span>')
                    parts.append(
                        f'<tr>'
                        f'<td>{esc(cur["glyphs"])}</td>'
                        f'<td><code style="font-size:.85em">{esc(rcn)}</code></td>'
                        f'<td>{recon}</td>'
                        f'</tr>'
                    )
                parts.append('</tbody></table>')
            # Failed attempts (xx notes) below the success tree, if any
            if failed_rows:
                parts.append(
                    '<table class="table table-sm table-bordered process-parse-table'
                    ' text-muted" style="margin-top:.25rem">'
                    '<thead class="thead-light"><tr>'
                    '<th colspan="3" style="font-size:.75em">Attempted but failed</th>'
                    '</tr><tr>'
                    '<th style="width:30%">Reflex</th>'
                    '<th style="width:40%">rcn</th>'
                    '<th>proto</th>'
                    '</tr></thead><tbody>'
                )
                for (rcn, proto, syll) in failed_rows:
                    recon = f'{esc(proto)}'
                    if syll:
                        recon += (f' <span class="badge badge-secondary"'
                                  f' style="font-size:.7em">{esc(syll)}</span>')
                    parts.append(
                        f'<tr>'
                        f'<td>{esc(cur["glyphs"])}</td>'
                        f'<td><code style="font-size:.85em">{esc(rcn)}</code></td>'
                        f'<td>{recon}</td>'
                        f'</tr>'
                    )
                parts.append('</tbody></table>')
        else:
            # No parses — render the parse-tree table.
            key        = (cur['lang'], cur['glyphs'])
            all_depths = all_fail_map.get(key, {})
            flat       = flat_fail_map.get(key, [])
            # Prefer the rich all-depths data; fall back to the deepest-only list
            reasons_by_depth = all_depths or ({0: flat} if flat else {})
            tree_html = _render_tree_table(reasons_by_depth, esc)
            if tree_html:
                parts.append(tree_html)
            elif reasons_by_depth:
                # Fallback: simple flat list when tree rendering produces nothing
                parts.append(
                    '<table class="table table-sm table-bordered process-parse-table">'
                    '<thead class="thead-light"><tr><th>Reason</th></tr></thead><tbody>'
                )
                for pos in sorted(reasons_by_depth.keys(), reverse=True):
                    for r in reasons_by_depth[pos]:
                        cls = _failure_reason_class(r)
                        parts.append(
                            f'<tr><td>'
                            f'<span class="iso-badge iso-fail-reason {cls}">{esc(r)}</span>'
                            f'</td></tr>'
                        )
                parts.append('</tbody></table>')
        parts.append('</div>')
        cur['lang'] = None
        cur['parses'] = []

    for note in debug_notes:
        if note.startswith('!Parsing '):
            flush()
            form_str = note[len('!Parsing '):]
            if form_str.endswith('...'):
                form_str = form_str[:-3]
            tab_parts   = form_str.split('\t')
            lang_glyphs = tab_parts[0].strip()
            cur['gloss'] = tab_parts[1].strip() if len(tab_parts) > 1 else ''
            sp = lang_glyphs.find(' ')
            cur['lang']   = lang_glyphs[:sp]   if sp > 0 else lang_glyphs
            cur['glyphs'] = lang_glyphs[sp+1:] if sp > 0 else ''
            cur['parses'] = []

        elif note.startswith(' *'):
            content = note[2:]
            # Steps breakdown appended after a tab: "proto - rcn syll\tstep_str"
            steps_str = None
            if '\t' in content:
                content, steps_str = content.split('\t', 1)
            if ' - ' in content:
                proto, rest = content.split(' - ', 1)
                toks = rest.rsplit(None, 1)
                rcn  = toks[0].strip() if len(toks) == 2 else rest.strip()
                syll = toks[1]          if len(toks) == 2 else ''
                steps = _parse_steps_str(steps_str) if steps_str else []
                cur['parses'].append((rcn, proto, syll, True, steps))

        elif note.startswith(' xx '):
            content = note[4:]
            if ' - ' in content:
                proto, rest = content.split(' - ', 1)
                toks = rest.rsplit(None, 1)
                rcn  = toks[0].strip() if len(toks) == 2 else rest.strip()
                syll = toks[1]          if len(toks) == 2 else ''
                cur['parses'].append((rcn, proto, syll, False, None))

    flush()

    # ── Summary notes ──────────────────────────────────────────────────────────
    if notes:
        parts.append(
            '<hr class="my-2">'
            '<div class="process-summary">'
            '<strong class="small">Summary</strong>'
            '<ul class="list-unstyled small mt-1 mb-0">'
        )
        for n in notes:
            parts.append(f'<li>{esc(n)}</li>')
        parts.append('</ul></div>')

    parts.append('</div>')
    return '\n'.join(parts)


# ── Canvas test page ───────────────────────────────────────────────────────────

@bp.route('/canvas-test')
def canvas_test():
    projects = sorted(proj_module.projects.keys())
    return render_template('canvas_test.html', projects=projects)

@bp.route('/api/canvas_nodes/<project>')
def canvas_nodes_api(project):
    import re, glob
    path = proj_module.projects.get(project)
    if not path:
        return jsonify(error='project not found'), 404
    corr_re = re.compile(r'[^.]+\.(.+?)\.correspondences\.xml$')
    data_re = re.compile(r'[^.]+\.(.+?)\.data\.xml$')
    protos  = sorted(m.group(1) for f in glob.glob(os.path.join(path, '*.correspondences.xml'))
                     if (m := corr_re.search(os.path.basename(f))))
    leaves  = sorted(m.group(1) for f in glob.glob(os.path.join(path, '*.data.xml'))
                     if (m := data_re.search(os.path.basename(f))))
    return jsonify(protos=protos, leaves=leaves)

# ── Main page ──────────────────────────────────────────────────────────────────

@bp.route('/')
def index():
    all_projects = proj_module.projects
    project_data = {}
    for name, path in all_projects.items():
        if not os.path.isdir(path):
            continue
        project_data[name] = {
            'path':               path,
            'recons':             find_candidates(path, 'correspondences.xml'),
            'mels':               find_candidates(path, 'mel.xml'),
            'fuzzies':            find_candidates(path, 'fuz.xml'),
            'upstream_suggestion': _upstream_suggestion(path, name),
        }
    history_counts = {name: runlog.count_runs(name) for name in project_data}
    return render_template('index.html',
                           project_data=project_data,
                           history_counts=history_counts)


# ── Project file-list refresh ──────────────────────────────────────────────────

@bp.route('/api/projects')
def api_projects():
    """Return current project file candidates as JSON (used by the Refresh button)."""
    proj_module.projects = proj_module.get_dirs('projects')
    data = {}
    for name, path in proj_module.projects.items():
        if not os.path.isdir(path):
            continue
        data[name] = {
            'path':               path,
            'recons':             find_candidates(path, 'correspondences.xml'),
            'mels':               find_candidates(path, 'mel.xml'),
            'fuzzies':            find_candidates(path, 'fuz.xml'),
            'history_count':      runlog.count_runs(name),
            'upstream_suggestion': _upstream_suggestion(path, name),
        }
    return jsonify(data)


# ── Start an upstream run ──────────────────────────────────────────────────────

@bp.route('/api/run', methods=['POST'])
def api_run():
    """Start an upstream run.  Returns { run_id, run_name }."""
    import RE, read, serialize, load_hooks

    body               = request.get_json(force=True)
    project            = body.get('project')
    recon              = body.get('recon') or None
    mel                = body.get('mel')   or None
    fuzzy              = body.get('fuzzy') or None
    upstream           = body.get('upstream') or None

    if project == 'ROMANCE':
        recon = None

    if project not in proj_module.projects:
        return jsonify(error=f'Unknown project: {project}'), 400

    project_path = proj_module.projects[project]
    run_name     = time.strftime('%Y%m%d-%H%M%S')
    run_id       = str(uuid.uuid4())

    run_info = {
        'id':       run_id,
        'project':  project,
        'run_name': run_name,
        'status':   'running',
        'log':      [],
        'files':    {},
        'error':    None,
    }
    with _runs_lock:
        _runs[run_id] = run_info

    def do_run():
        log = run_info['log']

        class _Tee:
            def __init__(self, orig):
                self._orig = orig
            def write(self, s):
                if s.strip():
                    log.append(s.rstrip())
                return self._orig.write(s)
            def flush(self):
                self._orig.flush()

        old_stdout = sys.stdout
        sys.stdout = _Tee(old_stdout)
        try:
            runs_dir = os.path.join(project_path, 'runs')
            os.makedirs(runs_dir, exist_ok=True)

            load_hooks.load_hook(project_path)
            settings = read.read_settings(
                project_path, project, recon,
                mel_token=mel, fuzzy_token=fuzzy, upstream=upstream)

            run_info['run_params'] = {
                'recon': recon, 'mel': mel, 'fuzzy': fuzzy, 'upstream': upstream,
            }

            # Attach syllable_canon to settings so it is available for
            # logging and serialize_stats.  ProjectSettings doesn't hold it;
            # we read the upstream-target correspondences file to get it.
            try:
                _recon_path = os.path.join(
                    settings.directory_path,
                    settings.proto_languages[settings.upstream_target])
                _params = read.read_correspondence_file(
                    _recon_path, settings.upstream_target,
                    None, None)
                settings.syllable_canon = _params.syllable_canon
            except Exception:
                pass

            try:
                sc = settings.syllable_canon
                run_info['context_match_type'] = sc.context_match_type
                run_info['spec'] = spec_for_storage(sc)
                print(f'context_match_type: {sc.context_match_type}')
                print(f'spec (supra_segmentals): {run_info["spec"]}')
            except Exception:
                pass

            B = RE.upstream(settings, only_with_mel=True)

            _isolates_dict = RE.extract_isolates(B)
            B.isolates_dict = _isolates_dict
            B.isolates = sorted(
                _isolates_dict.keys(), key=lambda x: x.language)
            B.failures = sorted(
                B.statistics.failed_parses, key=lambda x: x.language)

            # Annotate each isolate form with a human-readable reason string
            # so the serializer can write a <reason> element into sets.xml.
            #
            # Three independent facts are concatenated:
            #
            # 1. Set membership (raw, pre-MEL groupings):
            #    "Found in a set"    — rcn shared by forms from >1 language
            #    "Not found in a set" — rcn is unique to one language
            #
            #    We must include BOTH real-set protoforms (B.forms) AND
            #    singleton protoforms (B.statistics.singleton_support) when
            #    building the raw groupings, because two isolates from
            #    different languages with the same rcn together constitute a
            #    raw set even though MEL filtering left them both as singletons.
            #
            # 2. MEL matching:
            #    "Matched a MEL"  — the form's singleton reconstruction is
            #                       associated with a real MEL (glosses != [])
            #    "No MEL found"   — no MEL entry was matched
            #
            # 3. Semantic exclusion (only when 1 AND 2 are both positive):
            #    "Excluded by semantics" — form was in a raw multi-language
            #    set AND matched a MEL, but the MEL group it fell into had
            #    only one language, so semantics split it off from the set.

            # Build: rcn → set of languages across ALL reconstructions
            # (real sets + singletons = the full raw grouping before MEL).
            _raw_rcn_langs = {}
            for _pf in B.forms:
                _rcn_str = RE.correspondences_as_ids(_pf.correspondences).strip()
                for _af in _pf.attested_support:
                    _raw_rcn_langs.setdefault(_rcn_str, set()).add(_af.language)
            for (_corr, _sf, _att, _mel) in B.statistics.singleton_support:
                _rcn_str = RE.correspondences_as_ids(_corr).strip()
                for _af in _att:
                    _raw_rcn_langs.setdefault(_rcn_str, set()).add(_af.language)

            for _form, _proto_forms in _isolates_dict.items():
                _reasons = []
                _has_mel = any(
                    pf.mel and getattr(pf.mel, 'glosses', None)
                    for pf in _proto_forms)
                _found_in_set = bool(_proto_forms) and any(
                    len(_raw_rcn_langs.get(
                        RE.correspondences_as_ids(pf.correspondences).strip(),
                        set())) > 1
                    for pf in _proto_forms)

                # 1. Set membership
                _reasons.append('Found in a set' if _found_in_set
                                 else 'Not found in a set')
                # 2. MEL matching
                _reasons.append('Matched a MEL' if _has_mel
                                 else 'No MEL found')
                # 3. Semantic exclusion (only when both 1 and 2 hold)
                if _found_in_set and _has_mel:
                    _reasons.append('Excluded by semantics')

                _form._isolate_reason = ', '.join(_reasons)

            sets_xml = os.path.join(
                runs_dir, f'{project}.{run_name}.sets.xml')
            intermediate_pls = [pl for pl in settings.proto_languages if pl != settings.upstream_target]
            all_languages = intermediate_pls + list(settings.attested.keys())
            B.mel_used = getattr(settings, 'mel_filename', None) is not None
            RE.dump_xml_sets(
                B, all_languages,
                sets_xml, True)

            # Unique cognate sets = deduplicated by supporting_forms, matching
            # what create_xml_sets actually writes (merging multi-reconstruction sets).
            unique_sfs  = {pf.supporting_forms for pf in B.forms}
            unique_sets = len(unique_sfs)
            total_reflexes = sum(len(sf) for sf in unique_sfs)
            B.statistics.add_stat('isolates', len(B.isolates))
            B.statistics.add_stat('failure',  len(B.failures))
            B.statistics.add_stat('sets',     unique_sets)
            B.statistics.add_stat('reflexes', total_reflexes)

            # Enrich per-language stats with isolates and in-sets counts.
            # Build fast lookup dicts before touching language_stats.
            _iso_by_lang = {}
            for _f in B.isolates:
                _iso_by_lang[_f.language] = _iso_by_lang.get(_f.language, 0) + 1
            _in_sets_by_lang = {}
            for _sf in unique_sfs:
                for _f in _sf:
                    _in_sets_by_lang[_f.language] = _in_sets_by_lang.get(_f.language, 0) + 1
            for _lang, _ls in B.statistics.language_stats.items():
                _iso  = _iso_by_lang.get(_lang, 0)
                _in_s = _in_sets_by_lang.get(_lang, 0)
                # Rebuild in desired column order: forms | failures | isolates | in_sets | reconstructions
                B.statistics.language_stats[_lang] = {
                    'forms':           _ls.get('forms', 0),
                    'no_parses':       _ls.get('no_parses', 0),
                    'isolates':        _iso,
                    'in_sets':         _in_s,
                    'reconstructions': _ls.get('reconstructions', 0),
                }

            stats_xml = os.path.join(
                runs_dir,
                f'{project}.{run_name}.upstream.statistics.xml')

            args_ns = SimpleNamespace(
                run=run_name, project=project, project_path=project_path,
                recon=recon, mel=mel, fuzzy=fuzzy, upstream=upstream,
                only_with_mel=True)
            serialize.serialize_stats(
                B.statistics, settings, args_ns, stats_xml)

            mel_path   = getattr(settings, 'mel_filename',   None)
            fuzzy_path = getattr(settings, 'fuzzy_filename', None)

            coverage_xml = None
            if mel_path and os.path.isfile(mel_path):
                import coverage as re_coverage
                # Reuses the mels/attested_lexicons/associated_mels_table
                # already computed for this run (stashed on B.statistics by
                # RE.upstream) -- no re-read, no re-normalizing, and
                # the annotated per-MEL/per-language table is assembled here
                # once rather than rebuilt on every Coverage-tab request.
                cov_stats = re_coverage.build_coverage_statistics(
                    B.statistics.mels, B.statistics.attested_lexicons,
                    B.statistics.associated_mels_table, all_languages, B)
                coverage_xml = os.path.join(
                    runs_dir, f'{project}.{run_name}.coverage.xml')
                serialize.serialize_stats(cov_stats, settings, args_ns, coverage_xml)

            fuzzy_cov_xml = None
            if fuzzy_path and os.path.isfile(fuzzy_path):
                fuzzy_cov_xml = os.path.join(
                    runs_dir, f'{project}.{run_name}.fuzzy_cov.xml')
                serialize.serialize_fuzzy_coverage(
                    fuzzy_path, B.statistics.fuzzy_usage, fuzzy_cov_xml)

            # ── Write run log to disk ─────────────────────────────────────
            log_txt = os.path.join(
                runs_dir, f'{project}.{run_name}.log.txt')
            try:
                with open(log_txt, 'w', encoding='utf-8') as fh:
                    fh.write('\n'.join(run_info['log']))
            except OSError:
                log_txt = None

            run_info['files'] = {
                'sets':     sets_xml,
                'stats':    stats_xml,
                'log':      log_txt,
                'recon':    list(settings.proto_languages.values()),
                'data':     {lg: os.path.join(settings.directory_path, p)
                             for lg, p in settings.attested.items()},
                'mel':      mel_path     if mel_path     and os.path.isfile(mel_path)     else None,
                'fuzzy':     fuzzy_path    if fuzzy_path    and os.path.isfile(fuzzy_path)    else None,
                'fuzzy_cov': fuzzy_cov_xml if fuzzy_cov_xml and os.path.isfile(fuzzy_cov_xml) else None,
                'coverage':  coverage_xml  if coverage_xml  and os.path.isfile(coverage_xml)  else None,
            }
            run_info['status'] = 'done'

            # ── Persist to runs.toml ──────────────────────────────────────
            try:
                runlog.append_run({
                    'run_id':       run_id,
                    'project':      project,
                    'run_name':     run_name,
                    'sets':         unique_sets,
                    'isolates':     len(B.isolates),
                    'failures':     len(B.failures),
                    'has_coverage': bool(run_info['files'].get('coverage')),
                    'params': {
                        'recon':              recon    or '',
                        'mel':                mel      or '',
                        'fuzzy':              fuzzy    or '',
                        'upstream':           upstream or '',
                        'context_match_type': run_info.get('context_match_type', ''),
                        'spec':               run_info.get('spec', ''),
                    },
                    'files': {
                        'sets':     sets_xml  or '',
                        'stats':    stats_xml or '',
                        'log':      log_txt   or '',
                        'mel':       run_info['files'].get('mel')       or '',
                        'fuzzy':     run_info['files'].get('fuzzy')     or '',
                        'fuzzy_cov': run_info['files'].get('fuzzy_cov') or '',
                        'coverage':  run_info['files'].get('coverage')  or '',
                        'recon':     run_info['files'].get('recon')     or [],
                        'data':      dict(run_info['files'].get('data') or {}),
                    },
                })
            except Exception:
                pass  # log errors must not abort the run

        except Exception:
            run_info['error']  = traceback.format_exc()
            run_info['status'] = 'error'
        finally:
            sys.stdout = old_stdout

    threading.Thread(target=do_run, daemon=True).start()
    return jsonify(
        run_id   = run_id,
        run_name = run_name,
        recon    = recon,
        mel      = mel,
        fuzzy    = fuzzy,
        upstream = upstream,
    )


# ── Poll run status ────────────────────────────────────────────────────────────

@bp.route('/api/poll/<run_id>')
def api_poll(run_id):
    with _runs_lock:
        r = _runs.get(run_id)
    if r is None:
        return jsonify(error='unknown run'), 404
    done = r['status'] == 'done'
    return jsonify(
        status              = r['status'],
        log                 = r['log'],
        error               = r['error'],
        has_mel             = bool(r['files'].get('mel'))      if done else None,
        has_fuzzy           = bool(r['files'].get('fuzzy'))    if done else None,
        has_coverage        = bool(r['files'].get('coverage')) if done else None,
        context_match_type  = r.get('context_match_type', '') if done else None,
        spec                = r.get('spec', '')               if done else None,
    )


# ── Lexicon language list ──────────────────────────────────────────────────────

@bp.route('/api/lexicon_langs/<run_id>')
def api_lexicon_langs(run_id):
    """Return the sorted list of languages available for a completed run."""
    with _runs_lock:
        r = _runs.get(run_id)
    if r is None:
        return jsonify(error='unknown run'), 404
    languages = sorted(r['files'].get('data', {}).keys())
    return jsonify(languages=languages)


# ── Tab content ────────────────────────────────────────────────────────────────

@bp.route('/api/tab/<run_id>/<tab>')
def api_tab(run_id, tab):
    with _runs_lock:
        r = _runs.get(run_id)
    if r is None:
        return '<p class="text-danger">Run not found.</p>', 404
    if r['status'] != 'done':
        return '<p class="text-muted">Run not complete.</p>'

    mode  = request.args.get('mode', 'paragraph')
    files = r['files']

    if tab == 'sets':
        ss = 'sets2html.xsl' if mode == 'paragraph' else 'sets2tabular.xsl'
        lazy = request.args.get('lazy', '0')
        params = {'lazy': lazy} if lazy == '1' else None
        return xslt.xml_to_html(files['sets'], ss, params)

    if tab in ('isolates', 'failures'):
        sets_file = files.get('sets')
        if not sets_file or not os.path.isfile(sets_file):
            return '<p class="text-muted">No sets file found.</p>'
        ss = 'isolates2html.xsl' if tab == 'isolates' else 'failures2html.xsl'
        return xslt.xml_to_html(sets_file, ss)

    if tab == 'stats':
        return xslt.xml_to_html(files['stats'], 'stats2html.xsl')

    if tab == 'parameters':
        recon_files = files.get('recon', [])
        if not recon_files:
            return '<p class="text-muted">No correspondences files.</p>'

        if mode == 'freq':
            sets_file = files.get('sets')
            if not sets_file or not os.path.isfile(sets_file):
                return '<p class="text-muted">No sets file found — run the project first.</p>'
            annotated = xslt.compute_corr_freq(sets_file, recon_files[0])
            fuz_path_f = files.get('fuzzy')
            if fuz_path_f and os.path.isfile(fuz_path_f):
                _annotate_fuzzy(annotated, fuz_path_f, files.get('fuzzy_cov'))
            html = xslt.xml_to_html_from_tree(annotated, 'toc2html-freq.xsl')
            fuz_path = files.get('fuzzy')
            if fuz_path and os.path.isfile(fuz_path):
                fuz_cov = files.get('fuzzy_cov')
                view_path = fuz_cov if fuz_cov and os.path.isfile(fuz_cov) else fuz_path
                fuzzy_html = xslt.xml_to_html(view_path, 'fuzzy2html.xsl')
                html += (
                    '<button type="button" class="params-sec-hdr collapsed"'
                    ' data-bs-toggle="collapse" data-bs-target="#params-fuzzy-sec"'
                    ' aria-expanded="false">Fuzzy</button>'
                    '<div class="collapse" id="params-fuzzy-sec">' + fuzzy_html + '</div>'
                )
            return html

        if mode == 'edit':
            recon_file = recon_files[0]
            label = os.path.basename(recon_file)
            note = ''
            if len(recon_files) > 1:
                note = (
                    f'<p class="alert alert-info py-1 px-2 small mb-2">'
                    f'<i class="fas fa-info-circle mr-1"></i>'
                    f'Editing <strong>{label}</strong> '
                    f'(1 of {len(recon_files)} files). '
                    f'Save and re-run to edit others.</p>'
                )
            html = xslt.xml_to_html(recon_file, 'toc2html-edit.xsl')
            return f'{note}<div data-recon-file="{recon_file}">{html}</div>'

        fuz_path_v = files.get('fuzzy')
        use_subpanes = request.args.get('subpanes') and len(recon_files) > 1

        if use_subpanes:
            # Bootstrap tab per correspondences file (used in the Research pane)
            nav_items, pane_items = [], []
            for i, recon_file in enumerate(recon_files):
                label    = _html.escape(os.path.basename(recon_file))
                pane_id  = f'research-corr-pane-{i}'
                active   = 'active' if i == 0 else ''
                show     = 'show'   if i == 0 else ''
                selected = 'true'   if i == 0 else 'false'
                nav_items.append(
                    f'<li class="nav-item" role="presentation">'
                    f'<button class="nav-link {active}" id="research-corr-tab-{i}"'
                    f' data-bs-toggle="tab" data-bs-target="#{pane_id}"'
                    f' type="button" role="tab" aria-selected="{selected}">'
                    f'{label}</button></li>'
                )
                recon_tree = ET.parse(recon_file)
                if fuz_path_v and os.path.isfile(fuz_path_v):
                    _annotate_fuzzy(recon_tree, fuz_path_v, files.get('fuzzy_cov'))
                pane_html = xslt.xml_to_html_from_tree(recon_tree, 'toc2html-view.xsl')
                pane_items.append(
                    f'<div class="tab-pane fade {show} {active}" id="{pane_id}"'
                    f' role="tabpanel" aria-labelledby="research-corr-tab-{i}">'
                    f'{pane_html}</div>'
                )
            result = (
                '<ul class="nav nav-tabs params-corr-tabs mb-2" role="tablist">'
                + ''.join(nav_items) + '</ul>'
                + '<div class="tab-content">' + ''.join(pane_items) + '</div>'
            )
            fuz_path = files.get('fuzzy')
            if fuz_path and os.path.isfile(fuz_path):
                fuz_cov   = files.get('fuzzy_cov')
                view_path = fuz_cov if fuz_cov and os.path.isfile(fuz_cov) else fuz_path
                fuzzy_html = xslt.xml_to_html(view_path, 'fuzzy2html.xsl')
                result += (
                    '<button type="button" class="params-sec-hdr collapsed"'
                    ' data-bs-toggle="collapse" data-bs-target="#params-fuzzy-sec"'
                    ' aria-expanded="false">Fuzzy</button>'
                    '<div class="collapse" id="params-fuzzy-sec">' + fuzzy_html + '</div>'
                )
            return result

        parts = []
        for recon_file in recon_files:
            if len(recon_files) > 1:
                label = os.path.basename(recon_file)
                parts.append(f'<h5 class="mt-3 border-bottom pb-1">{label}</h5>')
            recon_tree = ET.parse(recon_file)
            if fuz_path_v and os.path.isfile(fuz_path_v):
                _annotate_fuzzy(recon_tree, fuz_path_v, files.get('fuzzy_cov'))
            parts.append(xslt.xml_to_html_from_tree(recon_tree, 'toc2html-view.xsl'))
        fuz_path = files.get('fuzzy')
        if fuz_path and os.path.isfile(fuz_path):
            fuz_cov = files.get('fuzzy_cov')
            view_path = fuz_cov if fuz_cov and os.path.isfile(fuz_cov) else fuz_path
            fuzzy_html = xslt.xml_to_html(view_path, 'fuzzy2html.xsl')
            parts.append(
                '<button type="button" class="params-sec-hdr collapsed"'
                ' data-bs-toggle="collapse" data-bs-target="#params-fuzzy-sec"'
                ' aria-expanded="false">Fuzzy</button>'
                '<div class="collapse" id="params-fuzzy-sec">' + fuzzy_html + '</div>'
            )
        return '\n'.join(parts)

    if tab == 'lexicons':
        ss = 'lexicon2html.xsl' if mode == 'paragraph' else 'lexicon2table.xsl'
        data_files = files.get('data', {})
        lang = request.args.get('lang')
        if lang:
            path = data_files.get(lang)
            if not path:
                return f'<p class="text-danger">Language not found: {lang}</p>', 404
            return xslt.xml_to_html(path, ss)
        # fallback: all languages at once (backward compat)
        parts = []
        for lg, path in sorted(data_files.items()):
            parts.append(f'<h5 class="mt-3 mb-1 border-bottom pb-1">{lg}</h5>')
            parts.append(xslt.xml_to_html(path, ss))
        return '\n'.join(parts) or '<p class="text-muted">No lexicons.</p>'

    if tab == 'mel':
        mel_path = files.get('mel')
        if not mel_path:
            return '<p class="text-muted">No MEL file selected.</p>'
        mel_basename = os.path.basename(mel_path)
        if mode == 'edit':
            html = xslt.xml_to_html(mel_path, 'mel2html-edit.xsl',
                                    params={'mel_filename': mel_basename})
            return f'<div data-mel-file="{mel_path}">{html}</div>'
        return xslt.xml_to_html(mel_path, 'mel2html.xsl',
                                params={'mel_filename': mel_basename})

    if tab == 'fuzzy':
        fuz_path = files.get('fuzzy')
        if not fuz_path:
            return '<p class="text-muted">No Fuzzy file selected.</p>'
        if mode == 'edit':
            html = xslt.xml_to_html(fuz_path, 'fuzzy2html-edit.xsl')
            return f'<div data-fuz-file="{fuz_path}">{html}</div>'
        fuz_cov_path = files.get('fuzzy_cov')
        view_path = fuz_cov_path if fuz_cov_path and os.path.isfile(fuz_cov_path) else fuz_path
        return xslt.xml_to_html(view_path, 'fuzzy2html.xsl')

    if tab == 'coverage':
        cov_path = files.get('coverage')
        if not cov_path or not os.path.isfile(cov_path):
            return '<p class="text-muted">No coverage report — run with a MEL selected.</p>'
        # coverage.xml is fully self-contained (languages + annotated
        # per-MEL/per-language/status table) as of the run that produced it
        # -- no per-request re-derivation needed.
        return xslt.xml_to_html(cov_path, 'coverage2html.xsl')

    return '<p class="text-danger">Unknown tab.</p>', 400


# ── Raw XML (for edit mode) ────────────────────────────────────────────────────

@bp.route('/api/raw/<run_id>/<tab>')
def api_raw(run_id, tab):
    with _runs_lock:
        r = _runs.get(run_id)
    if r is None:
        abort(404)
    files = r['files']
    path  = None
    if tab == 'parameters' and files.get('recon'):
        path = files['recon'][0]
    elif tab == 'mel':
        path = files.get('mel')
    elif tab == 'fuzzy':
        path = files.get('fuzzy')
    if not path or not os.path.isfile(path):
        abort(404)
    with open(path, 'r', encoding='utf-8') as fh:
        return Response(fh.read(), mimetype='text/plain; charset=utf-8')


# ── Save edited XML ────────────────────────────────────────────────────────────

@bp.route('/api/save/<run_id>/<tab>', methods=['POST'])
def api_save(run_id, tab):
    with _runs_lock:
        r = _runs.get(run_id)
    if r is None:
        return jsonify(error='Unknown run'), 404

    files = r['files']
    path  = None
    if tab == 'parameters' and files.get('recon'):
        path = files['recon'][0]
    elif tab == 'mel':
        path = files.get('mel')
    elif tab == 'fuzzy':
        path = files.get('fuzzy')
    if not path:
        return jsonify(error='No file mapped to this tab'), 400

    xml_text = request.get_data(as_text=True)
    try:
        ET.fromstring(xml_text.encode('utf-8'))
    except ET.XMLSyntaxError as exc:
        return jsonify(error=f'XML not well-formed: {exc}'), 422

    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(xml_text)
    return jsonify(ok=True, saved_to=path)


# ── Save correspondences from XSLT edit form ──────────────────────────────────

@bp.route('/api/save_toc/<run_id>', methods=['POST'])
def api_save_toc(run_id):
    """Reconstruct a correspondences XML file from the XSLT edit form fields."""
    with _runs_lock:
        r = _runs.get(run_id)
    if r is None:
        return jsonify(error='Unknown run'), 404

    body      = request.get_json(force=True)
    fields    = body.get('fields',   {})
    dialects  = body.get('dialects', [])
    file_path = body.get('file_path', '')

    recon_files = r['files'].get('recon', [])
    if file_path not in recon_files:
        return jsonify(error='Unknown or unauthorised file path'), 400

    try:
        orig_root = ET.parse(file_path).getroot()
    except Exception as exc:
        return jsonify(error=f'Could not read original: {exc}'), 500

    new_root = ET.Element('tableOfCorr')

    createdat = orig_root.find('createdat')
    if createdat is not None:
        new_root.append(copy.deepcopy(createdat))

    params_el = ET.SubElement(new_root, 'parameters')
    n = 1
    while f'class-{n}-name' in fields:
        cls_el = ET.SubElement(params_el, 'class')
        cls_el.set('name',  fields.get(f'class-{n}-name',  ''))
        cls_el.set('value', fields.get(f'class-{n}-value', ''))
        n += 1
    if 'canon' in fields:
        ET.SubElement(params_el, 'canon').set('value', fields['canon'])
    if 'context_match_type' in fields:
        ET.SubElement(params_el, 'context_match_type').set(
            'value', fields['context_match_type'])
    if 'spec' in fields:
        ET.SubElement(params_el, 'spec').set('value', fields['spec'])

    if not dialects:
        seen: set = set()
        for k in fields:
            m = _re.match(r'^cell-r1-c-(.+)$', k)
            if m and m.group(1) not in seen:
                dialects.append(m.group(1))
                seen.add(m.group(1))

    row = 1
    while f'r{row}-proto' in fields or f'r{row}-num' in fields:
        corr_el = ET.SubElement(new_root, 'corr')
        corr_el.set('num', fields.get(f'r{row}-num', str(row)))

        proto_el = ET.SubElement(corr_el, 'proto')
        proto_el.text = fields.get(f'r{row}-proto', '')
        syll  = fields.get(f'r{row}-syll',  '')
        left  = fields.get(f'r{row}-left',  '')
        right = fields.get(f'r{row}-right', '')
        if syll:  proto_el.set('syll',     syll)
        if left:  proto_el.set('contextL', left)
        if right: proto_el.set('contextR', right)

        for d in dialects:
            cell_val  = fields.get(f'cell-r{row}-c-{d}', '')
            modern_el = ET.SubElement(corr_el, 'modern')
            modern_el.set('dialecte', d)
            segs = [s.strip() for s in cell_val.split(',') if s.strip()]
            if segs:
                for seg_text in segs:
                    seg_el = ET.SubElement(modern_el, 'seg')
                    if seg_text.startswith('='):
                        seg_el.set('statut', 'doute')
                        seg_el.text = seg_text[1:]
                    else:
                        seg_el.text = seg_text
            else:
                ET.SubElement(modern_el, 'seg')
        row += 1

    rule_n = 1
    while f'rule-{rule_n}-input' in fields:
        rule_el = ET.SubElement(new_root, 'rule')
        num_v  = fields.get(f'rule-{rule_n}-num',   str(rule_n))
        stage  = fields.get(f'rule-{rule_n}-stage',  '')
        if num_v: rule_el.set('num',   num_v)
        if stage: rule_el.set('stage', stage)

        inp_el = ET.SubElement(rule_el, 'input')
        inp_el.text = fields.get(f'rule-{rule_n}-input', '')
        cl = fields.get(f'rule-{rule_n}-contextL', '')
        cr = fields.get(f'rule-{rule_n}-contextR', '')
        if cl: inp_el.set('contextL', cl)
        if cr: inp_el.set('contextR', cr)

        out_el = ET.SubElement(rule_el, 'outcome')
        out_el.text = fields.get(f'rule-{rule_n}-output', '')
        langs = fields.get(f'rule-{rule_n}-languages', '')
        if langs: out_el.set('languages', langs)
        rule_n += 1

    for tag in ('protolanguage', 'quirk'):
        for el in orig_root.findall(tag):
            new_root.append(copy.deepcopy(el))

    xml_bytes = ET.tostring(new_root, encoding='utf-8', xml_declaration=True)
    try:
        with open(file_path, 'wb') as fh:
            fh.write(xml_bytes)
    except OSError as exc:
        return jsonify(error=f'Could not write file: {exc}'), 500

    return jsonify(ok=True, saved_to=os.path.basename(file_path))


# ── Save MEL from XSLT edit form ──────────────────────────────────────────────

@bp.route('/api/save_mel/<run_id>', methods=['POST'])
def api_save_mel(run_id):
    """Reconstruct a MEL XML file from the XSLT edit form fields."""
    with _runs_lock:
        r = _runs.get(run_id)
    if r is None:
        return jsonify(error='Unknown run'), 404

    body      = request.get_json(force=True)
    fields    = body.get('fields',   {})
    file_path = body.get('file_path', '')

    if file_path != r['files'].get('mel'):
        return jsonify(error='Unknown or unauthorised file path'), 400

    new_root = ET.Element('semantics')
    n = 1
    while f'mel-{n}-id' in fields:
        mel_el = ET.SubElement(new_root, 'mel')
        mel_el.set('id', fields.get(f'mel-{n}-id', ''))
        for g in [g.strip() for g in fields.get(f'mel-{n}-glosses', '').split(',') if g.strip()]:
            ET.SubElement(mel_el, 'gl').text = g
        n += 1

    xml_bytes = ET.tostring(new_root, encoding='utf-8', xml_declaration=True)
    try:
        with open(file_path, 'wb') as fh:
            fh.write(xml_bytes)
    except OSError as exc:
        return jsonify(error=f'Could not write file: {exc}'), 500

    return jsonify(ok=True, saved_to=os.path.basename(file_path))


# ── Save Fuzzy from XSLT edit form ────────────────────────────────────────────

@bp.route('/api/save_fuz/<run_id>', methods=['POST'])
def api_save_fuz(run_id):
    """Reconstruct a fuzzy XML file from the XSLT edit form fields."""
    with _runs_lock:
        r = _runs.get(run_id)
    if r is None:
        return jsonify(error='Unknown run'), 404

    body      = request.get_json(force=True)
    fields    = body.get('fields',   {})
    file_path = body.get('file_path', '')

    if file_path != r['files'].get('fuzzy'):
        return jsonify(error='Unknown or unauthorised file path'), 400

    new_root = ET.Element('fuzzy')
    n = 1
    while f'item-{n}-dial' in fields:
        item_el = ET.SubElement(new_root, 'item')
        item_el.set('dial', fields.get(f'item-{n}-dial', ''))
        item_el.set('to',   fields.get(f'item-{n}-to',   ''))
        for f_val in [v.strip() for v in fields.get(f'item-{n}-from', '').split(',') if v.strip()]:
            ET.SubElement(item_el, 'from').text = f_val
        n += 1

    xml_bytes = ET.tostring(new_root, pretty_print=True,
                            encoding='utf-8', xml_declaration=True)
    try:
        with open(file_path, 'wb') as fh:
            fh.write(xml_bytes)
    except OSError as exc:
        return jsonify(error=f'Could not write file: {exc}'), 500

    # The coverage-annotated copy (fuzzy_cov) is now stale — it reflects usage
    # counts from the last run against the OLD fuzzy rules.  Remove it from the
    # run's file map so the view immediately re-renders from the freshly-saved
    # fuz_path instead of the stale coverage file.
    with _runs_lock:
        stale_cov = r['files'].pop('fuzzy_cov', None)
    if stale_cov and os.path.isfile(stale_cov):
        try:
            os.remove(stale_cov)
        except OSError:
            pass   # best effort

    return jsonify(ok=True, saved_to=os.path.basename(file_path))


# ── Run history ───────────────────────────────────────────────────────────────

@bp.route('/api/history/<project>')
def api_history(project):
    """Return run-log entries for a project, newest first."""
    return jsonify(runs=runlog.get_runs(project))


@bp.route('/api/load_run', methods=['POST'])
def api_load_run():
    """Load a historical run into _runs and return its metadata."""
    body   = request.get_json(force=True)
    run_id = body.get('run_id', '')
    if not run_id:
        return jsonify(error='Missing run_id'), 400

    # Already live in memory?
    with _runs_lock:
        existing = _runs.get(run_id)
    if existing and existing['status'] == 'done':
        r      = existing
        record = runlog.get_run(run_id) or {}
        if 'run_params' not in r:
            r['run_params'] = record.get('params', {})
    else:
        record = runlog.get_run(run_id)
        if not record:
            return jsonify(error='Run not found in history'), 404
        f = record.get('files', {})
        log_path  = f.get('log', '')
        log_lines = []
        if log_path and os.path.isfile(log_path):
            try:
                with open(log_path, encoding='utf-8') as fh:
                    log_lines = fh.read().splitlines()
            except OSError:
                pass
        data = f.get('data') or {}
        # Resolve fuzzy_cov: use stored path if present, else derive from
        # the sets filename (handles records written before this was persisted).
        fuzzy_cov = f.get('fuzzy_cov') or None
        if not fuzzy_cov:
            sets_path = f.get('sets') or ''
            if sets_path.endswith('.sets.xml'):
                candidate = sets_path[:-len('.sets.xml')] + '.fuzzy_cov.xml'
                if os.path.isfile(candidate):
                    fuzzy_cov = candidate
        r = {
            'id':         run_id,
            'project':    record['project'],
            'run_name':   record['run_name'],
            'status':     'done',
            'log':        log_lines,
            'error':      None,
            'run_params': record.get('params', {}),
            'files': {
                'sets':      f.get('sets')     or None,
                'stats':     f.get('stats')    or None,
                'log':       log_path          or None,
                'recon':     f.get('recon')    or [],
                'data':      data,
                'mel':       f.get('mel')      or None,
                'fuzzy':     f.get('fuzzy')    or None,
                'fuzzy_cov': fuzzy_cov,
                'coverage':  f.get('coverage') or None,
            },
        }
        with _runs_lock:
            _runs[run_id] = r

    files    = r['files']
    log_lines = r.get('log', [])
    return jsonify(
        run_id       = run_id,
        run_name     = r['run_name'],
        project      = r['project'],
        params       = record.get('params', {}),
        log          = log_lines,
        has_mel      = bool(files.get('mel')      and os.path.isfile(files['mel'])),
        has_fuzzy    = bool(files.get('fuzzy')    and os.path.isfile(files['fuzzy'])),
        has_coverage = bool(files.get('coverage') and os.path.isfile(files['coverage'])),
    )


@bp.route('/api/compare_runs', methods=['POST'])
def api_compare_runs():
    """Compare two runs (same project); save a .compare.xml and return HTML."""
    body = request.get_json(force=True)
    id_a = body.get('run_id_a', '')
    id_b = body.get('run_id_b', '')

    def _get_record(run_id):
        rec = runlog.get_run(run_id)
        if rec:
            return rec
        with _runs_lock:
            r = _runs.get(run_id)
        if r and r['status'] == 'done':
            files = r['files']
            return {
                'run_id':   run_id,
                'run_name': r.get('run_name', ''),
                'project':  r.get('project', ''),
                'sets': 0, 'isolates': 0, 'failures': 0,
                'params': {
                    'context_match_type': r.get('context_match_type', ''),
                    'spec':               r.get('spec', ''),
                },
                'files': {
                    'sets':     files.get('sets')     or '',
                    'coverage': files.get('coverage') or '',
                },
            }
        return None

    rec_a = _get_record(id_a)
    rec_b = _get_record(id_b)

    if not rec_a or not rec_b:
        return '<p class="text-danger">One or both runs not found.</p>'
    if rec_a.get('project') != rec_b.get('project'):
        return '<p class="text-warning">Comparison requires runs from the same project.</p>'

    project = rec_a['project']

    # Build the <compare> XML element tree
    compare_root = run_compare.build_compare_xml(rec_a, rec_b)

    # Save to a named file in the project's runs/ directory
    compare_path = None
    if project in proj_module.projects:
        runs_dir = os.path.join(proj_module.projects[project], 'runs')
        os.makedirs(runs_dir, exist_ok=True)
        name_a   = rec_a.get('run_name', id_a)
        name_b   = rec_b.get('run_name', id_b)
        fname    = f'{project}.{name_a}-vs-{name_b}.compare.xml'
        compare_path = os.path.join(runs_dir, fname)
        try:
            ET.ElementTree(compare_root).write(
                compare_path, encoding='utf-8',
                xml_declaration=True, pretty_print=True)
        except OSError:
            compare_path = None

    # Render via XSLT
    if compare_path and os.path.isfile(compare_path):
        return xslt.xml_to_html(compare_path, 'compare2html.xsl')

    # Fallback: transform the in-memory tree (no persistence)
    return xslt.xml_to_html_from_tree(
        ET.ElementTree(compare_root), 'compare2html.xsl')


@bp.route('/api/delete_run', methods=['POST'])
def api_delete_run():
    """Delete a run record from the log and remove its output files."""
    body   = request.get_json(force=True)
    run_id = body.get('run_id', '')
    if not run_id:
        return jsonify(error='Missing run_id'), 400

    record = runlog.delete_run(run_id)
    if not record:
        return jsonify(error='Run not found'), 404

    # Evict from in-memory store too
    with _runs_lock:
        _runs.pop(run_id, None)

    # Delete output files only (sets, stats, log, coverage — not input mel/fuzzy/recon)
    deleted, errors = [], []
    for key in ('sets', 'stats', 'log', 'coverage'):
        path = record.get('files', {}).get(key, '')
        if not path:
            continue
        if os.path.isfile(path):
            try:
                os.remove(path)
                deleted.append(os.path.basename(path))
            except OSError as exc:
                errors.append(str(exc))

    return jsonify(
        ok            = True,
        deleted       = deleted,
        errors        = errors,
        history_count = runlog.count_runs(record.get('project', '')),
    )


# ── Save projects.toml ────────────────────────────────────────────────────────

@bp.route('/api/save_projects', methods=['POST'])
def api_save_projects():
    """Rewrite projects.toml from a JSON list of {name, path} objects."""
    body     = request.get_json(force=True)
    projects = body.get('projects', [])

    lines   = ['# projects configuration\n']
    invalid = []
    repo_root      = os.path.dirname(PROJECTS_TOML)
    local_projects = os.path.normpath(os.path.join(repo_root, 'projects'))
    for entry in projects:
        name = str(entry.get('name', '')).strip()
        path = str(entry.get('path', '')).strip()
        if not name:
            continue
        resolved = path if os.path.isabs(path) else os.path.normpath(
            os.path.join(repo_root, path))
        if not os.path.isdir(resolved):
            invalid.append({'name': name, 'path': path, 'resolved': resolved})
        # Write local projects/ entries as relative paths; keep others as-is
        if os.path.normpath(resolved).startswith(local_projects + os.sep) or \
                os.path.normpath(resolved) == local_projects:
            rel = os.path.relpath(resolved, repo_root).replace('\\', '/')
            escaped = rel.replace('"', '\\"')
        else:
            escaped = path.replace('\\', '\\\\').replace('"', '\\"')
        # Always use a quoted TOML key so names with dots, spaces, etc. are
        # stored literally.  "x.y" = "..." is a quoted key (value "x.y"),
        # whereas x.y = "..." is a dotted key (nested table), which tomllib
        # would return as {'x': {'y': '...'}} — breaking the name lookup.
        escaped_name = name.replace('\\', '\\\\').replace('"', '\\"')
        lines.append(f'"{escaped_name}" = "{escaped}"\n')

    if invalid:
        return jsonify(
            error='Some paths do not point to existing directories',
            invalid=invalid
        ), 400

    try:
        with open(PROJECTS_TOML, 'w', encoding='utf-8') as fh:
            fh.writelines(lines)
    except OSError as exc:
        return jsonify(error=f'Could not write projects.toml: {exc}'), 500

    proj_module.projects = proj_module.get_dirs('projects')
    return jsonify(ok=True)


# ── Interactive pane — language list ──────────────────────────────────────────

@bp.route('/api/interactive_langs/<run_id>')
def api_interactive_langs(run_id):
    """Return attested language list for the Interactive pane, in upstream order."""
    import read as re_read

    with _runs_lock:
        r = _runs.get(run_id)
    if r is None or r['status'] != 'done':
        return jsonify(error='Run not found'), 404

    attested_set = set(r['files'].get('data', {}).keys())
    run_params   = r.get('run_params', {})
    upstream_str = (run_params.get('upstream') or '').strip()

    if upstream_str:
        try:
            upstream_map = re_read.parse_upstream(upstream_str)
            proto_keys   = set(upstream_map.keys())
            ordered = [
                lg for lgs in upstream_map.values()
                for lg in lgs
                if lg not in proto_keys
            ]
            # Keep only languages actually attested in this run, in upstream order
            seen    = set()
            ordered = [lg for lg in ordered
                       if lg in attested_set and lg not in seen and not seen.add(lg)]
            # Append any attested languages not mentioned in the upstream string
            for lg in sorted(attested_set - set(ordered)):
                ordered.append(lg)
        except Exception:
            ordered = sorted(attested_set)
    else:
        ordered = sorted(attested_set)

    return jsonify(languages=ordered)


# ── Interactive pane — load forms from an existing set ───────────────────────

@bp.route('/api/run/<run_id>/set_forms')
def api_set_forms(run_id):
    """Return {language, reflex, gloss} forms for one cognate set in a completed run."""
    import xml.etree.ElementTree as ET
    set_num = request.args.get('num', '').strip()
    if not set_num:
        return jsonify(error='num parameter required'), 400
    with _runs_lock:
        r = _runs.get(run_id)
    if r is None or r.get('status') != 'done':
        return jsonify(error='Run not found or not complete'), 404
    sets_path = (r.get('files') or {}).get('sets', '')
    if not sets_path or not os.path.exists(sets_path):
        return jsonify(error='Sets file not found'), 404
    try:
        root = ET.parse(sets_path).getroot()
        target = None
        for s in root.iterfind('.//sets/set'):
            if (s.findtext('id') or '').strip() == set_num:
                target = s
                break
        if target is None:
            return jsonify(error=f'Set {set_num!r} not found'), 404
        forms = []
        for rfx in target.iterfind('.//rfx'):
            lg = (rfx.findtext('lg') or '').strip()
            lx = (rfx.findtext('lx') or '').strip()
            gl = (rfx.findtext('gl') or '').strip()
            if lg and lx:
                forms.append({'language': lg, 'reflex': lx, 'gloss': gl})
        return jsonify(forms=forms)
    except Exception as exc:
        return jsonify(error=str(exc)), 500


# ── Interactive pane — run ────────────────────────────────────────────────────

@bp.route('/api/interactive_run', methods=['POST'])
def api_interactive_run():
    """Run the Upstream process on a user-supplied set of reflexes and glosses."""
    import RE, read as re_read, load_hooks
    import unicodedata

    body       = request.get_json(force=True)
    run_id     = body.get('run_id')
    forms_data = body.get('forms', [])   # [{language, reflex, gloss}, ...]

    with _runs_lock:
        r = _runs.get(run_id)
    if r is None or r['status'] != 'done':
        return jsonify(error='Base run not found or not complete'), 400

    project = r['project']
    if project not in proj_module.projects:
        return jsonify(error=f'Project not found: {project}'), 400
    project_path = proj_module.projects[project]

    run_params   = r.get('run_params', {})
    recon        = run_params.get('recon')    or None
    mel          = run_params.get('mel')      or None
    fuzzy        = run_params.get('fuzzy')    or None
    upstream     = run_params.get('upstream') or None

    try:
        load_hooks.load_hook(project_path)
        settings = re_read.read_settings(
            project_path, project, recon,
            mel_token=mel, fuzzy_token=fuzzy, upstream=upstream)
    except Exception as exc:
        return jsonify(error=f'Could not read settings: {exc}'), 500

    # Apply the same Unicode normalisation that read_attested_lexicons would use
    ctx = getattr(settings, 'context_match_type', None)
    norm = (lambda s: unicodedata.normalize('NFD', s)) if ctx == 'glyphs' \
           else (lambda s: unicodedata.normalize('NFC', s))

    # Build attested lexicons from user-supplied form data
    attested_by_lang = {}
    for item in forms_data:
        lang   = item.get('language', '').strip()
        reflex = item.get('reflex',   '').strip()
        gloss  = item.get('gloss',    '').strip()
        if lang and reflex and lang in settings.attested:
            attested_by_lang.setdefault(lang, []).append(
                RE.ModernForm(lang, norm(reflex), gloss, ''))

    if not attested_by_lang:
        return jsonify(error='No valid forms entered (check languages match the run)'), 400

    # Provide empty lexicons for all expected attested languages so upstream_tree
    # can reach every leaf — languages with no forms will simply produce no reconstructions.
    attested_lexicons = {
        lang: RE.Lexicon(lang, attested_by_lang.get(lang, []), [])
        for lang in settings.attested
    }

    old_debug  = RE.Debug.debug
    RE.Debug.debug = True

    old_stdout = sys.stdout
    class _Tee:
        def __init__(self, orig): self._orig = orig
        def write(self, s):
            return self._orig.write(s)
        def flush(self): self._orig.flush()
    sys.stdout = _Tee(old_stdout)

    try:
        B = RE.upstream(settings, attested_lexicons, only_with_mel=False)

        # Mirror the post-processing done in do_run so serialize_sets has everything it needs
        _isolates_dict = RE.extract_isolates(B)
        B.isolates_dict = _isolates_dict
        B.isolates = sorted(_isolates_dict.keys(), key=lambda x: x.language)
        B.failures = sorted(B.statistics.failed_parses, key=lambda x: x.language)

        # Serialize sets to a uniquely-named file (not added to run history)
        run_name  = time.strftime('%Y%m%d-%H%M%S')
        runs_dir  = os.path.join(project_path, 'runs')
        os.makedirs(runs_dir, exist_ok=True)
        sets_xml  = os.path.join(runs_dir,
                                 f'{project}.interactive.{run_name}.sets.xml')
        inter_pls = [pl for pl in settings.proto_languages
                     if pl != settings.upstream_target]
        all_langs = inter_pls + list(settings.attested.keys())
        B.mel_used = getattr(settings, 'mel_filename', None) is not None
        RE.dump_xml_sets(B, all_langs, sets_xml, True)

        sets_html    = xslt.xml_to_html(sets_xml, 'sets2html.xsl')
        print(f'Interactive: {len(B.statistics.debug_notes)} debug notes, '
              f'{len(B.statistics.notes)} summary notes, '
              f'{len(B.failures)} failures')
        process_html = _build_process_html(
            B.statistics.debug_notes, B.statistics.notes, B.failures)

    except Exception:
        return jsonify(error=traceback.format_exc()), 500
    finally:
        RE.Debug.debug = old_debug
        sys.stdout      = old_stdout

    return jsonify(process_html=process_html, sets_html=sets_html)
