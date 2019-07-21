<div id="content" class="col-sm-12">
    <div id="project" class="col-sm-4">
        % include('render_project.tpl')
    </div>
    % if 'content' in data:
        <div id="content" class="col-sm-8">
            <h3>{{data['filename']}}</h3>
            <i>last updated: {{data['date']}}</i>
            {{!data['content']}}
        </div>
    % end
</div>