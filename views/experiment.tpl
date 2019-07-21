<div class="row">
<div class="col-md-4 panel border rounded">
    <h3>Experiment: {{data['project']}}/{{data['experiment']}}</h3>
% if data['num_files'] > 0:
    <form method="post">
          <table>
          % for d in data['data_elements']:
                <tr><td><i>{{d}}</i><td><input name="{{d}}" type="text" value="{{d}}"></td></tr>
          % end
          </table>
          <a class="btn btn-primary" href="/make/{{data['project']}}/{{data['experiment']}}">Save and Run</a>
          % include('render_experiment.tpl')
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