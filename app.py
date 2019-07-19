from bottle import Bottle, HTTPResponse, default_app, post, request, run, route, template, debug, static_file, \
    Jinja2Template, BaseTemplate

import os
import sys
from shutil import copy
import utils
import run_make
import RE

dirname = os.path.dirname(os.path.abspath(__file__))

app = Bottle()
debug(True)

# add version and start timestamp to footer
BaseTemplate.defaults['footer_info'] = utils.add_time_and_version()


@app.route('/static/<filename:re:.*\.css>')
def send_css(filename):
    return static_file(filename, root=dirname + '/static/asset/css')


@app.route('/static/<filename:re:.*\.js>')
def send_js(filename):
    return static_file(filename, root=dirname + '/static/asset/js')


@app.route('/fonts/<filename:re:.*\.(woff|ttf).*>')
def send_font(filename):
    return static_file(filename, root=dirname + '/static/asset/fonts')


@app.route('/')
def index():
    data = {'home': 'here'}
    return template('index', data=data)


@app.route('/about')
def index():
    data = {'about': 'here'}
    return template('index', data=data)


@app.route('/list_tree/<tree:re:.*>')
def list_tree(tree):
    tree_info = utils.tree_info(tree)
    data = {tree: tree_info}
    return template('index', data=data)


@app.route('/project/<project_name:re:.*>')
def project(project_name):
    files, base_dir = utils.data_files(utils.PROJECTS, project_name)
    data = {'tree': 'projects', 'project': project_name, 'files': files, 'base_dir': base_dir}
    return template('index', data=data)


@app.route('/get_file/<tree:re:.*>/<project_name:re:.*>/<filename:re:.*>')
def get_project(tree, project_name, filename):
    full_path = utils.combine_parts(tree, project_name, filename)
    content, date = utils.file_content(full_path)
    files, base_dir = utils.data_files(tree, project_name)
    data = {'tree': tree, 'project': project_name, 'files': files, 'base_dir': base_dir, 'filename': filename, 'date': date, 'content': content}
    return template('index', data=data)


@app.route('/get_file/<tree:re:.*>/<project_name:re:.*>/<experiment:re:.*>/<filename:re:.*>')
def get_experiment(tree, project_name, experiment, filename):
    full_path = utils.combine_parts(tree, project_name, experiment, filename)
    content, date = utils.file_content(full_path)
    files, base_dir = utils.data_files(tree, project_name)
    data = {'tree': tree, 'project': project_name, 'experiment': experiment, 'files': files, 'base_dir': base_dir, 'filename': filename, 'date': date, 'content': content}
    return template('index', data=data)


def download(full_path, filename):
    content = utils.all_file_content(full_path)
    response = HTTPResponse()
    response.body = content
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    return response


@app.route('/download_file/<tree:re:.*>/<project_name:re:.*>/<experiment:re:.*>/<filename:re:.*>')
def download_experiment(tree, project_name, filename):
    full_path = utils.combine_parts(tree, project_name, filename)
    return download(full_path, filename)


@app.route('/download_file/<tree:re:.*>/<project_name:re:.*>/<filename:re:.*>')
def download_project(tree, project_name, filename):
    full_path = utils.combine_parts(tree, project_name, filename)
    return download(full_path, filename)


@app.post('/interactive/<project_name:re:.*>')
def upstream(project_name):
    languages = [(i, getattr(request.forms, i)) for i in request.forms]
    RE.Debug.debug = True
    language_names, upstream_target, base_dir = utils.upstream('languages', [], project_name, True)
    forms, notes, isolates, no_parses, debug_notes = utils.upstream('upstream', languages, project_name, True)
    data = {'interactive': 'start', 'project': project_name, 'languages': languages, 'base_dir': base_dir,
            'forms': forms, 'notes': notes, 'debug_notes': debug_notes, 'isolates': isolates, 'no_parses': no_parses}
    return template('index', data=data)


@app.route('/interactive/<project_name:re:.*>')
def interactive_project(project_name):
    languages, upstream_target, base_dir = utils.upstream('languages', [], project_name, True)
    languages = [(l, '') for l in languages]
    data = {'interactive': 'start', 'project': project_name, 'languages': languages, 'base_dir': base_dir}
    return template('index', data=data)

@app.route('/experiment/<project_name:re:.*>/<experiment_name:re:.*>')
def experiment(project_name, experiment_name):
    experiments, exp_proj_path, data_elements = utils.list_experiments(project_name)
    error_messages = []
    experiment_info = utils.get_experiment_info(exp_proj_path, experiment_name, data_elements, project_name)
    files, experiment_path = utils.data_files(os.path.join(utils.EXPERIMENTS, project_name), experiment_name)
    data = {'experiment': experiment_name, 'project': project_name, 'base_dir': experiment_path,
            'data_elements': data_elements, 'experiment_info': experiment_info, 'files': files}
    data['tree'] = 'experiment'
    if len(error_messages) > 0:
        data['errors'] = error_messages
    return template('index', data=data)


@app.post('/experiments/<project_name:re:.*>/<experiment_name:re:.*>')
def do_experiment(project_name, experiment_name):
    experiments, base_dir, data_elements = utils.list_experiments(project_name)
    project_dir = os.path.join('..', 'projects', project_name)
    error_messages = []
    if experiment_name == 'NEW':
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
            raise
            error_messages.append(f"couldn't make experiment {new_experiment}")
        experiments, base_dir, data_elements = utils.list_experiments(project_name)
        data = {'experiments': experiments, 'project': project_name, 'experiments': experiments, 'base_dir': base_dir,
                'data_elements': data_elements}
    else:
        pass
    return template('index', data=data)


@app.route('/experiments/<project_name:re:.*>')
def list_experiments(project_name):
    experiments, base_dir, data_elements = utils.list_experiments(project_name)
    data = {'experiments': experiments, 'project': project_name, 'base_dir': base_dir,
            'data_elements': data_elements}
    return template('index', data=data)


@app.post('/remake')
def remake():
    data = {'make': run_make.make('ALL')}
    response = HTTPResponse()
    response.body = data['make']
    return response


@app.route('/make')
def make():
    data = {'make': run_make.make('ALL')}
    return template('index', data=data)


@app.route('/make/<project_name:re:.*>')
def make(project_name):
    data = {'make': run_make.make(project_name)}
    return template('index', data=data)


run(app, host='localhost', port=8080)
# application = default_app()
