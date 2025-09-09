<div id="content" class="col-sm-12">
    <h6 class="pt-3 pl-3">Projects and Their Experiments</h6>
    <div class="w-20 border">
      <ul class="mb-3 pl-3 pb-2">
      % for (project, updated_at, experiments) in data['projects']:
            <li class="w-10">
            <a title="view project source" class="closed">
            <i class="fas fa-angle-right rotate"></i>
            <span>{{project}}</span></a>
            <!-- {{updated_at}} -->
            <ul>
                <li><a title="view project source" href="/project/{{project}}">
                <span class="fas fa-archive"></span> source data</a></li>
                % for experiment in experiments[0]:
                    <li>
                    <a title="interactive" href="/interactive/{{project}}/{{ experiment['name'] }}">
                    <span class="fas fa-eye"></span></a>
                    <a title="open experiment" href="/experiment/{{project}}/{{ experiment['name'] }}">
                    <span class="fas fa-folder-open"></span>
                     {{ experiment['name'] }}</a>
                    <!-- {{ experiment['date'] }} -->
                    </li>
                % end
                <li>
                    <form method="post" action="/new/{{project}}">
                    <button title="create new experiment" class="btn-sm" type="submit"><span class="fas fa-folder-plus"></span></button>
                    <input type="text" name="new_experiment">
                    </form>
                </li>
            </ul>
            </li>
      % end
      </ul>
    </div>
</div>
