<div id="experiment_files" class="panel panel-default">
    <div class="panel-heading">Files in this experiment</div>
    <div class="panel-body">
    <table id="retable" class="table table-sm">
    % for (file_type, files) in data['files']:
      % if len(files) > 0:
        <tr><td colspan="4"><h6>{{file_type}}</h6></td></tr>
          % for file in files:
            <tr>
                % if 'sets' == file_type:
                   <td width="15%"><a href="/download_file/experiment/{{data['project']}}/{{data['experiment']}}/{{file}}"><span class="fas fa-download""></span></a>
                   &nbsp;<a href="/get_file/{{data['tree']}}/{{data['project']}}/{{data['experiment']}}/{{file}}?paragraph"><span class="fas fa-file-alt"></span></a></td>
                % else:
                   <td><a href="/download_file/experiment/{{data['project']}}/{{data['experiment']}}/{{file}}"><span class="fas fa-download"></span></a></td>
                % end
                <td><a href="/get_file/experiments/{{data['project']}}/{{data['experiment']}}/{{file}}?tabular">{{file}}</a></td>
            </tr>
          % end
      % end
    % end
    </table>
    </div>
</div>
