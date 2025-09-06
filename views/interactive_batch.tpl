<div id="content" class="col-sm-12">
<h5>{{data['project']}}/{{data['experiment']}}: Interactive Batch</h5>
    <form method="post">
        <div class="row">
          <div class="col-md">
              % include('lexicons.tpl')
          </div>
          <div class="col-md">
              % include('cognate_sets.tpl')
          </div>
        </div>
        <div class="row">
          <div class="col-md">
            % include('settings.tpl')
          </div>
          <div class="col-md">
            % include('statistics.tpl')
          </div>
        </div>
    </form>
</div>