<div id="cognate_sets" class="card">
    <h6 class="card-header">Cognate Sets</h6>
    <div class="card-body">
        <div class="table-responsive">
            <table class="table-sm table-striped">
                <thead/>
                <tbody>
                % if 'forms' in data:
                  % for form in data['forms']:
                      <tr><td></td><b>{{form}}</b></td>
                      % for support in form.supporting_forms:
                        <td>{{support}}</td>
                      % end
                      </tr>
                  % end
                % end
                </tbody>
            </table>
        </div>
    </div>
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
</div>
