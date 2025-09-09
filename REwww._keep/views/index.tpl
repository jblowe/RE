<!DOCTYPE html>
<html lang="en">
% include('head.tpl')
<body>
% include ('nav.tpl')
<main role="main" class="container" style="padding-top: 15px;">
    <div class="row">
        <div class="container-fluid">
            % if 'make' in data:
                % include('make.tpl')
            % elif 'compare' in data:
                % include('compare.tpl')
            % elif 'home' in data:
                <p>A computer implementation of the comparative method.</p>
            % elif 'about' in data:
                % include('about.tpl')
            % else:
                % include('alerts.tpl')
                % if 'interactive' in data:
                    % include('interactive.tpl')
                % elif 'interactive_batch' in data:
                    % include('interactive_batch.tpl')
                % elif 'projects' in data:
                    % include('projects.tpl')
                % elif 'experiment' in data:
                    % include('experiment.tpl')
                % elif 'experiments' in data:
                    % include('experiments.tpl')
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
<script>
    $( "#toggle_sidebar" ).click(function() {
      $( "#leftpane" ).toggle();
      $( "#content" ).toggleClass( "col-sm-8", "col-sm-12" );
    });
    $( "#toggle_parameters" ).click(function() {
      $( "#upstream" ).toggle();
    });
</script>
</main>
</body>
</html>
