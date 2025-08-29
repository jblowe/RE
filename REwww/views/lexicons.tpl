<div id="lexicons" class="card">
    <h6 class="card-header">Lexicons</h6>
    <div class="card-body">
        <div class="table-responsive">
            <table class="table-sm table-striped">
                <thead/>
                <tbody>
                <tr>
                    % for (language, value) in data['languages']:
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