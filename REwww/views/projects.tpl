<table class="table table-striped">
    <thead>
    <tr>
        <th>Project</th>
        <th>Last updated</th>
        <th></th>
        <th></th>
    </tr>
    </thead>
    <tbody>
  % for (project, updated_at) in data['projects']:
    <tr>
        <td><a href="/project/{{project}}">{{project}}</a></td>
        <td>{{updated_at}}</td>
        <td><a href="/experiments/{{project}}">experiments</a></td>
    </tr>
  % end
    </tbody>
</table>
