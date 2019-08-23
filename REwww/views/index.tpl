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
                        (Re)run completed.
                    </p>
                    <p>
                        {{data['make'][0][0]}}
                    </p>
                    <!-- p>
                        <a href="/get_file/experiments/{{data['project']}}/{{data['experiment']}}/{{data['project']}}.default.upstream.statistics.xml">View results</a>
                    </p>
                    <p>
                        <a class="btn btn-primary" href="/experiment/{{data['project']}}/{{data['experiment']}}">Return to experiment</a>
                    </p -->
                    <p>
                        <a class="btn btn-primary" href="/list_tree/projects">Return to project list</a>
                    </p>
                </ul>
            % elif 'compare' in data:
                <ul>
                    <h2>Compare</h2>
                    <p>
                    </p>
                    <a class="btn btn-primary" href="/experiment/{{data['project']}}/{{data['experiment']}}">Compare</a>
                </ul>
            % elif 'home' in data:
                <h2>The Reconstruction Engine</h2>
                <p>
                    A computer implementation of the comparative method.
                </p>
            % elif 'about' in data:
                % include('about.tpl')
            % else:
                <a href="{{data['back']}}">&lt;&lt; back</a>
                % include('errors.tpl')
                % if 'interactive' in data:
                    % include('interactive.tpl')
                % elif 'experiment' in data:
                    % include('experiment.tpl')
                % elif 'experiments' in data:
                    % include('experiments.tpl')
                % elif 'projects' in data:
                    % include('projects.tpl')
                % elif 'project' in data:
                    % include('project.tpl')
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
