<div class="row">
    <div id="leftpane" class="col-md-4">
        <h5>Experiment: {{data['project']}}/{{data['experiment']}}</h5>
        % if 'title' in data['experiment_info']:
            <p>Source data description: {{data['experiment_info']['title']}}</p>
        % end
        <button class="btn-sm btn-primary" id="toggle_parameters" >setup and perform upstream run</button>
        <div id="upstream" class="panel panel-default" style="display:none;">
            <form method="post" action="/make/{{data['project']}}/{{data['experiment']}}">
                  % include('parameters.tpl')
                  <p/><p>
                  <button class="btn-sm btn-primary" name="make">Upstream</button>
                  <a href= "" class="btn-sm btn-primary" name="refresh">Refresh</a>
                  </p>
            </form>
        </div>
        % if data['num_files'] > 0:
            % include('render_experiment.tpl')
        % else:
            <hr/>
        % end
    </div>
    % if 'content' in data:
        <div id="content" class="col-sm-8">
            <h4>{{data['filename']}}</h4>
            <i>last updated: {{data['date']}}</i>
            {{!data['content']}}
        </div>
    % end
</div>