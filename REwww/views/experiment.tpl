<div class="row">
<div class="col-md-4 panel border rounded">
    <h3>Experiment: {{data['project']}}/{{data['experiment']}}</h3>
% if 'title' in data['experiment_info']:
    <p>Source data description: {{data['experiment_info']['title']}}</p>
% end
% if data['num_files'] > 0:
    <form method="post" action="/make/{{data['project']}}/{{data['experiment']}}">
          % include('parameters.tpl')
          <p/><p>
          <button class="btn btn-primary" name="make">Upstream</button>
          <a href= "" class="btn btn-primary" name="refresh">Refresh</a>
          % include('render_experiment.tpl')
          </p>
          </div>
    </form>
    % if 'content' in data:
        <div id="content" class="col-sm-8">
            <h3>{{data['filename']}}</h3>
            <i>last updated: {{data['date']}}</i>
            {{!data['content']}}
        </div>
    % end
</div>
% else:
    <hr/>
% end
</div>