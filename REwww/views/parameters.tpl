<div id="parameters" class="card">
    <h6 class="card-header">Upstream parameters available</h6>
    <div class="card-body">
        <form method="get" action="/make/{{data['project']}}/{{data['experiment']}}">
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
                % for c in data['experiment_info']['reconstructions']:
                    <option value="{{c}}"
                    % if c == data['experiment_info']['recon']:
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
                    % if f == data['experiment_info']['fuzzy']:
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
        </form>
    </div>
</div>