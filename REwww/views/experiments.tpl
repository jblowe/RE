<div id="content" class="col-sm-12">
<h5>{{data['project']}} Experiments</h5>
  <form method="post" action="/experiments/{{data['project']}}/NEW">
    <input type="hidden" name="project" value="{{data['project']}}">
        <div class="row">
          <div class="col-md-12">
          <div class="table-responsive">
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
            <td>{{ experiment['name'] }}</td>
            <td>{{experiment['date']}}</td>
            <td><a href="/experiment/{{data['project']}}/{{experiment['name']}}">view and/or run</a></td>
            <td><a href="/interactive/{{data['project']}}/{{experiment['name']}}">interactive</a></td>
            <td><input type="checkbox" value="{{experiment['name']}}"></td>
            <td><a class="btn" href="/delete/{{data['project']}}/{{experiment['name']}}"><span class="fas fa-trash"></span> delete</a></td>
            </tr>
          % end
          </tbody>
          </table>
          </div>
          <button class="btn-sm btn-primary" type="submit">Create new experiment</button>
          <input type="text" name="new_experiment">
          or
          <a class="btn-sm btn-primary" href="/compare">Compare selected experiments</a>
          </div>
  </form>
</div>