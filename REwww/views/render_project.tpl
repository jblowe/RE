<h3>{{data['project']}}</h3>
<h4>Source data</h4>
% for (file_type, files) in data['files']:
  % if len(files) > 0:
    <h5>{{file_type}}</h5>
    <ul>
      % for file in files:
        <li>
            <a href="/get_file/{{data['tree']}}/{{data['project']}}/{{file}}">{{file}}</a>
            <a href="/download_file/{{data['tree']}}/{{data['project']}}/{{file}}"><span class="glyphicon glyphicon glyphicon-download-alt"></span></a>
        </li>
      % end
    </ul>
  % end
% end
