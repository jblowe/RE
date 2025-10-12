<div id="experiment_files" class="card">
  <h6 class="card-header">Files in this project</h6>
  <div class="card-body">
    <form method="post" action="/compare/{{data['project']}}">
      <div class="table-responsive">
        <table class="table-sm table-sm retable">
          <tbody>
          % for (file_type, files) in data['files']:
          % if len(files) > 0:
          <tr>
            <td colspan="2">
              <h6 class="subheadr">{{file_type}}</h6>
            </td>
          </tr>
          % end

          % short_files = {}
          % for file in files:
          % short_file = file.replace(data['project'] + '.','').replace('.' + file_type + '.xml','')
          % short_parts = short_file.split('.')
          % if len(short_parts) == 2:
          % short_file = f'{short_parts[0]} {short_parts[1]}'
          % end
          % short_files[short_file] = file
          % end

          % for short_file in short_files:
          % file = short_files[short_file]
          <tr>
            % if 'sets' == file_type:
            <td>
              <div style="width: 60px;">
                <a href="/download_file/projects/{{data['project']}}/{{file}}"><span class="fas fa-download""></span>
                </a>
                <a href="/get_file/projects/{{data['project']}}/{{file}}?paragraph"><span
                        class="fas fa-file-alt"></span></a>
                <input type="checkbox" value="{{file}}" name="{{file}}">
                <!-- label for="{{file}}">{{file}}</label -->
                <div>
            </td>
            % elif 'mel' == file_type:
            <td>
              <div style="width: 60px;">
                <a href="/download_file/projects/{{data['project']}}/{{file}}"><span class="fas fa-download""></span>
                </a>
                <a href="/d3/projects/{{data['project']}}/{{file}}"><span class="fas fa-share-alt"></span></a>
                <div>
            </td>
            % else:
            <td><a href="/download_file/projects/{{data['project']}}/{{file}}"><span class="fas fa-download"></span></a>
            </td>
            % end
            <td><a href="/get_file/projects/{{data['project']}}/{{file}}">{{short_file}}</a></td>
          </tr>
          % end

          % if 'sets' == file_type:
          <tr>
            <td colspan="2">
              <hr/>
              check 2 above to
              <button class="btn btn-xs btn-primary" name="compare">compare</button>
            </td>
          </tr>
          % end
          % end
          </tbody>
        </table>
      </div>
    </form>
  </div>
</div>
