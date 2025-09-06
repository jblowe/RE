<div id="content" class="col-sm-12">
    <h6 class="pt-3 pl-3">Projects and Their Experiments</h6>
    <div class="w-20 border">
      <ul class="mb-3 pl-3 pb-2">
      % for (project, updated_at, experiments) in data['projects']:
            <li class="w-10">
            <a title="view project source" href="/project/{{project}}">
            <span class="fas fa-archive"></span>
            <span>{{project}}</span></a>
            <!-- {{updated_at}} -->
            </li>
      % end
      </ul>
    </div>
</div>
