<div class="panel card mb-3 pane" id="pane-parameters">
    <h6 class="card-header">Upstream parameters available</h6>
    <div class="card-body">
        <div class="table-responsive">
        <table class="table-sm table-striped">
        <thead/>
        <tbody>
        % if not 'interactive' in data:
            <tr><td><i>Run name (required)</i></td><td><input name="run" type="text"></td></tr>
            <tr><td><i>Remarks (optional)</i></td><td><input name="remarks" type="text"></td></tr>
        % end
        % if 'reconstructions' in data['experiment_info']:
            <tr><td><i>Correspondences</i></td><td>
            <select name="recon">
                <option value="">Select...</option>
            % for c in data['experiment_info']['reconstructions']:
                <option value="{{c}}"
                % if c == form.get('recon'):
                    selected
                % end
                >{{c}}</option>
            % end
            </select>
            </td></tr>
        % end
        % if 'fuzzies' in data['experiment_info']:
            <tr><td><i>Fuzzy files</i></td><td>
            <select name="fuzzy">
                <option value="">No fuzzying</option>
            % for f in data['experiment_info']['fuzzies']:
                <option value="{{f}}"
                % if f == form.get('fuzzy'):
                    selected
                % end
                >{{f}}</option>
            % end
            </select>
            </td></tr>
        % end
        % if not 'interactive' in data:
            % if 'mels' in data['experiment_info']:
                <tr><td><i>MELs</i></td><td>
                <select name="mel">
                    <option value="">No MELs</option>
                % for m in data['experiment_info']['mels']:
                    <option value="{{m}}"
                    % if m == data['experiment_info']['mel']:
                        selected
                    % end
                    >{{m}}</option>
                % end
                </select>
                </td></tr>
            % end
            <tr><td><i>Strict</i></td><td>
            <select name="strict">
            <option value="no">no</option>
            <option value="yes">yes</option>
            </select>
            </td></tr>
        % end
        </tbody>
        </table>
        </div>

      % if not 'interactive' in data:
          <button class="btn-sm btn-primary" name="make">Upstream</button>
          <input class="btn-sm btn-primary" type="reset" value="Reset">
      % end
      </p>
    </div>
</div>