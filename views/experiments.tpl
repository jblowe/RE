<div id="content" class="col-sm-12">
<h3>{{data['project']}} Experiments</h3>
    <input type="hidden" name="project" value="{{data['project']}}">
    <form method="post" action="/experiments/{{data['project']}}/NEW">
        <div class="row">
          <div class="col-md-12 panel border rounded">
          <table class="table table-striped sortable">
          <thead>
          <tr>
            <th>Name</th>
            <th>Updated at</th>
            <th></th>
            <th></th>
            <th>Check to compare</th>
            <th>Click to delete</th>
          </tr>
          </thead>
          <tbody>
          % for experiment in data['experiments']:
            <tr>
            <td>{{ experiment[0] }}</td>
            <td>{{experiment[1]}}</td>
            <td><a href="/experiment/{{data['project']}}/{{experiment[0]}}">view and run</a></td>
            <td><a href="/interactive/{{data['project']}}/{{experiment[0]}}">interactive</a></td>
            <td><input type="checkbox" value="{{experiment[0]}}"></td>
            <td><a class="btn" href="/delete/{{experiment[0]}}">delete</a></td>
            </tr>
          % end
          </tbody>
          </table>
          <button class="btn btn-primary" type="submit">Create new experiment</button>
          <input type="text" name="new_experiment">
          or
          <a class="btn btn-primary" href="/compare">compare</a>
          </div>
    </form>
</div>