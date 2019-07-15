<div id="content" class="col-sm-12">
<h3>{{data['project']}} Interactive</h3>
    <form method="post">
        <div class="row">
          <div class="col-md-4 panel border rounded">
          <table>
          % for (language, value) in data['languages']:
                <tr><td><i>{{language}}</i><td><input name="{{language}}" type="text" value="{{value}}"></td></tr>
          % end
          </table>
          <button type="submit">Upstream</button>
          <button type="reset">Reset</button>
          </div>
          <div class="col-md-8 panel border rounded">
          % if 'forms' in data:
          <h4>Sets</h4>
              % for form in data['forms']:
                  <li>{{form}}
                  <ul>
                  % for support in form.supporting_forms:
                  <li>{{support}}</li>
                  % end
                  </li>
                  </ul>
              % end
          % end
          </div>
        </div>
        <div class="row">
          <div class="col-md-4 panel border rounded">
          % if 'no_parses' in data:
          <h4>No parses</h4>
              % for no_parse in data['no_parses']:
                  <li>{{no_parse}}</li>
              % end
          % end
          % if 'isolates' in data:
          <h4>Reconstructions not in sets</h4>
          <h6>(includes "Isolates")</h6>
              % for isolate in data['isolates']:
                  <li>{{isolate[0]}} - {{isolate[1]}}</li>
              % end
          % end
          </div>
          <div class="col-md-8 panel border rounded">
          % if 'debug_notes' in data:
          <h4>Trace</h4>
              % for note in data['debug_notes']:
                   % if note[0] == ' ':
                      {{note}}<br/>
                   % else:
                      <li>{{note}}</li>
                   % end
              % end
          % end
          % if 'notes' in data:
          <h4>Notes</h4>
              % for note in data['notes']:
                  <li>{{note}}</li>
              % end
          % end
          </div>
        </div>
    </form>
</div>