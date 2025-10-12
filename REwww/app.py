from bottle import Bottle, HTTPResponse, default_app, post, request, run, route, template, debug, static_file, BaseTemplate

import os
import sys
import shutil
from shutil import copy
sys.path.append(os.path.join('..', 'src'))
import read
import load_hooks
import time
# from adapter import *

# we need some code from the sibling directory where the rest of the RE code lives

# this path is valid on 'local' deployments
sys.path.append(os.path.join('..', 'src'))

# this path is only valid on pythonanywhere
sys.path.append(os.path.join('RE', 'src'))

import wutils
import run_make
import RE

dirname = os.path.dirname(os.path.abspath(__file__))

# add version and start timestamp to footer
BaseTemplate.defaults['footer_info'] = wutils.add_time_and_version()


@route('/static/<filename:re:.*\\.(ico|jpg|png|gif)>')
def send_ico(filename):
    return static_file(filename, root=dirname + os.sep + os.path.join('static', 'asset', 'images'))


@route('/static/<filename:re:.*\\.css(.map)?>')
def send_css(filename):
    return static_file(filename, root=dirname + os.sep + os.path.join('static', 'asset', 'css'))


@route('/static/<filename:re:.*\\.js(.map)?>')
def send_js(filename):
    return static_file(filename, root=dirname + os.sep + os.path.join('static', 'asset', 'js'))


@route('/webfonts/<filename:re:.*\\.(woff2?|ttf|svg)>')
def send_font(filename):
    return static_file(filename, root=dirname + os.sep + os.path.join('static', 'asset', 'webfonts'))


@route('/')
def index():
    data = {'home': 'here'}
    return wutils.check_template('index', data, request.forms)


@route('/about')
def about():
    data = {'about': 'here'}
    return wutils.check_template('index', data, request.forms)


@route('/list_tree/<tree:re:.*>')
def list_tree(tree):
    tree_info = wutils.tree_info(tree)
    data = {tree: tree_info}
    return wutils.check_template('index', data, request.forms)


# @route('/edit/<subcommand:re:.*>')
@post('/edit/<tree:re:.*>/<project:re:.*>/<filename:re:.*>')
@route('/edit/<tree:re:.*>/<project:re:.*>/<filename:re:.*>')
def edit(tree, project, filename):
    x = request
    origin = wutils.get_origin(request)
    if request.POST.action == 'save':
        pass
    elif request.POST.action == 'upstream':
        pass
    elif request.POST.action == 'exit':
        pass
    # subcommand = request.GET.get('action')
    # try:
    #     (tree, project, file) = subcommand.replace('/', '').split('|')
    # except Exception:
    #     tree, project, file = 5 * []
    # if subcommand == 'edit':
    #     pass
    display = ''
    command = 'edit'
    data = wutils.setup_data(tree, project, filename, display, command, origin)
    data['content'] = str(data['content'])
    data['content'] = data['content'].replace('#document_path#', f'{tree}/{project}/{filename}')
    return wutils.check_template('index', data, request.forms)


@route('/project/<project:re:.*>')
def project_info(project):
    files, base_dir, num_files = wutils.data_files(wutils.PROJECTS, project)
    data = {'tree': 'projects', 'project': project, 'files': files, 'base_dir': base_dir, 'num_files': num_files,
            'project_info': wutils.get_project_info(project, [])}
    return wutils.check_template('index', data, request.forms)


@route('/get_file/<tree:re:.*>/<project:re:.*>/<filename:re:.*>')
def get_project(tree, project, filename):
    display = 'paragraph' if 'paragraph' in request.GET else 'tabular'
    command = 'edit' if 'edit' in request.GET else 'view'
    origin = wutils.get_origin(request)
    data = wutils.setup_data(tree, project, filename, display, command, origin)
    return wutils.check_template('index', data, request.forms)


@route('/download_file/<tree:re:.*>/<project:re:.*>/<filename:re:.*>')
def download_project(tree, project, filename):
    full_path = wutils.combine_parts(tree, project, filename)
    return wutils.download(full_path, filename)


@post('/compare/<project:re:.*>')
def compare(project):
    runs = [i.replace(f'{project}.', '').replace('.sets.xml', '') for i in request.forms if i not in 'compare'.split()]
    alerts, success = run_make.compare(project, runs)
    errors = alerts if not success else None
    messages = alerts if success else None
    return show_project(project, messages, errors)


# one cycle through interactive environment
@post('/interactive/<project:re:.*>')
@route('/interactive/<project:re:.*>')
def interactive_upstream(project):
    # initialize the interactive form
    x = request
    files, base_dir, num_files = wutils.data_files(wutils.PROJECTS, project)
    if request.method == 'GET':
        parameters_file = os.path.join(base_dir, f'{project}.master.parameters.xml')
        settings = read.read_settings_file(parameters_file)
        # check_setup(command_args.command, args, settings)
        languages = [(l, '') for l in settings.attested]
        forms = []
        notes = []
        isolates = []
        no_parses = []
        debug_notes = []
    # take the submitted values, upstream
    else:
        languages = [(i, getattr(request.forms, i)) for i in request.forms if i not in 'fuzzy recon mel make'.split(' ')]
        RE.Debug.debug = True
        forms, notes, isolates, no_parses, debug_notes = wutils.upstream('interactive', languages, project, request.forms, False)
        no_parses = [n for n in no_parses if n.glyphs != '']
        notes = [n for n in notes if 'form missing' not in n]
    project_info = wutils.get_project_info(project, [])
    # language_names, upstream_target, base_dir = wutils.upstream('languages', [], project, request.forms, False)
    # clean out unused elements from upstream results
    data = {'interactive': 'start', 'project': project, 'languages': languages,
            'base_dir': base_dir, 'forms': forms, 'notes': notes, 'debug_notes': debug_notes, 'isolates': isolates, 'no_parses': no_parses,
            'project_info': project_info}
    return wutils.check_template('index', data, request.forms)


@route('/prxject/<project:re:.*>')
def show_project(project, messages=None, errors=None):
    files, base_dir, num_files = wutils.data_files(wutils.PROJECTS, project)
    data = {'tree': 'projects', 'project': project, 'files': files, 'base_dir': base_dir, 'num_files': num_files,
            'project_info': wutils.get_project_info(project, [])}
    if messages: data['messages'] = messages
    if errors: data['errors'] = errors
    if num_files == 0:
        data['errors'] = ['No files in this project!']
    return wutils.check_template('index', data, request.forms)


@post('/create-project/<project:re:.*>')
def new_project(project):
    project_dir = os.path.join('..', 'projects', project)
    error_messages = []
    new_project = getattr(request.forms, 'new_project')
    try:
        new_dir = os.path.join(base_dir, new_project)
        os.mkdir(new_dir)
        for root, dirs, files in os.walk(project_dir):
            for f in files:
                print(os.path.join(root, f))
                copy(os.path.join(root, f), new_dir)
    except:
        error_messages.append(f"couldn't make project {new_project}")
    projects, base_dir, data_elements = wutils.list_of_projects(project)
    data = {'projects': wutils.tree_info('projects'), 'projects': projects,
            'project': project, 'base_dir': base_dir,
            'data_elements': data_elements, 'back': '/list_tree/projects'}
    if len(error_messages) > 0:
        data['errors'] = error_messages
    return list_tree('projects')
    # return wutils.check_template('index', data, request.forms)


@route('/delete-project/<project:re:.*>')
def delete_project(project):
    try:
        delete_dir = wutils.combine_parts(PROJECTS, project)
        shutil.rmtree(delete_dir)
    except:
        pass
    return list_tree('projects')


@post('/remake')
def remake():
    data = {'make': run_make.make('ALL', None, None)}
    response = HTTPResponse()
    response.body = str(data['make'][1])
    return response


@route('/make/ALL')
def make_all():
    data = {'make': run_make.make('ALL', None, None), 'project': 'ALL'}
    return wutils.check_template('index', data, request.forms)


@post('/make/<project:re:.*>')
@route('/make/<project:re:.*>')
def make_project(project):
    alerts, success = run_make.make(project, request.forms)
    errors = alerts if not success else None
    messages = alerts if success else None
    return show_project(project, messages, errors)


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

# allow user to set run parameters at startup for development. on the web, this is done via wsgi/apache
if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(description="Run the Bottle app.")
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=3002)
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    run(host=args.host, port=args.port, debug=args.debug)

