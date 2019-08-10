<h4>Parameters available</h4>
<table class="table table-striped">
<thead>
<tr>
<th/>
<th/>
</tr>
</thead>
<tbody>
<tr><td><i>Run name (required)</i></td><td><input name="run_name" type="text"></td></tr>
<tr><td><i>Remarks (optional)</i></td><td><input name="remarks" type="text"></td></tr>
% if 'reconstructions' in data['experiment_info']:
    <tr><td><i>Reconstructions (required)</i></td><td>
    <select name="toc">
    % for c in data['experiment_info']['reconstructions']:
        <option value="{{c}}">{{c}}</option>
    % end
    </select>
    </td></tr>
% end
% if 'fuzzies' in data['experiment_info']:
    <tr><td><i>Fuzzy files</i></td><td>
    <select name="fuzzy">
        <option value="none">none</option>
    % for f in data['experiment_info']['fuzzies']:
        <option value="{{f}}">{{f}}</option>
    % end
    </select>
    </td></tr>
% end
% if 'mels' in data['experiment_info']:
    <tr><td><i>MELs</i></td><td>
    <select name="mel">
        <option value="none">none</option>
    % for m in data['experiment_info']['mels']:
        <option value="{{m}}">{{m}}</option>
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
</tbody>
</table>
