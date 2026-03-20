<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" encoding="UTF-8" omit-xml-declaration="yes"/>
  <xsl:template match="/">
    <html lang="en">
      <head>
        <meta charset="utf-8"/>
        <style>
          .actions-col { width: 1%; white-space: nowrap; }
          .btn-icon { padding: .1rem .4rem; line-height: 1; }
        </style>
      </head>
      <body>
        <div class="card mb-3">
          <div class="card-header fw-semibold">Fuzzy Mappings</div>
          <div class="card-body p-0">
            <div class="table-responsive">
              <table class="table table-sm table-bordered table-hover mb-0" id="fuz-table">
                <thead class="table-light">
                  <tr>
                    <th class="actions-col">
                      <button type="button" id="addFuzBtn"
                              class="btn btn-outline-primary btn-sm btn-icon"
                              title="Add row">+</button>
                    </th>
                    <th>Dialect</th>
                    <th>From (comma-separated)</th>
                    <th>To</th>
                  </tr>
                </thead>
                <tbody id="fuz-body">
                  <xsl:for-each select="fuzzy/item">
                    <xsl:variable name="n" select="position()"/>
                    <tr>
                      <td class="actions-col">
                        <button type="button"
                                class="btn btn-outline-danger btn-sm btn-icon btn-del-fuz-row"
                                title="Delete row">&#x2212;</button>
                      </td>
                      <td>
                        <input type="text" class="form-control form-control-sm"
                               name="item-{$n}-dial" id="item-{$n}-dial">
                          <xsl:attribute name="value">
                            <xsl:value-of select="@dial"/>
                          </xsl:attribute>
                        </input>
                      </td>
                      <td>
                        <input type="text" class="form-control form-control-sm"
                               name="item-{$n}-from" id="item-{$n}-from">
                          <xsl:attribute name="value">
                            <xsl:for-each select="from">
                              <xsl:value-of select="."/>
                              <xsl:if test="position()!=last()">, </xsl:if>
                            </xsl:for-each>
                          </xsl:attribute>
                        </input>
                      </td>
                      <td>
                        <input type="text" class="form-control form-control-sm"
                               name="item-{$n}-to" id="item-{$n}-to">
                          <xsl:attribute name="value">
                            <xsl:value-of select="@to"/>
                          </xsl:attribute>
                        </input>
                      </td>
                    </tr>
                  </xsl:for-each>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <script><![CDATA[
(function(){
  function reindex(){
    var rows = document.querySelectorAll('#fuz-body tr');
    rows.forEach(function(tr, i){
      var n = i + 1;
      ['dial','from','to'].forEach(function(key){
        var inp = tr.querySelector('input[name$="-' + key + '"]');
        if(inp){ inp.name = 'item-' + n + '-' + key; inp.id = 'item-' + n + '-' + key; }
      });
    });
  }
  document.addEventListener('click', function(ev){
    if(ev.target && ev.target.id === 'addFuzBtn'){
      var tr = document.createElement('tr');
      tr.innerHTML =
        '<td class="actions-col"><button type="button" class="btn btn-outline-danger btn-sm btn-icon btn-del-fuz-row" title="Delete row">&#x2212;</button></td>'
        + '<td><input type="text" class="form-control form-control-sm" placeholder="dialect"></td>'
        + '<td><input type="text" class="form-control form-control-sm" placeholder="from1, from2"></td>'
        + '<td><input type="text" class="form-control form-control-sm" placeholder="to"></td>';
      document.getElementById('fuz-body').appendChild(tr);
      reindex();
      return;
    }
    var del = ev.target.closest('.btn-del-fuz-row');
    if(del){ del.closest('tr').remove(); reindex(); }
  });
})();
        ]]></script>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
