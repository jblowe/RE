<h4>{{data['project']}}</h4>
<h5>Source data</h5>
% for (file_type, files) in data['files']:
  % if len(files) > 0:
    <h6>{{file_type}}</h6>
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
