<div class="row">
    <div id="leftpane" class="col-md-4">
        <h5>Experiment: {{data['project']}}/{{data['experiment']}}</h5>
        % if 'title' in data['experiment_info']:
            <p>Source data description: {{data['experiment_info']['title']}}</p>
        % end
        <h6>click <a href="#" id="toggle_parameters">here</a> to do computations (compare, upstream)</h6>
        <form method="post" action="/make/{{data['project']}}/{{data['experiment']}}">
        <div id="upstream" style="display:none;">
            % include('parameters.tpl')
        </div>
        % if data['num_files'] > 0:
            % include('render_experiment.tpl')
        % else:
            <hr/>
        % end
        </form>
    </div>
    % if 'content' in data:
        <div id="content" class="col-sm-8">
            <h4>{{data['filename']}}</h4>
            <!-- i>last updated: {{data['date']}}</i -->
            {{!data['content']}}
        </div>
    % end
</div>