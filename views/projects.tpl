<table class="table table-striped">
    <thead>
    <tr>
        <th>Corpus</th>
        <th></th>
        <th></th>
        <th>Last updated</th>
        <th></th>
    </tr>
    </thead>
    <tbody>
  % for (project, updated_at) in data['projects']:
    <tr>
        <td>{{project}}</td>
        <td><a href="/project/{{project}}">source data</a></td>
        <td><a href="/experiments/{{project}}">experiments</a></td>
        <td>{{updated_at}}</td>
    </tr>
  % end
    </tbody>
</table>
