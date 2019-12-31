<div id="experiment_files" class="card">
    <h6 class="card-header">Files in this experiment</h6>
    <div class="card-body">
        <form method="post" action="/compare/{{data['project']}}/{{data['experiment']}}">
            <div class="table-responsive">
            <table class="table-sm table-sm retable">
                <tbody>
                % for (file_type, files) in data['files']:
                  % if len(files) > 0:
                    <tr>
                      <td colspan="2">
                        <h6 class="subheadr">{{file_type}}</h6>
                          % if 'sets' == file_type:
                            to compare sets: check 2 &amp; click <button class="btn btn-xs btn-primary" name="compare">compare</button>
                          % end
                      </td>
                    </tr>
                  % end

                  % short_files = {}
                  % for file in files:
                  %     short_file = file.replace(data['project'] + '.','').replace('.' + file_type + '.xml','')
                  %     short_parts = short_file.split('.')
                  %     if len(short_parts) == 2:
                  %         short_file = f'{short_parts[1]} of {short_parts[0]}'
                  %     end
                  %     short_files[short_file] = file
                  % end

                  % for short_file in sorted(short_files):
                        % file = short_files[short_file]
                        <tr>
                            % if 'sets' == file_type:
                               <td>
                                 <div style="width: 60px;">
                                     <a href="/download_file/experiment/{{data['project']}}/{{data['experiment']}}/{{file}}"><span class="fas fa-download""></span></a>
                                     <a href="/get_file/experiments/{{data['project']}}/{{data['experiment']}}/{{file}}?paragraph"><span class="fas fa-file-alt"></span></a>
                                      <input type="checkbox" value="{{file}}" name="{{file}}">
                                      <!-- label for="{{file}}">{{file}}</label -->
                                 <div>
                               </td>
                            % else:
                               <td><a href="/download_file/experiment/{{data['project']}}/{{data['experiment']}}/{{file}}"><span class="fas fa-download"></span></a></td>
                            % end
                            <td><a href="/get_file/experiments/{{data['project']}}/{{data['experiment']}}/{{file}}?tabular">{{short_file}}</a></td>
                        </tr>
                      % end

                % end
                </tbody>
            </table>
            </div>
        </form>
    </div>
</div>
