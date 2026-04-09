"""REwww/routes.py – Flask Blueprint: all HTTP route handlers."""

import copy
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
from utils import find_candidates

bp = Blueprint('main', __name__)

# ── In-memory run store  { run_id -> run_info dict } ──────────────────────────
_runs: dict = {}
_runs_lock  = threading.Lock()


# ── PROJECTS_TOML path (set by app.py after import) ───────────────────────────
PROJECTS_TOML: str = ''


# ── Main page ──────────────────────────────────────────────────────────────────

@bp.route('/')
def index():
    all_projects = proj_module.projects
    project_data = {}
    for name, path in sorted(all_projects.items()):
        if not os.path.isdir(path):
            continue
        project_data[name] = {
            'path':    path,
            'recons':  find_candidates(path, 'correspondences.xml'),
            'mels':    find_candidates(path, 'mel.xml'),
            'fuzzies': find_candidates(path, 'fuz.xml'),
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
    for name, path in sorted(proj_module.projects.items()):
        if not os.path.isdir(path):
            continue
        data[name] = {
            'path':          path,
            'recons':        find_candidates(path, 'correspondences.xml'),
            'mels':          find_candidates(path, 'mel.xml'),
            'fuzzies':       find_candidates(path, 'fuz.xml'),
            'history_count': runlog.count_runs(name),
        }
    return jsonify(data)


# ── Start an upstream run ──────────────────────────────────────────────────────

@bp.route('/api/run', methods=['POST'])
def api_run():
    """Start an upstream run.  Returns { run_id, run_name }."""
    import RE, read, serialize, load_hooks

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
            load_hooks.load_hook(project_path)
            settings = read.read_settings(
                project_path, project, recon,
                mel_token=mel, fuzzy_token=fuzzy, upstream=upstream)

            try:
                sc = settings.syllable_canon
                print(f'context_match_type: {sc.context_match_type}')
                print(f'spec (supra_segmentals): {", ".join(sc.supra_segmentals)}')
            except Exception:
                pass

            B = RE.batch_all_upstream(settings, only_with_mel=True)

            _isolates_dict = RE.extract_isolates(B)
            B.isolates_dict = _isolates_dict
            B.isolates = sorted(
                _isolates_dict.keys(), key=lambda x: x.language)
            B.failures = sorted(
                B.statistics.failed_parses, key=lambda x: x.language)

            sets_xml = os.path.join(
                project_path, f'{project}.{run_name}.sets.xml')
            RE.dump_xml_sets(
                B, settings.upstream[settings.upstream_target],
                sets_xml, True)

            # Unique cognate sets = deduplicated by supporting_forms, matching
            # what create_xml_sets actually writes (merging multi-reconstruction sets).
            unique_sets = len({pf.supporting_forms for pf in B.forms})
            B.statistics.add_stat('isolates', len(B.isolates))
            B.statistics.add_stat('failure',  len(B.failures))
            B.statistics.add_stat('sets',     unique_sets)

            stats_xml = os.path.join(
                project_path,
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
                cov_stats = re_coverage.check_mel_coverage(settings)
                coverage_xml = os.path.join(
                    project_path, f'{project}.{run_name}.coverage.xml')
                serialize.serialize_stats(cov_stats, settings, args_ns, coverage_xml)

            # ── Write run log to disk ─────────────────────────────────────
            log_txt = os.path.join(
                project_path, f'{project}.{run_name}.log.txt')
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
                'fuzzy':    fuzzy_path   if fuzzy_path   and os.path.isfile(fuzzy_path)   else None,
                'coverage': coverage_xml if coverage_xml and os.path.isfile(coverage_xml) else None,
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
                        'recon':    recon    or '',
                        'mel':      mel      or '',
                        'fuzzy':    fuzzy    or '',
                        'upstream': upstream or '',
                    },
                    'files': {
                        'sets':     sets_xml  or '',
                        'stats':    stats_xml or '',
                        'log':      log_txt   or '',
                        'mel':      run_info['files'].get('mel')      or '',
                        'fuzzy':    run_info['files'].get('fuzzy')    or '',
                        'coverage': run_info['files'].get('coverage') or '',
                        'recon':    run_info['files'].get('recon')    or [],
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
    return jsonify(
        status       = r['status'],
        log          = r['log'],
        error        = r['error'],
        has_mel      = bool(r['files'].get('mel'))      if r['status'] == 'done' else None,
        has_fuzzy    = bool(r['files'].get('fuzzy'))    if r['status'] == 'done' else None,
        has_coverage = bool(r['files'].get('coverage')) if r['status'] == 'done' else None,
    )


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
        return xslt.xml_to_html(files['sets'], ss)

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
            return xslt.xml_to_html_from_tree(annotated, 'toc2html-freq.xsl')

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

        parts = []
        for recon_file in recon_files:
            label = os.path.basename(recon_file)
            parts.append(f'<h5 class="mt-3 border-bottom pb-1">{label}</h5>')
            parts.append(xslt.xml_to_html(recon_file, 'toc2html-view.xsl'))
        return '\n'.join(parts)

    if tab == 'lexicons':
        ss = 'lexicon2html.xsl' if mode == 'paragraph' else 'lexicon2table.xsl'
        parts = []
        for lg, path in sorted(files.get('data', {}).items()):
            parts.append(
                f'<h5 class="mt-3 mb-1 border-bottom pb-1 text-primary">{lg}</h5>')
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
        return xslt.xml_to_html(fuz_path, 'fuzzy2html.xsl')

    if tab == 'coverage':
        cov_path = files.get('coverage')
        if not cov_path or not os.path.isfile(cov_path):
            return '<p class="text-muted">No coverage report — run with a MEL selected.</p>'
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
    for spec_el in list(orig_root.findall('parameters/spec')) + list(orig_root.findall('spec')):
        params_el.append(copy.deepcopy(spec_el))

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

    xml_bytes = ET.tostring(new_root, encoding='utf-8', xml_declaration=True)
    try:
        with open(file_path, 'wb') as fh:
            fh.write(xml_bytes)
    except OSError as exc:
        return jsonify(error=f'Could not write file: {exc}'), 500

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
        r = {
            'id':       run_id,
            'project':  record['project'],
            'run_name': record['run_name'],
            'status':   'done',
            'log':      log_lines,
            'error':    None,
            'files': {
                'sets':     f.get('sets')     or None,
                'stats':    f.get('stats')    or None,
                'log':      log_path          or None,
                'recon':    f.get('recon')    or [],
                'data':     {},
                'mel':      f.get('mel')      or None,
                'fuzzy':    f.get('fuzzy')    or None,
                'coverage': f.get('coverage') or None,
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
    """Compare two runs (same project); return an HTML fragment."""
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
                'params': {},
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

    return run_compare.compare_runs(rec_a, rec_b)


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
        lines.append(f'{name} = "{escaped}"\n')

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
