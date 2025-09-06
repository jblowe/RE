<div class="panel card mb-3 pane" id="pane-cognate-sets">
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
  <h6>No parses</h6>
      % for no_parse in data['no_parses']:
          <li>{{no_parse}}</li>
      % end
  % end
  % if 'isolates' in data:
  <hr/>
  <h6>Isolates</h6>
      % for isolate in data['isolates']:
          <li>{{isolate[0]}} - {{isolate[1]}}</li>
      % end
  % end
  </div>
</div>
