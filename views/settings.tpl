<div class="panel card mb-3 pane" id="pane-parameters">
    <h6 class="card-header">Parameters</h6>
    <div class="card-body">
        <div class="table-responsive">
            <table class="table-sm table-striped">
                <thead/>
                <tbody>
                <tr>
                    <td><i>Run name (required)</i></td>
                    <td><input name="run" type="text"></td>
                </tr>
                <tr>
                    <td><i>Remarks (optional)</i></td>
                    <td><input name="remarks" type="text"></td>
                </tr>
                % if 'reconstructions' in data['settings'].other:
                <tr>
                    <td><i>Correspondences</i></td>
                    <td>
                        <select name="recon">
                            <option value="">Select...</option>
                            % for c in data['settings'].other['reconstructions']:
                                <option value="{{c}}"
                                % if c == data['recon']:
                                    selected
                                % end
                                >{{c}}</option>
                            % end
                        </select>
                    </td>
                </tr>
                % end
                % if 'fuzzies' in data['settings'].other:
                <tr>
                    <td><i>Fuzzy files</i></td>
                    <td>
                        <select name="fuzzy">
                            <option value="">No fuzzying</option>
                            % for f in data['settings'].other['fuzzies']:
                                <option value="{{f}}"
                                % if f == data['fuzzy']:
                                    selected
                                % end
                                >{{f}}</option>
                            % end
                        </select>
                    </td>
                </tr>
                % end
                % if 'mels' in data['settings'].other:
                <tr>
                    <td><i>MELs</i></td>
                    <td>
                        <select name="mel">
                            <option value="">No MELs</option>
                            % for m in data['settings'].other['mels']:
                                <option value="{{m}}"
                                % if m == data['mel']:
                                    selected
                                % end
                                >{{m}}</option>
                            % end
                        </select>
                    </td>
                </tr>
                % end
                <tr>
                    <td><i>Strict</i></td>
                    <td>
                        <select name="strict">
                            <option value="no">no</option>
                            <option value="yes">yes</option>
                        </select>
                    </td>
                </tr>
                </tbody>
            </table>
        </div>
        <button class="btn-sm btn-primary" name="make">Upstream</button>
        <input class="btn-sm btn-primary" type="reset" value="Reset">
        </p>
    </div>
</div>