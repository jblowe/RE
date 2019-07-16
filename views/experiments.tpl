<div id="content" class="col-sm-12">
<h3>{{data['project']}} Experiments</h3>
    <form method="post" action="/experiments/{{data['project']}}/NEW">
        <div class="row">
          <div class="col-md-12 panel border rounded">
          <table class="table table-striped sortable">
          <thead>
          <tr>
          % for d in data['data_elements']:
            <th>{{d}}</th>
          % end
          </tr>
          </thead>
          <tbody>
          % for experiment in data['experiments']:
                <tr>
                <td><a href="/experiment/{{data['project']}}/{{experiment[0]}}">{{ experiment[0] }}</a></td>
                % for e in experiment[1:]:
                <td>{{e}}</td>
                % end
                </tr>
          % end
          </tbody>
          </table>
          <button type="submit">New</button>
          <input type="text" name="new_experiment">
          </div>
    </form>
</div>