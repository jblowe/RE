<div class="row">
<div class="col-md-4 panel border rounded">
    <h3>Experiment: {{data['project']}}/{{data['experiment']}}</h3>
% if data['num_files'] > 0:
    <form method="post" action="/make/{{data['project']}}/{{data['experiment']}}">
          <h4>Parameters</h4>
          <table class="table table-striped">
          <thead>
          <tr>
            <th/>
            <th/>
          </tr>
          </thead>
          <tbody>
            <tr><td><i>Run name</i></td><td><input name="name" type="text" value="default"></td></tr>
            % if 'title' in data['experiment_info']:
              <tr><td><i>Title</i></td><td>{{data['experiment_info']['title']}}</td></tr>
            % end
            % if 'mels' in data['experiment_info']:
                <tr><td><i>MEL</i></td><td>
                <select name="mel">
                    <option value="none">none</option>
                % for m in data['experiment_info']['mels']:
                    <option value="{{m}}">{{m}}</option>
                % end
                </select>
                </td></tr>
            % end
            <tr><td><i>Strict</i></td><td>
            <select name="strict">
            <option value="no">no</option>
            <option value="yes">yes</option>
            </select>
            </td></tr>
          </tbody>
          </table>
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