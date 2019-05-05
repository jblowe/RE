from bottle import Bottle, default_app, run, route, template, debug, static_file, Jinja2Template, BaseTemplate

import os
import sys
import utils

# we need some code from the sibling directory where the rest of the RE code lives
sys.path.append("../src")

import projects

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


@app.route('/')
def index():
    data = {'home': 'here'}
    return template('index', data=data)


@app.route('/about')
def index():
    data = {'about': 'here'}
    return template('index', data=data)


@app.route('/list_projects')
def list_projects():
    project_names = [p for p in projects.projects]
    data = {'projects': project_names}
    return template('index', data=data)


@app.route('/project/<project_name:re:.*>')
def project(project_name):
    files, base_dir = utils.data_files(project_name)
    data = {'project': project_name, 'files': files, 'base_dir': base_dir}
    return template('index', data=data)


@app.route('/project_files/<filename:re:.*>')
def project_files(filename):
    content, project_name = utils.file_content(filename)
    files, base_dir = utils.data_files(project_name)
    data = {'project': project_name, 'files': files, 'base_dir': base_dir, 'filename': filename, 'content': content}
    return template('index', data=data)


@app.route('/make')
def make():
    data = {'make': utils.make(dirname)}
    return template('index', data=data)

run(app, host='localhost', port=8080)
# application = default_app()
