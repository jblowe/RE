<h5>Upstream parameters available</h5>
<table class="table table-striped">
<thead>
<tr>
<th/>
<th/>
</tr>
</thead>
<tbody>
% if not 'interactive' in data:
    <tr><td><i>Run name (required)</i></td><td><input name="run" type="text"></td></tr>
    <tr><td><i>Remarks (optional)</i></td><td><input name="remarks" type="text"></td></tr>
% end
% if 'reconstructions' in data['experiment_info']:
    <tr><td><i>Reconstructions (required)</i></td><td>
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
