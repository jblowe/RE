<div class="row">
    <div id="leftpane" class="col-md-3">
        <h5>
            <a class="btn-sm" href="/project/{{data['project']}}"><span class="fas fa-arrow-up"></span></a>
            Experiment: {{data['project']}}/{{data['experiment']}}&nbsp;
            <a class="btn-sm" href="/delete-experiment/{{data['project']}}/{{data['experiment']}}"><span class="fas fa-trash-alt"></span></a>
        </h5>
        % if 'title' in data['experiment_info']:
            <p><i>{{data['experiment_info']['title']}}</i></p>
        % end
        <h6>
            <small>perform 'upstream' computations:</small>
            <a href="#" id="toggle_parameters"><span class="far fa-caret-square-right" /></a>
        </h6>
        <form method="post" action="/make/{{data['project']}}/{{data['experiment']}}">
            <div id="upstream" style="display:none;">
                % include('parameters.tpl')
            </div>
        </form>
        % if data['num_files'] > 0:
            % include('render_experiment.tpl')
        % else:
            <hr/>
        % end
    </div>
    % if 'content' in data:
        <div id="content" class="col-sm-9">
            <div class="row">
            <div class="col-sm-10">
                <h5>{{data['filename']}}</h5>
            </div>
            <div class="col-sm-2">
            % if 'next' in data:
              <a href="{{ data['next'] }}" class="btn btn-success me-3">Edit</a>
            %end
            </div>
            </div>
            <!-- i>last updated: {{data['date']}}</i -->
            {{!data['content']}}
        </div>
    % end
</div>