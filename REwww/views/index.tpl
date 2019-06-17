<!DOCTYPE html>
<html lang="en">
% include('head.tpl')
<body>
    % include ('nav.tpl')
	<div class="container">
		<div class="row">
			<div class="container-fluid">
            % if 'project' in data:
              % if 'interactive' in data:
                % include('interactive.tpl')
              % else:
              <div id="project" class="col-sm-4">
                <a href="/list_projects">&lt;&lt; back</a>
                <h3>{{data['project']}}</h3>
                  % for (file_type, files) in data['files']:
                      % if len(files) > 0:
                        <h5>{{file_type}}</h5>
                        <ul>
                          % for file in files:
                            <li>
                                <a href="/project_file/{{data['project']}}/{{file}}">{{file}}</a>
                                <a href="/download/{{data['project']}}/{{file}}"><span class="glyphicon glyphicon glyphicon-download-alt"></span></a>
                            </li>
                          % end
                        </ul>
                      % end
                  % end
              </div>
              %end
              % if 'content' in data:
                <div id="content" class="col-sm-8">
                <!-- a href="/project/{{data['project']}}">&lt;&lt; back</a -->
                <h3>{{data['filename']}}</h3>
                <i>last updated: {{data['date']}}</i>
                {{!data['content']}}
                </div>
              % end
            % elif 'projects' in data:
            <table class="table table-striped">
                <thead>
                <tr>
                    <th>Project</th>
                    <th>Last updated</th>
                    <th></th>
                    <th></th>
                </tr>
                </thead>
                <tbody>
              % for (project, updated_at, project_dir) in data['projects']:
                <tr>
                    <td><a href="/project/{{project}}">{{project}}</a></td>
                    <td>{{updated_at}}</td>
                    <td><a href="/interactive/{{project}}">interactive</a></td>
                    <td><a href="/make/{{project}}">refresh</a></td>
                </tr>
              % end
                </tbody>
            </table>
            % elif 'make' in data:
            <ul>
			<h2>'Make' results</h2>
				<p>
				{{data['make']}}
				</p>
            </ul>
            % elif 'home' in data:
			<h2>The Reconstruction Engine</h2>
				<p>
				A computer implementation of the comparative method.
				</p>
            % elif 'about' in data:
                % include('about.tpl')
            % end
		</div>
		<!--./row-->
		<div class="row">
			<hr>
			<footer>
				<p><i>Lowe, François, Mazaudon, and Zhang 2019.</i>  {{ footer_info }}</p>
			</footer>			
		</div>
	</div>
	<!-- /container -->
</body>
</html>