from bottle import Bottle, HTTPResponse, default_app, post, request, run, route, template, debug, static_file, BaseTemplate

import os
import sys
import shutil
from shutil import copy

# we need some code from the sibling directory where the rest of the RE code lives

# this path is valid on 'local' deployments
sys.path.append(os.path.join('..', 'src'))

# this path is only valid on pythonanywhere
sys.path.append(os.path.join('RE', 'src'))

import utils
import run_make
import RE

dirname = os.path.dirname(os.path.abspath(__file__))

# add version and start timestamp to footer
BaseTemplate.defaults['footer_info'] = utils.add_time_and_version()


@route('/static/<filename:re:.*\.(ico|jpg|png|gif)>')
def send_ico(filename):
    return static_file(filename, root=dirname + os.sep + os.path.join('static', 'asset', 'images'))


@route('/static/<filename:re:.*\.css(.map)?>')
def send_css(filename):
    return static_file(filename, root=dirname + os.sep + os.path.join('static', 'asset', 'css'))


@route('/static/<filename:re:.*\.js(.map)?>')
def send_js(filename):
    return static_file(filename, root=dirname + os.sep + os.path.join('static', 'asset', 'js'))


@route('/webfonts/<filename:re:.*\.(woff2?|ttf|svg)>')
def send_font(filename):
    return static_file(filename, root=dirname + os.sep + os.path.join('static', 'asset', 'webfonts'))


@route('/')
def index():
    data = {'home': 'here'}
    return utils.check_template('index', data, request.forms)


@route('/about')
def index():
    data = {'about': 'here'}
    return utils.check_template('index', data, request.forms)


@route('/list_tree/<tree:re:.*>')
def list_tree(tree):
    tree_info = utils.tree_info(tree)
    data = {tree: tree_info}
    return utils.check_template('index', data, request.forms)


@route('/project/<project:re:.*>')
def project(project):
    files, base_dir, num_files = utils.data_files(utils.PROJECTS, project)
    data = {'tree': 'projects', 'project': project, 'files': files, 'base_dir': base_dir}
    return utils.check_template('index', data, request.forms)


@route('/get_file/<tree:re:.*>/<project:re:.*>/<experiment:re:.*>/<filename:re:.*>')
def get_experiment_file(tree, project, experiment, filename):
    full_path = utils.combine_parts(tree, project, experiment, filename)
    experiments, exp_proj_path, data_elements = utils.list_of_experiments(project)
    experiment_info = utils.get_experiment_info(exp_proj_path, experiment, data_elements, project)

    display = 'paragraph' if 'paragraph' in request.GET else 'tabular'
    content, date = utils.file_content(full_path, display)
    experiments, base_dir, data_elements = utils.list_of_experiments(project)
    files, experiment_path, num_files = utils.data_files(os.path.join(utils.EXPERIMENTS, project), experiment)
    data = {'tree': tree, 'project': project, 'experiment': experiment, 'files': files, 'base_dir': base_dir,
            'num_files': num_files, 'experiment_info': experiment_info, 'filename': filename, 'date': date,
            'content': content, 'data_elements': data_elements, 'back': '/list_tree/projects'}
    return utils.check_template('index', data, request.forms)


@route('/get_file/<tree:re:.*>/<project:re:.*>/<filename:re:.*>')
def get_project(tree, project, filename):
    full_path = utils.combine_parts(tree, project, filename)
    display = 'paragraph' if 'paragraph' in request.GET else 'tabular'
    content, date = utils.file_content(full_path, display)
    files, base_dir, num_files = utils.data_files(tree, project)
    data = {'tree': tree, 'project': project, 'files': files, 'base_dir': base_dir, 'filename': filename,
            'source': 'Source data', 'date': date, 'content': content}
    return utils.check_template('index', data, request.forms)


def download(full_path, filename):
    content = utils.all_file_content(full_path)
    response = HTTPResponse()
    response.body = content
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    return response


@route('/download_file/<tree:re:.*>/<project:re:.*>/<experiment:re:.*>/<filename:re:.*>')
def download_experiment(tree, project, experiment, filename):
    full_path = utils.combine_parts(tree, project, filename)
    return download(full_path, filename)


@route('/download_file/<tree:re:.*>/<project:re:.*>/<filename:re:.*>')
def download_project(tree, project, filename):
    full_path = utils.combine_parts(tree, project, filename)
    return download(full_path, filename)


@post('/compare/<project:re:.*>/<experiment:re:.*>')
def compare(project, experiment):
    x = request.forms
    runs = [i.replace(f'{project}.', '').replace('.sets.xml', '') for i in request.forms if i not in 'compare'.split()]
    alerts, success = run_make.compare(project, experiment, runs)
    errors = alerts if not success else None
    messages = alerts if success else None
    return show_experiment(project, experiment, messages, errors)


# one cycle through interactive environment
@post('/interactive/<project:re:.*>/<experiment:re:.*>')
def upstream(project, experiment):
    languages = [(i, getattr(request.forms, i)) for i in request.forms if i not in 'fuzzy recon mel make'.split(' ')]
    RE.Debug.debug = True
    experiments, exp_proj_path, data_elements = utils.list_of_experiments(project)
    experiment_info = utils.get_experiment_info(exp_proj_path, experiment, data_elements, project)
    language_names, upstream_target, base_dir = utils.upstream('languages', [], project, experiment, request.forms, False)
    forms, notes, isolates, no_parses, debug_notes = utils.upstream('upstream', languages, project, experiment, request.forms, False)
    # clean out unused elements from upstream results
    no_parses = [n for n in no_parses if n.glyphs != '']
    notes = [n for n in notes if 'form missing' not in n]
    data = {'interactive': 'start', 'project': project, 'experiment': experiment, 'languages': languages, 'base_dir': base_dir,
            'forms': forms, 'notes': notes, 'debug_notes': debug_notes, 'isolates': isolates, 'no_parses': no_parses,
            'experiment_info': experiment_info}
    return utils.check_template('index', data, request.forms)


# initial setup of interactive environment
@route('/interactive/<project:re:.*>/<experiment:re:.*>')
def interactive_project(project, experiment):
    files, experiment_path, num_files = utils.data_files(os.path.join(utils.EXPERIMENTS, project), experiment)
    experiments, exp_proj_path, data_elements = utils.list_of_experiments(project)
    experiment_info = utils.get_experiment_info(exp_proj_path, experiment, data_elements, project)
    if num_files == 0:
        experiments, base_dir, data_elements = utils.list_of_experiments(project)
        data = {'experiments': experiments, 'project': project, 'base_dir': base_dir,
                'data_elements': data_elements, 'errors': ['No files in this experiment!']}
    else:
        languages, upstream_target, base_dir = utils.upstream('languages', [], project, experiment, request.forms, True)
        languages = [(l, '') for l in languages]
        data = {'interactive': 'start', 'project': project, 'experiment': experiment, 'languages': languages,
                'base_dir': base_dir, 'back': '/list_tree/projects', 'experiment_info': experiment_info}
    return utils.check_template('index', data, request.forms)


@route('/experiment/<project:re:.*>/<experiment:re:.*>')
def show_experiment(project, experiment, messages=None, errors=None):
    experiments, exp_proj_path, data_elements = utils.list_of_experiments(project)
    experiment_info = utils.get_experiment_info(exp_proj_path, experiment, data_elements, project)
    files, experiment_path, num_files = utils.data_files(os.path.join(utils.EXPERIMENTS, project), experiment)
    data = {'tree': 'experiment', 'experiment': experiment, 'project': project, 'base_dir': experiment_path,
            'data_elements': data_elements, 'experiment_info': experiment_info, 'files': files, 'num_files': num_files,
            'back': '/list_tree/projects'}
    if messages: data['messages'] = messages
    if errors: data['errors'] = errors
    if num_files == 0:
        data['errors'] = ['No files in this experiment!']
    return utils.check_template('index', data, request.forms)


@post('/new/<project:re:.*>')
def new_experiment(project):
    experiments, base_dir, data_elements = utils.list_of_experiments(project)
    project_dir = os.path.join('..', 'projects', project)
    error_messages = []
    new_experiment = getattr(request.forms, 'new_experiment')
    try:
        new_dir = os.path.join(base_dir, new_experiment)
        os.mkdir(new_dir)
        for root, dirs, files in os.walk(project_dir):
            for f in files:
                print(os.path.join(root, f))
                copy(os.path.join(root, f), new_dir)
            break
    except:
        error_messages.append(f"couldn't make experiment {new_experiment}")
    experiments, base_dir, data_elements = utils.list_of_experiments(project)
    data = {'projects': utils.tree_info('projects'), 'experiments': experiments,
            'project': project, 'base_dir': base_dir,
            'data_elements': data_elements, 'back': '/list_tree/projects'}
    if len(error_messages) > 0:
        data['errors'] = error_messages
    # return list_tree('projects')
    return utils.check_template('index', data, request.forms)


@route('/delete/<project:re:.*>/<experiment:re:.*>')
def delete_experiment(project, experiment):
    try:
        experiments, exp_proj_path, data_elements = utils.list_of_experiments(project)
        delete_dir = os.path.join(exp_proj_path, experiment)
        shutil.rmtree(delete_dir)
    except:
        pass
    return list_tree('projects')


@route('/experiments/<project:re:.*>')
def list_experiments(project):
    experiments, base_dir, data_elements = utils.list_of_experiments(project)
    data = {'experiments': experiments, 'project': project, 'base_dir': base_dir,
            'data_elements': data_elements}
    return utils.check_template('index', data, request.forms)


@post('/remake')
def remake():
    data = {'make': run_make.make('ALL', None, None)}
    response = HTTPResponse()
    response.body = str(data['make'][1])
    return response


@route('/make/ALL')
def make_all():
    data = {'make': run_make.make('ALL', None, None), 'project': 'ALL', 'experiment': 'semantics'}
    return utils.check_template('index', data, request.forms)


@post('/make/<project:re:.*>/<experiment:re:.*>')
@route('/make/<project:re:.*>/<experiment:re:.*>')
def make_experiment(project, experiment):
    alerts, success = run_make.make(project, experiment, request.forms)
    errors = alerts if not success else None
    messages = alerts if success else None
    return show_experiment(project, experiment, messages, errors)


@route('/plot/<type:re:.*>/<data:re:.*>')
def plot(type, data):
    import numpy as np
    import matplotlib.pyplot as plt
    plt.close()
    if type == 'venn':
        from matplotlib_venn import venn2
        t = tuple([int(t) for t in data.split(',')])
        # plt.figure()  # needed to avoid adding curves in plot
        venn2(subsets=t, set_labels=('Cognate sets 1', 'Cognate sets 2'))
        plt.title('Set overlap')

    elif type == 'sankey':
        from matplotlib.sankey import Sankey
        # three values come in: isolates, failures, total forms
        counts = [int(t) for t in data.split(',')]
        # create 'in sets' count using the other two values
        counts[2] = counts[2] - int(counts[0] + counts[1])
        sum_triple = sum(counts)
        counts = [-sum_triple] + counts
        flows = [-(100 * t / sum_triple) for t in counts]
        labels = 'all forms,isolates,failures,in sets'.split(',')
        labels = [f'{labels[i]} ({abs(counts[i])})' for i in range(len(labels))]
        orientations = [0, 1, 1, 0]
        pathlengths = [0.25, 0.25, 0.25, 0.25]
        Sankey(unit='%', scale=0.01, pathlengths=pathlengths, format='%.0f', flows=flows, labels=labels, orientations=orientations).finish()
        plt.title("Sankey diagram")

    from io import BytesIO
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)

    headers = {
        'Content-Type': 'image/png'
    }
    return HTTPResponse(figfile.getvalue(), **headers)

    # response = HTTPResponse(content_type="image/png")
    # response.body = figfile
    # return response


# application = default_app()
run()
