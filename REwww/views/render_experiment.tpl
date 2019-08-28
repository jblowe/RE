<h4>Results</h4>
<table class="table">
% for (file_type, files) in data['files']:
  % if len(files) > 0:
    <tr><td colspan="4"><h5>{{file_type}}</h5></td></tr>
      % for file in files:
        <tr>
            % if 'sets' == file_type:
               <td width="15%"><a href="/download_file/experiment/{{data['project']}}/{{data['experiment']}}/{{file}}"><span class="glyphicon glyphicon glyphicon-download-alt"></span></a>
               &nbsp;<a href="/get_file/{{data['tree']}}/{{data['project']}}/{{data['experiment']}}/{{file}}?paragraph"><span class="glyphicon glyphicon glyphicon-arrow-right"></span></a></td>
            % else:
               <td><a href="/download_file/experiment/{{data['project']}}/{{data['experiment']}}/{{file}}"><span class="glyphicon glyphicon glyphicon-download-alt"></span></a></td>
            % end
            <td><a href="/get_file/experiments/{{data['project']}}/{{data['experiment']}}/{{file}}?tabular">{{file}}</a></td>
        </tr>
      % end
  % end
% end
</table>
