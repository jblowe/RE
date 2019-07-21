import os, time, sys
import lxml.etree as ET

# we need some code from the sibling directory where the rest of the RE code lives
sys.path.append("../src")

import projects
import RE, read

# nb: we are trying to get the directory above the directory this file is in
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS = 'projects'
EXPERIMENTS = 'experiments'

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

def combine_parts(*args):
    x = args
    return os.path.join('..', *args)


def list_experiments(project):
    experiment_dir = combine_parts(EXPERIMENTS, project)
    experiment_dirs = [f for f in sorted(os.listdir(experiment_dir)) if os.path.isdir(os.path.join(experiment_dir, f))]
    experiments = []
    data_elements = 'name,updated,canon,correspondences,strict,mel,fuzzy,classes,lexicons,results'.split(',')
    for x in experiment_dirs:
        experiments.append(get_experiment_info(experiment_dir, x, data_elements, project))
    return experiments, experiment_dir, data_elements


def get_experiment_info(experiment_dir, experiment, data_elements, project):
    parameters_file = os.path.join(experiment_dir, experiment, f'{project}.default.parameters.xml')
    experiment_info = (experiment,) + (get_info(parameters_file),) + tuple(data_elements[2:])
    if experiment_info[1] == 'unknown':
        pass
    else:
        settings = read.read_settings_file(parameters_file,
                                           mel='none',
                                           recon='default')
        for s in settings.other:
            pass
        # dom = ET.parse(parameters_file)
        # experiment_info = (experiment, 'date', settings.mel_filename,

    return experiment_info


def data_files(tree, directory):
    directory_dir = projects.find_path(tree, directory)
    filelist = [f for f in sorted(os.listdir(directory_dir)) if os.path.isfile(os.path.join(directory_dir, f))]
    # filelist = [f for f in filelist if '.xml' in f]
    to_display = []
    num_files = 0
    for type in 'parameters correspondences mel data'.split(' '):
        to_display.append((f'{type}', [f for f in filelist if f'{type}.xml' in f]))
        num_files += len([f for f in filelist if f'{type}.xml' in f])
    for type in 'statistics compare sets'.split(' '):
        to_display.append((f'{type}', [f for f in filelist if f'{type}.xml' in f]))
        num_files += len([f for f in filelist if f'{type}.xml' in f])
    for type in 'correspondences data u8 keys'.split(' '):
        to_display.append((f'{type} csv', [f for f in filelist if f'{type}.csv' in f]))
        num_files += len([f for f in filelist if f'{type}.csv' in f])
    for type in 'statistics keys sets coverage'.split(' '):
        to_display.append((f'{type} txt', [f for f in filelist if f'{type}.txt' in f]))
        num_files += len([f for f in filelist if f'{type}.txt' in f])
    other_files = []
    for type in 'DAT DIS csv xls xlsx ods'.split(' '):
        [other_files.append(f) for f in filelist if f'.{type}' in f]
        num_files += len([f for f in filelist if f'.{type}' in f])
    to_display.append(('Other data types', other_files))
    return to_display, directory_dir, num_files


def all_file_content(file_path):
    try:
        f = open(file_path, 'r')
        data = f.read()
        f.close()
    except:
        data = None
    return data


def file_content(file_path):
    if '.xml' in file_path:
        xslt_path = determine_file_type(file_path)
        xslt_path = os.path.join(BASE_DIR, 'styles', xslt_path)
        try:
            data = xml2html(file_path, xslt_path)
        except:
            data = '<p style="color: red">Problem handling this file, sorry!</p>'
    elif '.txt' in file_path or '.DAT' in file_path or '.DIS' in file_path:
        f = open(file_path, 'r')
        data = f.read()
        f.close()
        data = '<pre>' + limit_lines(data, 5000) + '</pre>'
    elif '.csv' in file_path:
        f = open(file_path, 'r')
        data = f.read()
        f.close()
        data = reformat(data, 5000)
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
    # project_dir = os.path.join(BASE_DIR, 'projects', project)
    # filelist = [f for f in os.listdir(project_dir) if os.path.isfile(os.path.join(project_dir, f))]
    tree_list = projects.find_path(tree, 'all')
    return [(p, get_info(p)) for p in tree_list]


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
    project_dir = projects.find_path(EXPERIMENTS, project)
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


VERSION = get_version()
