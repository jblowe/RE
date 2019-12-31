<div id="content" class="col-sm-12">
    <div class="treeview w-20 border">
      <h6 class="pt-3 pl-3">Projects and Experiments</h6>
      <hr>
      <ul class="mb-1 pl-3 pb-2">
      % for (project, updated_at, experiments) in data['projects']:
            <li>
            <i class="fas fa-angle-right rotate"></i>
            <a href="/project/{{project}}">{{project}}</a>
            {{updated_at}}
            <ul class="nested">
                % for experiment in experiments[0]:
                    <li>
                    <a href="/experiment/{{project}}/{{ experiment['name'] }}">
                    <span class="fas fa-folder-open"></span> {{ experiment['name'] }}</a>
                    <!-- {{ experiment['date'] }} -->
                    </li>
                % end
                <li>
                    <form method="post" action="/new/{{project}}">
                    <button class="btn-sm" type="submit"><span class="fas fa-folder-plus"></span></button>
                    <input type="text" name="new_experiment">
                    </form>
                </li>
            </ul>
            </li>
      % end
      </ul>
    </div>
</div>
