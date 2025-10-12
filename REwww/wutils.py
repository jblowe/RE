import os, time, sys, csv
import lxml.etree as ET
import traceback
from bottle import HTTPResponse

# we need some code from the sibling directory where the rest of the RE code lives

# this path is valid on 'local' deployments
sys.path.append(os.path.join('..', 'src'))

# this path is only valid on pythonanywhere
sys.path.append(os.path.join('RE', 'src'))

import projects
import RE, read
import load_hooks
from bottle import template

# nb: we are trying to get the directory above the directory this file is in
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS = 'projects'


def get_version():
    try:
        with os.popen("/usr/bin/git describe --always") as f:
            version = f.read().strip()
        if version == '':  # try alternate location for git (this is the usual Mac location)
            with os.popen("/usr/local/bin/git describe --always") as f:
                version = f.read().strip()
    except:
        version = 'Unknown'
    return version


def get_origin(request):
    # Data user submitted...
    q = request.query.get('q')

    # Original page URL (explicit > reliable)
    origin = request.query.get('origin')  # from hidden input

    # Fallback to Referer if not provided
    if not origin:
        origin = request.get_header('Referer')
    return origin


def add_time_and_version():
    return 'code and data version: %s, system last restarted: %s' % (
        get_version(), time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()))


def combine_parts(*args):
    return os.path.join('..', *args)


def check_template(tpl, data, parameters):
    if 'back' not in data:
        data['back'] = '/list_tree/projects'
    return template(tpl, data=data, form=parameters)


def setup_data(tree, project, filename, display, next, origin):
    full_path = combine_parts(tree, project, filename)
    content, date = file_content(full_path, display, next)
    next = full_path.replace('../', '/edit/')
    # every response needs a project...
    data = {'project': project, 'origin': origin, 'next': next}
    files, base_dir, num_files = data_files(tree, project)
    project_info = get_project_info(project, [])
    data.update({'tree': tree, 'files': files, 'base_dir': base_dir, 'num_files': num_files,
                 'filename': filename, 'date': date, 'project_info': project_info,
                 'content': content, 'back': '/list_tree/projects'
                 })
    return data


def get_project_info(project, data_elements):
    if not project: return []
    project_dir = combine_parts(PROJECTS, project)
    parameters_file = os.path.join(project_dir, f'{project}.master.parameters.xml')
    project_info = {'name': project, 'date': get_info(parameters_file)}
    if project_info['date'] == 'unknown':
        pass
    else:
        # we need to set a recon in order to even read the parameters file
        recon = 'standard'
        settings = read.read_settings_file(parameters_file,
                                           mel=None,
                                           recon=recon,
                                           fuzzy=None)
        for s in settings.other:
            if s in 'fuzzies reconstructions mels title'.split(' '):
                project_info[s] = settings.other[s]

    for i in 'fuzzy recon mel'.split(' '):
        project_info[i] = data_elements[i] if i in data_elements else ''

    return project_info


def data_files(tree, directory):
    directory_dir = projects.find_path(tree, directory)
    filelist = [f for f in sorted(os.listdir(directory_dir)) if os.path.isfile(os.path.join(directory_dir, f))]
    # filelist = [f for f in filelist if '.xml' in f]
    to_display = []
    num_files = 0
    for type in 'rechk'.split(' '):
        to_display.append((f'{type}', [f for f in filelist if f'.{type}' in f]))
        num_files += len([f for f in filelist if f'{type}' in f])
    for type in 'statistics compare'.split(' '):
        to_display.append((f'{type}', [f for f in filelist if f'{type}.xml' in f]))
        num_files += len([f for f in filelist if f'{type}.xml' in f])
    for type in 'sets'.split(' '):
        to_display.append((f'{type}', [f for f in filelist if f'{type}.xml' in f]))
        num_files += len([f for f in filelist if f'{type}.xml' in f])
    for type in 'parameters correspondences mel data fuz'.split(' '):
        to_display.append((f'{type}', [f for f in filelist if f'{type}.xml' in f]))
        num_files += len([f for f in filelist if f'{type}.xml' in f])
    for type in 'correspondences data u8 keys'.split(' '):
        to_display.append((f'{type} csv', [f for f in filelist if f'{type}.csv' in f]))
        num_files += len([f for f in filelist if f'{type}.csv' in f])
    for type in 'keys sets coverage'.split(' '):
        to_display.append((f'{type} txt', [f for f in filelist if f'{type}.txt' in f]))
        num_files += len([f for f in filelist if f'{type}.txt' in f])
    other_files = []
    for type in 'DAT DIS csv xls xlsx ods log'.split(' '):
        [other_files.append(f) for f in filelist if f'.{type}' in f]
        num_files += len([f for f in filelist if f'.{type}' in f])
    to_display.append(('Other data types', other_files))
    return to_display, directory_dir, num_files


def set_defaults(data, parameters):
    for i in 'fuzzy recon mel'.split(' '):
        data['project_info'][i] = parameters[i] if i in parameters else None


def all_file_content(file_path):
    try:
        f = open(file_path, 'r', encoding='utf-8')
        data = f.read()
        f.close()
    except:
        raise
        data = None
    return data


def file_content(file_path, display, command):
    if '.xml' in file_path:
        xslt_path = determine_file_type(file_path, display, command)
        xslt_path = os.path.join(BASE_DIR, 'styles', xslt_path)
        try:
            data = xml2html(file_path, xslt_path)
        except Exception:
            print(traceback.format_exc())
            data = '<p style="color: red">Problem handling this file, sorry!</p>'
    elif '.txt' in file_path or '.DAT' in file_path or '.DIS' in file_path:
        f = open(file_path, 'r', encoding='utf-8')
        data = f.read()
        f.close()
        data = '<pre>' + limit_lines(data, 30000) + '</pre>'
    elif '.csv' in file_path:
        # f = open(file_path, 'r')
        # data = f.read()
        # sniff the csv dialect
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            sample = csvfile.read(2048)
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample)
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, dialect)
            data = ''
            i = 0
            comments = []
            for row in reader:
                if "#" in row[0]:
                    comments.append('\t'.join(row))
                    continue
                i += 1
                if i == 1:
                    data += '<tr><thead>' + ''.join([f'<th>{r}</th>' for r in row]) + '</thead></tr>'
                else:
                    data += '<tr>' + ''.join([f'<td>{r}</td>' for r in row]) + '</tr>'
            data = '<div class="table-responsive">' + \
                   f'<table class="table table-sm table-hover table-bordered sets sortable">{data}</table>' + \
                   '</div>'
    else:
        data = '<p style="color: red">Not a type of file that can be displayed here, sorry!</p>'
    return data, get_info(file_path)


def get_info(path):
    try:
        stat = os.stat(os.path.join(BASE_DIR, 'projects', path))
        return time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(stat.st_mtime))
    except:
        return 'unknown'


def tree_info(tree):
    tree_list = projects.find_path(tree, 'all')
    return [(p, get_info(p)) for p in tree_list]


def download(full_path, filename):
    content = all_file_content(full_path)
    response = HTTPResponse()
    response.body = content
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    return response


def xml2html(xml_filename, xsl_filename):
    try:
        dom = ET.parse(xml_filename)
        xslt = ET.parse(xsl_filename)
        print(f'xsltproc.py {xsl_filename} {xml_filename}')
        transform = ET.XSLT(xslt)
        newdom = transform(dom)
    except:
        raise
    return newdom


def determine_file_type(file_path, display, command):
    if 'correspondences.xml' in file_path:
        return f'toc2html-{command}.xsl'
    elif 'parameters.xml' in file_path:
        return f'params2html-{command}.xsl'
    elif 'fuz.xml' in file_path:
        return 'fuzzy2html.xsl'
    elif 'data.xml' in file_path:
        if display == 'paragraph':
            return 'lexicon2html.xsl'
        else:
            return 'lexicon2table.xsl'
    elif 'sets.xml' in file_path:
        if display == 'paragraph':
            return 'sets2html.xsl'
        else:
            return 'sets2tabular.xsl'
    elif 'mel.xml' in file_path:
        return 'mel2html.xsl'
    elif 'coverage.statistics.xml' in file_path:
        return 'mel2html.xsl'
    elif 'statistics.xml' in file_path:
        return 'stats2html.xsl'
    elif 'compare.xml' in file_path:
        return 'compare_stats.xsl'


# this somewhat desperate function makes an html table from a tab- and newline- delimited string
def reformat(filecontent, max_rows):
    rows = filecontent.split('\n')
    rows = [r for r in rows if not '#' in r]
    rows = rows[:max_rows]
    header = rows[0]
    header = header.replace('\t', '<th>')
    header = '<thead><tr><th>' + header + '</thead>'
    rows = rows[1:]
    result = '<tr><td>'.join(rows)
    result = '<tbody><tr><td>' + result.replace('\t', '<td>')
    result += '</tbody></table>'
    return '<table width="100%" class="table table-striped sortable table-fixed">\n' + header + result


# this somewhat desperate function makes an html table from a tab- and newline- delimited string
def limit_lines(filecontent, max_rows):
    rows = filecontent.split('\n')
    num_rows = len(rows)
    rows = rows[:max_rows]
    message = ''
    if num_rows > max_rows:
        message = f'\n\n... and {num_rows - max_rows} more rows not shown.'
    return '\n'.join(rows) + message


# upstream for interactive only
def upstream(request, language_forms, project, parameters, only_with_mel):
    project_dir = combine_parts(PROJECTS, project)
    parameters_file = os.path.join(project_dir, f'{project}.master.parameters.xml')
    mel = parameters['mel'] if 'mel' in parameters and parameters['mel'] != '' else None
    recon = parameters['recon'] if 'recon' in parameters and parameters['recon'] != '' else None
    fuzzy = parameters['fuzzy'] if 'fuzzy' in parameters and parameters['fuzzy'] != '' else None
    settings = read.read_settings_file(parameters_file,
                                       mel=mel,
                                       fuzzy=fuzzy,
                                       recon=recon)
    attested_lexicons = read.create_lexicon_from_parms(language_forms)
    B = RE.interactive_upstream(settings, attested_lexicons=attested_lexicons, only_with_mel=only_with_mel)
    isolates = [(RE.correspondences_as_ids(i[0]), str(list(i[1])[0])) for i in B.statistics.singleton_support]
    return B.forms, B.statistics.notes, isolates, B.statistics.failed_parses, B.statistics.debug_notes


def setup_re(project, args, only_with_mel):
    print(time.asctime())
    elapsed_time = time.time()
    project_path = combine_parts(PROJECTS, project)
    parameters_file = combine_parts(PROJECTS, project, f'{project}.master.parameters.xml')
    settings = read.read_settings_file(parameters_file,
                                       mel=mel,
                                       fuzzy=fuzzy,
                                       recon=recon)
    load_hooks.load_hook(project_path, args, settings)
    mel_status = 'strict MELs' if only_with_mel else 'MELs not enforced'
    print(mel_status)


def run_up(project, settings, only_with_mel):
    B = RE.batch_all_upstream(settings, only_with_mel=only_with_mel)
    # print(f'wrote {len(B.statistics.keys)} keys and {len(B.statistics.failed_parses)} failures to {keys_file}')
    # print(f'wrote {len(B.forms)} text sets to {sets_file}')
    for c in sorted(B.statistics.correspondences_used_in_recons, key=lambda corr: corr.id):
        if c in B.statistics.correspondences_used_in_sets:
            set_count = B.statistics.correspondences_used_in_sets[c]
        else:
            set_count = 0
    print(f'{len(B.statistics.correspondences_used_in_recons)} correspondences used')
    B.isolates = RE.extract_isolates(B)
    B.failures = RE.ProtoForm('failed', (), sorted(B.statistics.failed_parses, key=lambda x: x.language), (), [])
    # print(f'wrote {len(B.forms)} xml sets, {len(B.failures.supporting_forms)} failures and {len(B.isolates)} isolates to {sets_xml_file}')
    B.statistics.add_stat('isolates', len(B.isolates))
    B.statistics.add_stat('sets', len(B.forms))
    B.statistics.add_stat('sankey',
                          f'{len(B.isolates)},{len(B.failures.supporting_forms)},{B.statistics.summary_stats["reflexes"]}')
    print(time.asctime())


VERSION = get_version()
