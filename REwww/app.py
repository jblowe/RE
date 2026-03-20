"""REweb/app.py – Flask web front-end for the Reconstruction Engine.

Usage:
    cd REweb
    python app.py [--host 127.0.0.1] [--port 5001] [--debug]
"""

import copy
import os
import re as _re
import sys
import time
import threading
import traceback
import uuid
from types import SimpleNamespace

import lxml.etree as ET
from flask import (Flask, abort, jsonify, render_template,
                   request, Response)

# ── Path setup ────────────────────────────────────────────────────────────────
HERE          = os.path.dirname(os.path.abspath(__file__))
SRC_DIR       = os.path.join(HERE, '..', 'src')
STYLES_DIR    = os.path.join(HERE, '..', 'styles')
STATIC_DIR    = os.path.join(HERE, 'static')
PROJECTS_TOML = os.path.normpath(os.path.join(HERE, '..', 'projects.toml'))

sys.path.insert(0, SRC_DIR)

import RE
import read
import serialize
import load_hooks
import projects as proj_module
from utils import find_candidates, resolve_file

# ── Flask app ─────────────────────────────────────────────────────────────────
app = Flask(
    __name__,
    template_folder=os.path.join(HERE, 'templates'),
    static_folder=STATIC_DIR,
    static_url_path='/static',
)

# In-memory run store  { run_id -> run_info dict }
_runs: dict = {}
_runs_lock  = threading.Lock()


# ── XSLT helpers ──────────────────────────────────────────────────────────────

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


def _stylesheet_for(filename: str, mode: str = 'paragraph') -> str | None:
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


# ── Main page ─────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    all_projects = proj_module.projects          # dict name -> abs path
    project_data = {}
    for name, path in sorted(all_projects.items()):
        if not os.path.isdir(path):
            continue
        recons  = find_candidates(path, 'correspondences.xml')
        mels    = find_candidates(path, 'mel.xml')
        fuzzies = find_candidates(path, 'fuz.xml')
        project_data[name] = {
            'path':    path,
            'recons':  recons,
            'mels':    mels,
            'fuzzies': fuzzies,
        }
    return render_template('index.html', project_data=project_data)


# ── Project file-list refresh ─────────────────────────────────────────────────

@app.route('/api/projects')
def api_projects():
    """Return current project file candidates as JSON (used by the Refresh button)."""
    proj_module.projects = proj_module.get_dirs('projects')   # re-read toml
    all_projects = proj_module.projects
    data = {}
    for name, path in sorted(all_projects.items()):
        if not os.path.isdir(path):
            continue
        data[name] = {
            'path':    path,
            'recons':  find_candidates(path, 'correspondences.xml'),
            'mels':    find_candidates(path, 'mel.xml'),
            'fuzzies': find_candidates(path, 'fuz.xml'),
        }
    return jsonify(data)


# ── Start an upstream run ─────────────────────────────────────────────────────

@app.route('/api/run', methods=['POST'])
def api_run():
    """Start an upstream run.  Returns { run_id, run_name }."""
    body     = request.get_json(force=True)
    project  = body.get('project')
    recon    = body.get('recon') or None
    mel      = body.get('mel')   or None
    fuzzy    = body.get('fuzzy') or None
    upstream = body.get('upstream') or None

    if project not in proj_module.projects:
        return jsonify(error=f'Unknown project: {project}'), 400

    project_path = proj_module.projects[project]
    run_name     = time.strftime('%Y%m%d-%H%M%S')
    run_id       = str(uuid.uuid4())

    run_info = {
        'id':       run_id,
        'project':  project,
        'run_name': run_name,
        'status':   'running',   # running | done | error
        'log':      [],
        'files':    {},
        'error':    None,
    }
    with _runs_lock:
        _runs[run_id] = run_info

    # ── Background thread ─────────────────────────────────────────────────────
    def do_run():
        log = run_info['log']

        class _Tee:
            """Forward writes to both the original stdout and the log list."""
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
            load_hooks.load_hook(project_path)
            settings = read.read_settings(
                project_path, project, recon,
                mel_token=mel, fuzzy_token=fuzzy, upstream=upstream)

            B = RE.batch_all_upstream(settings, only_with_mel=False)

            # Post-process (mirrors REcli.py)
            B.isolates = sorted(
                RE.extract_isolates(B).keys(), key=lambda x: x.language)
            B.failures = sorted(
                B.statistics.failed_parses, key=lambda x: x.language)

            sets_xml = os.path.join(
                project_path, f'{project}.{run_name}.sets.xml')
            RE.dump_xml_sets(
                B, settings.upstream[settings.upstream_target],
                sets_xml, False)

            B.statistics.add_stat('isolates', len(B.isolates))
            B.statistics.add_stat('failure',  len(B.failures))
            B.statistics.add_stat('sets',     len(B.forms))

            stats_xml = os.path.join(
                project_path,
                f'{project}.{run_name}.upstream.statistics.xml')

            args_ns = SimpleNamespace(
                run=run_name, project=project, project_path=project_path,
                recon=recon, mel=mel, fuzzy=fuzzy, upstream=upstream,
                only_with_mel=False)
            serialize.serialize_stats(
                B.statistics, settings, args_ns, stats_xml)

            mel_path   = getattr(settings, 'mel_filename',   None)
            fuzzy_path = getattr(settings, 'fuzzy_filename', None)

            run_info['files'] = {
                'sets':   sets_xml,
                'stats':  stats_xml,
                # correspondences files (one per proto-language)
                'recon':  list(settings.proto_languages.values()),
                # attested lexicon files keyed by language code
                'data':   {lg: os.path.join(settings.directory_path, p)
                           for lg, p in settings.attested.items()},
                'mel':    mel_path   if mel_path   and os.path.isfile(mel_path)   else None,
                'fuzzy':  fuzzy_path if fuzzy_path and os.path.isfile(fuzzy_path) else None,
            }
            run_info['status'] = 'done'

        except Exception:
            run_info['error']  = traceback.format_exc()
            run_info['status'] = 'error'
        finally:
            sys.stdout = old_stdout

    threading.Thread(target=do_run, daemon=True).start()
    return jsonify(run_id=run_id, run_name=run_name)


# ── Poll run status ───────────────────────────────────────────────────────────

@app.route('/api/poll/<run_id>')
def api_poll(run_id):
    """Return current status + accumulated log."""
    with _runs_lock:
        r = _runs.get(run_id)
    if r is None:
        return jsonify(error='unknown run'), 404
    return jsonify(
        status    = r['status'],
        log       = r['log'],
        error     = r['error'],
        has_mel   = bool(r['files'].get('mel'))   if r['status'] == 'done' else None,
        has_fuzzy = bool(r['files'].get('fuzzy')) if r['status'] == 'done' else None,
    )


# ── Tab content ───────────────────────────────────────────────────────────────

@app.route('/api/tab/<run_id>/<tab>')
def api_tab(run_id, tab):
    """Return rendered HTML for a tab pane."""
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
        return xml_to_html(files['sets'], ss)

    if tab == 'stats':
        return xml_to_html(files['stats'], 'stats2html.xsl')

    if tab == 'parameters':
        recon_files = files.get('recon', [])
        if not recon_files:
            return '<p class="text-muted">No correspondences files.</p>'

        if mode == 'edit':
            # Edit mode: render first file as an interactive form via toc2html-edit.xsl.
            # Wrap in a div whose data-recon-file attr tells the client which file to save.
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
            html = xml_to_html(recon_file, 'toc2html-edit.xsl')
            return f'{note}<div data-recon-file="{recon_file}">{html}</div>'

        # View mode: render all files
        parts = []
        for recon_file in recon_files:
            label = os.path.basename(recon_file)
            parts.append(f'<h5 class="mt-3 border-bottom pb-1">{label}</h5>')
            parts.append(xml_to_html(recon_file, 'toc2html-view.xsl'))
        return '\n'.join(parts)

    if tab == 'lexicons':
        ss = 'lexicon2html.xsl' if mode == 'paragraph' else 'lexicon2table.xsl'
        parts = []
        for lg, path in sorted(files.get('data', {}).items()):
            parts.append(
                f'<h5 class="mt-3 mb-1 border-bottom pb-1 text-primary">'
                f'{lg}</h5>')
            parts.append(xml_to_html(path, ss))
        return '\n'.join(parts) or '<p class="text-muted">No lexicons.</p>'

    if tab == 'mel':
        mel_path = files.get('mel')
        if not mel_path:
            return '<p class="text-muted">No MEL file selected.</p>'
        if mode == 'edit':
            html = xml_to_html(mel_path, 'mel2html-edit.xsl')
            return f'<div data-mel-file="{mel_path}">{html}</div>'
        return xml_to_html(mel_path, 'mel2html.xsl')

    if tab == 'fuzzy':
        fuz_path = files.get('fuzzy')
        if not fuz_path:
            return '<p class="text-muted">No Fuzzy file selected.</p>'
        if mode == 'edit':
            html = xml_to_html(fuz_path, 'fuzzy2html-edit.xsl')
            return f'<div data-fuz-file="{fuz_path}">{html}</div>'
        return xml_to_html(fuz_path, 'fuzzy2html.xsl')

    return '<p class="text-danger">Unknown tab.</p>', 400


# ── Raw XML (for edit mode) ───────────────────────────────────────────────────

@app.route('/api/raw/<run_id>/<tab>')
def api_raw(run_id, tab):
    """Return the raw XML source for a file (used by the Edit button)."""
    with _runs_lock:
        r = _runs.get(run_id)
    if r is None:
        abort(404)
    files = r['files']
    path  = None
    if tab == 'parameters' and files.get('recon'):
        path = files['recon'][0]          # first / only correspondences file
    elif tab == 'mel':
        path = files.get('mel')
    elif tab == 'fuzzy':
        path = files.get('fuzzy')
    if not path or not os.path.isfile(path):
        abort(404)
    with open(path, 'r', encoding='utf-8') as fh:
        return Response(fh.read(), mimetype='text/plain; charset=utf-8')


# ── Save edited XML ───────────────────────────────────────────────────────────

@app.route('/api/save/<run_id>/<tab>', methods=['POST'])
def api_save(run_id, tab):
    """Validate (well-formedness) and save edited XML for a file."""
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


# ── Save correspondences from XSLT edit form ─────────────────────────────────

@app.route('/api/save_toc/<run_id>', methods=['POST'])
def api_save_toc(run_id):
    """Reconstruct a correspondences XML file from the XSLT edit form fields.

    Expects JSON body:
        { "fields":   { name: value, … },   # all <input name=…> values
          "dialects": ["fr", "pt", …],       # dialect order from table headers
          "file_path": "/abs/path/file.xml"  # which correspondences file to save
        }

    The function rebuilds <tableOfCorr> from the form data, preserving
    <createdat>, <parameters/spec>, <protolanguage>, and <quirk> from
    the original file.
    """
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

    # ── Build new root ────────────────────────────────────────────────────────
    new_root = ET.Element('tableOfCorr')

    # Preserve <createdat>
    createdat = orig_root.find('createdat')
    if createdat is not None:
        new_root.append(copy.deepcopy(createdat))

    # Reconstruct <parameters>
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
    # Preserve <spec> from original
    for spec_el in list(orig_root.findall('parameters/spec')) + list(orig_root.findall('spec')):
        params_el.append(copy.deepcopy(spec_el))

    # If no dialect order supplied, infer from row-1 field names
    if not dialects:
        seen: set = set()
        for k in fields:
            m = _re.match(r'^cell-r1-c-(.+)$', k)
            if m and m.group(1) not in seen:
                dialects.append(m.group(1))
                seen.add(m.group(1))

    # Reconstruct <corr> rows
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
                ET.SubElement(modern_el, 'seg')   # preserve empty modern
        row += 1

    # Reconstruct <rule> elements
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

    # Preserve <protolanguage> and <quirk> from original
    for tag in ('protolanguage', 'quirk'):
        for el in orig_root.findall(tag):
            new_root.append(copy.deepcopy(el))

    # ── Write ─────────────────────────────────────────────────────────────────
    xml_bytes = ET.tostring(new_root, encoding='utf-8', xml_declaration=True)
    try:
        with open(file_path, 'wb') as fh:
            fh.write(xml_bytes)
    except OSError as exc:
        return jsonify(error=f'Could not write file: {exc}'), 500

    return jsonify(ok=True, saved_to=os.path.basename(file_path))


# ── Save MEL from XSLT edit form ─────────────────────────────────────────────

@app.route('/api/save_mel/<run_id>', methods=['POST'])
def api_save_mel(run_id):
    """Reconstruct a MEL XML file from the XSLT edit form fields.

    Expects JSON body:
        { "fields":   { name: value, … },   # all <input name=…> values
          "file_path": "/abs/path/file.mel.xml"
        }

    Field naming: mel-{n}-id, mel-{n}-glosses (comma-separated).
    """
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
        glosses_str = fields.get(f'mel-{n}-glosses', '')
        for g in [g.strip() for g in glosses_str.split(',') if g.strip()]:
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

@app.route('/api/save_fuz/<run_id>', methods=['POST'])
def api_save_fuz(run_id):
    """Reconstruct a fuzzy XML file from the XSLT edit form fields.

    Expects JSON body:
        { "fields":   { name: value, … },
          "file_path": "/abs/path/file.fuz.xml"
        }

    Field naming: item-{n}-dial, item-{n}-from (comma-sep), item-{n}-to.
    """
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
        froms_str = fields.get(f'item-{n}-from', '')
        for f_val in [v.strip() for v in froms_str.split(',') if v.strip()]:
            ET.SubElement(item_el, 'from').text = f_val
        n += 1

    xml_bytes = ET.tostring(new_root, encoding='utf-8', xml_declaration=True)
    try:
        with open(file_path, 'wb') as fh:
            fh.write(xml_bytes)
    except OSError as exc:
        return jsonify(error=f'Could not write file: {exc}'), 500

    return jsonify(ok=True, saved_to=os.path.basename(file_path))


# ── Save projects.toml ────────────────────────────────────────────────────────

@app.route('/api/save_projects', methods=['POST'])
def api_save_projects():
    """Rewrite projects.toml from a JSON list of {name, path} objects.

    Expects JSON body:
        { "projects": [ { "name": "ROMANCE", "path": "projects/ROMANCE" }, … ] }
    """
    body     = request.get_json(force=True)
    projects = body.get('projects', [])

    lines = ['# projects configuration\n']
    for entry in projects:
        name = str(entry.get('name', '')).strip()
        path = str(entry.get('path', '')).strip()
        if not name:
            continue
        # Simple TOML key = "value" line; quote the value
        escaped = path.replace('\\', '\\\\').replace('"', '\\"')
        lines.append(f'{name} = "{escaped}"\n')

    try:
        with open(PROJECTS_TOML, 'w', encoding='utf-8') as fh:
            fh.writelines(lines)
    except OSError as exc:
        return jsonify(error=f'Could not write projects.toml: {exc}'), 500

    # Reload the in-memory projects dict so the next run sees the new config
    proj_module.projects = proj_module.get_dirs('projects')

    return jsonify(ok=True)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='RE Flask web app')
    parser.add_argument('--host',  default='127.0.0.1')
    parser.add_argument('--port',  type=int, default=5001)
    parser.add_argument('--debug', action='store_true')
    a = parser.parse_args()
    app.run(host=a.host, port=a.port, debug=a.debug)
