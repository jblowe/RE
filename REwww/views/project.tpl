<div class="row">
    <div id="leftpane" class="col-md-3">
        % include('render_project.tpl')
    </div>
    % if 'content' in data:
        <div id="content" class="col-sm-9">
            <h5>{{data['filename']}}</h5>
            <!-- i>last updated: {{data['date']}}</i -->
            {{!data['content']}}
        </div>
    % end
</div>