<div id="content" class="col-sm-12">
<h3>{{data['project']}}:  {{data['experiment']}} Experimment</h3>
    <form method="post">
        <div class="row">
          <div class="col-md-4 panel border rounded">
          <table>
          % for d in data['data_elements']:
                <tr><td><i>{{d}}</i><td><input name="{{d}}" type="text" value="{{d}}"></td></tr>
          % end
          </table>
          <button type="submit">Run</button>
          </div>
          <div class="col-md-8 panel border rounded">
          </div>
        </div>
    </form>
</div>