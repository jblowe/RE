import os, time, sys
import lxml.etree as ET

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
    return os.path.join('..', *args)


def check_template(tpl, data, parameters):
    if 'back' not in data:
        data['back'] = '/list_tree/projects'
    if 'experiment_info' in data:
        for i in 'fuzzy recon mel'.split(' '):
            data['experiment_info'][i] = parameters[i] if i in parameters else ''
    return template(tpl, data=data)


def list_of_experiments(project):
    experiment_dir = combine_parts(EXPERIMENTS, project)
    if not os.path.isdir(experiment_dir):
        os.mkdir(experiment_dir)
    experiment_dirs = [f for f in sorted(os.listdir(experiment_dir)) if os.path.isdir(os.path.join(experiment_dir, f))]
    experiments = []
    data_elements = 'name,updated,canon,correspondences,strict,mel,fuzzy,classes,lexicons,results'.split(',')
    for x in experiment_dirs:
        experiments.append(get_experiment_info(experiment_dir, x, data_elements, project))
    return experiments, experiment_dir, data_elements


def get_experiment_info(experiment_dir, experiment, data_elements, project):
    parameters_file = os.path.join(experiment_dir, experiment, f'{project}.master.parameters.xml')
    experiment_info ={'name': experiment, 'date': get_info(parameters_file)}
    if experiment_info['date'] == 'unknown':
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
                experiment_info[s] = settings.other[s]

        # experiment_info['upstream'] = settings.upstream
        # experiment_info['attested'] = settings.attested
        # dom = ET.parse(parameters_file)
        # experiment_info = (experiment, 'date', settings.mel_filename,

    return experiment_info


def data_files(tree, directory):
    directory_dir = projects.find_path(tree, directory)
    filelist = [f for f in sorted(os.listdir(directory_dir)) if os.path.isfile(os.path.join(directory_dir, f))]
    # filelist = [f for f in filelist if '.xml' in f]
    to_display = []
    num_files = 0
    for type in 'statistics compare sets'.split(' '):
        to_display.append((f'{type}', [f for f in filelist if f'{type}.xml' in f]))
        num_files += len([f for f in filelist if f'{type}.xml' in f])
    for type in 'parameters correspondences mel data fuz'.split(' '):
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


def set_defaults(data, parameters):
    for i in 'fuzzy recon mel'.split(' '):
        data['experiment_info'][i] = parameters[i] if i in parameters else None


def all_file_content(file_path):
    try:
        f = open(file_path, 'r')
        data = f.read()
        f.close()
    except:
        data = None
    return data


def file_content(file_path, display):
    if '.xml' in file_path:
        xslt_path = determine_file_type(file_path, display)
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
    tree_list = projects.find_path(tree, 'all')
    return [(p, get_info(p)) for p in tree_list]


def xml2html(xml_filename, xsl_filename):
    dom = ET.parse(xml_filename)
    xslt = ET.parse(xsl_filename)
    transform = ET.XSLT(xslt)
    newdom = transform(dom)
    return newdom


def determine_file_type(file_path, display):
    if 'correspondences.xml' in file_path:
        return 'toc2html.xsl'
    elif 'data.xml' in file_path:
        return 'lexicon2html.xsl'
    elif 'parameters.xml' in file_path:
        return 'params2html.xsl'
    elif 'fuz.xml' in file_path:
        return 'fuzzy2html.xsl'
    elif 'sets.xml' in file_path:
        if display == 'paragraph':
            return 'sets2html.xsl'
        else:
            return 'sets2tabular.xsl'
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


def upstream(request, language_forms, project, experiment, parameters, only_with_mel):
    project_dir = os.path.join('..', EXPERIMENTS, project, experiment)
    parameters_file = os.path.join(project_dir, f'{project}.master.parameters.xml')
    if request == 'languages':
        mel = None
        fuzzy = None
        recon = 'standard'
        settings = read.read_settings_file(parameters_file,
                                           mel=mel,
                                           fuzzy=fuzzy,
                                           recon=recon)
        return settings.upstream[settings.upstream_target], settings.upstream_target, project_dir
    elif request == 'upstream':
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
    pass


VERSION = get_version()
