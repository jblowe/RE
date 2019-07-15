import os, time, sys
import lxml.etree as ET

# we need some code from the sibling directory where the rest of the RE code lives
sys.path.append("../src")

import projects
import RE, read

# nb: we are trying to get the directory above the directory this file is in
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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


def add_time_and_version():
    return 'code and data version: %s, system last restarted: %s' % (
        get_version(), time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()))


def list_experiments(project):
    project_dir = projects.projects[project]
    experiment_dirs = [f for f in sorted(os.listdir(os.path.join(project_dir, 'experiments'))) if os.path.isdir(os.path.join(project_dir, 'experiments', f))]
    experiments = []
    data_elements = 'name,updated,canon,correspondences,strict,mel,fuzzy,classes,lexicons,results'.split(',')
    for x in experiment_dirs:
        experiments.append(get_experiment_info(project_dir, x, data_elements, project))
    return experiments, BASE_DIR, data_elements


def get_experiment_info(project_dir, experiment, data_elements, project):
    parameters_file = os.path.join(project_dir, 'experiments', experiment, f'{project}.default.parameters.xml')
    experiment_info = (experiment,) + (get_info(parameters_file),) + tuple(data_elements[2:])
    settings = read.read_settings_file(parameters_file,
                                       mel='none',
                                       recon='default')
    for s in settings.other:
        pass
    # dom = ET.parse(parameters_file)
    # experiment_info = (experiment, 'date', settings.mel_filename,
    return experiment_info


def data_files(project):
    project_dir = projects.projects[project]
    filelist = [f for f in sorted(os.listdir(project_dir)) if os.path.isfile(os.path.join(project_dir, f))]
    # filelist = [f for f in filelist if '.xml' in f]
    to_display = []
    for type in 'parameters statistics compare correspondences mel sets data'.split(' '):
        to_display.append((f'{type}', [f for f in filelist if f'{type}.xml' in f]))
    for type in 'correspondences data u8 keys'.split(' '):
        to_display.append((f'{type} csv', [f for f in filelist if f'{type}.csv' in f]))
    for type in 'statistics keys sets coverage'.split(' '):
        to_display.append((f'{type} txt', [f for f in filelist if f'{type}.txt' in f]))
    for type in 'DAT'.split(' '):
        to_display.append((type, [f for f in filelist if f'.{type}' in f]))
    return to_display, BASE_DIR


def all_file_content(file_path):
    # file_path contains the project and filename, e.g. TGTM/TGTM.mel.xml
    (project, filename) = file_path.split('/')
    file_path = os.path.join(projects.projects[project], filename)
    f = open(file_path, 'r')
    data = f.read()
    f.close()
    return data, project


def file_content(file_path):
    # file_path contains the project and filename, e.g. TGTM/TGTM.hand.mel.xml
    (project, filename) = file_path.split('/')
    file_path = os.path.join(projects.projects[project], filename)
    if '.xml' in file_path:
        xslt_path = determine_file_type(file_path)
        xslt_path = os.path.join(BASE_DIR, 'styles', xslt_path)
        try:
            data = xml2html(file_path, xslt_path)
        except:
            data = '<span style="color: red">Problem handling this file, sorry!</span>'
    elif '.txt' in file_path or '.DAT' in file_path:
        f = open(file_path, 'r')
        data = f.read()
        f.close()
        data = '<pre>' + limit_lines(data, 5000) + '</pre>'
    elif '.csv' in file_path:
        f = open(file_path, 'r')
        data = f.read()
        f.close()
        data = reformat(data, 5000)
    return data, project, get_info(file_path)


def get_info(path):
    try:
        stat = os.stat(os.path.join(BASE_DIR, 'projects', path))
        return time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(stat.st_mtime))
    except:
        return 'unknown'


def project_info():
    # project_dir = os.path.join(BASE_DIR, 'projects', project)
    # filelist = [f for f in os.listdir(project_dir) if os.path.isfile(os.path.join(project_dir, f))]
    return [(p, get_info(p), projects.projects[p]) for p in projects.projects]


def xml2html(xml_filename, xsl_filename):

    dom = ET.parse(xml_filename)
    xslt = ET.parse(xsl_filename)
    transform = ET.XSLT(xslt)
    newdom = transform(dom)
    return newdom


def determine_file_type(file_path):
    if 'correspondences.xml' in file_path:
        return 'toc2html.xsl'
    elif 'data.xml' in file_path:
        return 'lexicon2html.xsl'
    elif 'parameters.xml' in file_path:
        return 'params2html.xsl'
    elif 'sets.xml' in file_path:
        return 'sets2html.xsl'
    elif 'mel.xml' in file_path:
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
    return '<table width="100%" class="table table-striped sortable">\n' + header + result


# this somewhat desperate function makes an html table from a tab- and newline- delimited string
def limit_lines(filecontent, max_rows):
    rows = filecontent.split('\n')
    num_rows = len(rows)
    rows = rows[:max_rows]
    message = ''
    if num_rows > max_rows:
        message = f'\n\n... and {num_rows - max_rows} more rows not shown.'
    return '\n'.join(rows) + message


def upstream(request, language_forms, project, only_with_mel):
    project_dir = projects.projects[project]
    parameters_file = os.path.join(project_dir, f'{project}.default.parameters.xml')
    settings = read.read_settings_file(parameters_file,
                                       mel='none',
                                       recon='default')
    if request == 'languages':
        return settings.upstream[settings.upstream_target], settings.upstream_target, project_dir
    elif request == 'upstream':
        attested_lexicons = read.create_lexicon_from_parms(language_forms)
        B = RE.batch_all_upstream(settings, attested_lexicons=attested_lexicons, only_with_mel=only_with_mel)
        isolates = [(RE.correspondences_as_ids(i[0]), str(list(i[1])[0])) for i in B.statistics.singleton_support]
        return B.forms, B.statistics.notes, isolates, B.statistics.failed_parses, B.statistics.debug_notes
    pass

def show_experiment(project_dir, experiment):
    pass

VERSION = get_version()
