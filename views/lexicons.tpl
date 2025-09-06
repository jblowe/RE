<div class="panel card mb-3 pane" id="pane-lexicons">
    <h6 class="card-header">Lexicons</h6>
    <div class="card-body">
        <div class="table-responsive">
            <table class="table-sm table-striped">
                <thead/>
                <tbody>
                <tr>
                    % for language in data['lexicons']:
                    <th>
                        <i>{{language}}</i>
                    </th>
                    % end
                </tr>
                </tbody>
            </table>
        </div>
    </div>
</div>