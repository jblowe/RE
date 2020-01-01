<div id="content" class="col-sm-12">
<h4>{{data['project']}}/{{data['experiment']}} Interactive</h4>
    <form method="post">
        <div class="row">
          <div class="col-md-4">
          % include('parameters.tpl')
          <hr/>
          <table>
          % for (language, value) in data['languages']:
                <tr><td><i>{{language}}</i><td><input name="{{language}}" type="text" value="{{value}}"></td></tr>
          % end
          </table>
          <button type="submit">Upstream</button>
          <button type="reset">Reset</button>

          % if 'no_parses' in data:
          <hr/>
          <h5>No parses</h5>
              % for no_parse in data['no_parses']:
                  <li>{{no_parse}}</li>
              % end
          % end
          % if 'isolates' in data:
          <hr/>
          <h5>Reconstructions not in sets</h5>
          <h6>(includes "Isolates")</h6>
              % for isolate in data['isolates']:
                  <li>{{isolate[0]}} - {{isolate[1]}}</li>
              % end
          % end
          </div>
          <div class="col-md-4 card border rounded">
          % if 'forms' in data:
          <h5>Sets</h5>
              % for form in data['forms']:
                  <li><b>{{form}}</b>
                  <ul>
                  % for support in form.supporting_forms:
                  <li>{{support}}</li>
                  % end
                  </li>
                  </ul>
              % end
          % end
          % if 'debug_notes' in data:
          <hr/>
          <h5>Trace</h5>
              % for note in data['debug_notes']:
                   % if note[0] == '!':
                      <br/><b>{{note[1:]}}</b><br/>
                   % else:
                      {{note}}<br/>
                   % end
              % end
          % end
          </div>
          <div class="col-md-4 card border rounded">
          % if 'notes' in data:
          <h5>Summary</h5>
              % for note in data['notes']:
                  <li>{{note}}</li>
              % end
          % end
          </div>
        </div>
    </form>
</div>