<div id="content" class="col-sm-12">
<h3>Experiment: {{data['project']}}</h3>
    <form method="post">
        <div class="row">
          <div class="col-md-4 panel border rounded">
          <table>
          % for d in data['data_elements']:
                <tr><td><i>{{d}}</i><td><input name="{{d}}" type="text" value="{{d}}"></td></tr>
          % end
          </table>
          <button type="submit" name="run">Save and Run</button>
          </div>
        </div>
        <div class="row">
          <div class="col-md-4 panel border rounded">
              % include('project.tpl')
          </div>
        </div>
    </form>
</div>