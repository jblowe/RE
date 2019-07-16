<!DOCTYPE html>
<html lang="en">
% include('head.tpl')
<body>
% include ('nav.tpl')
<div class="container">
    <div class="row">
        <div class="container-fluid">
            % if 'make' in data:
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
            % else:
                <a href="/list_tree/projects">&lt;&lt; back</a>
                % include('errors.tpl')
                % if 'interactive' in data:
                    % include('interactive.tpl')
                % elif 'experiments' in data:
                    % include('experiments.tpl')
                % elif 'experiment' in data:
                    % include('experiment.tpl')
                % elif 'projects' in data:
                    % include('projects.tpl')
                % elif 'project' in data:
                    <div id="project" class="col-sm-4">
                        % include('project.tpl')
                    </div>
                    % if 'content' in data:
                        <div id="content" class="col-sm-8">
                            <h3>{{data['filename']}}</h3>
                            <i>last updated: {{data['date']}}</i>
                            {{!data['content']}}
                        </div>
                    % end
                % end
            % end
        </div>
    </div>
    <!--./row-->
    <div class="row">
        <div id="footer" class="col-sm-12">
            <hr>
            <footer>
                <p><i>Lowe, François, Mazaudon, and Zhang 2019.</i> {{ footer_info }}</p>
            </footer>
        </div>
    </div>
</div>
</body>
</html>
