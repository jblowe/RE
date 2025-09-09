<div class="panel card mb-3 pane" id="pane-statistics">
    <h6 class="card-header">Statistics</h6>
    <div class="card-body">
        <div class="table-responsive">
            <table class="table-sm table-striped">
                <thead/>
                <tbody>
                % if 'debug_notes' in data:
                    % for note in data['debug_notes']:
                        % if note[0] == '!':
                            <tr><td>{{note[1:]}}</td></tr>
                        % else:
                            <tr><td>{{note}}</td></tr>
                        % end
                    % end
                % end
                % if 'notes' in data:
                <tr><td><h6>Summary</h6></td></tr>
                    % for note in data['notes']:
                    <tr><td>{{note}}</tr></td>
                    % end
                % end
                </tbody>
            </table>
        </div>
    </div>
</div>
