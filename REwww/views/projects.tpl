<div id="content" class="col-sm-12">
    <h6 class="pt-3 pl-3">Projects</h6>
    <div class="w-20 border">
      <ul class="mb-3 pl-3 pb-2">
      % for (project, updated_at) in data['projects']:
            <li class="w-10">
            <a title="view project source" href="/project/{{project}}">
            {{project}}</a>
            </li>
      % end
      </ul>
    </div>
</div>
