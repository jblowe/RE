from bottle import Bottle, HTTPResponse, default_app, post, request, run, route, template, debug, static_file, Jinja2Template, BaseTemplate

import os
import sys
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


@app.route('/list_projects')
def list_projects():
    project_info = utils.project_info()
    data = {'projects': project_info}
    return template('index', data=data)


@app.route('/project/<project_name:re:.*>')
def project(project_name):
    files, base_dir = utils.data_files(project_name)
    data = {'project': project_name, 'files': files, 'base_dir': base_dir}
    return template('index', data=data)


@app.route('/project_file/<filename:re:.*>')
def project_file(filename):
    content, project_name, date = utils.file_content(filename)
    files, base_dir = utils.data_files(project_name)
    data = {'project': project_name, 'files': files, 'base_dir': base_dir, 'filename': filename, 'date': date, 'content': content}
    return template('index', data=data)


@app.route('/download/<filename:re:.*>')
def download(filename):
    content, project_name = utils.all_file_content(filename)
    files, base_dir = utils.data_files(project_name)
    response = HTTPResponse()
    response.body = content
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    return response


@app.post('/interactive/<project_name:re:.*>')
def upstream(project_name):
    languages = [(i, getattr(request.forms, i)) for i in request.forms]
    postdict = request
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
