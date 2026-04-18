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
          <div class="card-header fw-semibold">MEL Entries</div>
          <div class="card-body p-0">
            <div class="table-responsive">
              <table class="table table-sm table-bordered table-hover mb-0" id="mel-table">
                <thead class="table-light">
                  <tr>
                    <th class="actions-col">
                      <button type="button" id="addMelBtn"
                              class="btn btn-outline-primary btn-sm btn-icon"
                              title="Add entry">+</button>
                    </th>
                    <th style="width:7ch">ID</th>
                    <th>Glosses (comma-separated)</th>
                  </tr>
                </thead>
                <tbody id="mel-body">
                  <xsl:for-each select="semantics/mel">
                    <xsl:variable name="n" select="position()"/>
                    <tr>
                      <td class="actions-col">
                        <button type="button"
                                class="btn btn-outline-danger btn-sm btn-icon btn-del-mel-row"
                                title="Delete row">&#x2212;</button>
                      </td>
                      <td>
                        <input type="text" class="form-control form-control-sm"
                               name="mel-{$n}-id" id="mel-{$n}-id">
                          <xsl:attribute name="value">
                            <xsl:value-of select="@id"/>
                          </xsl:attribute>
                        </input>
                      </td>
                      <td>
                        <input type="text" class="form-control form-control-sm"
                               name="mel-{$n}-glosses" id="mel-{$n}-glosses">
                          <xsl:attribute name="value">
                            <xsl:for-each select="gl">
                              <xsl:value-of select="."/>
                              <xsl:if test="position()!=last()">, </xsl:if>
                            </xsl:for-each>
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
    var rows = document.querySelectorAll('#mel-body tr');
    rows.forEach(function(tr, i){
      var n = i + 1;
      var id_inp = tr.querySelector('input[name$="-id"]');
      var gl_inp = tr.querySelector('input[name$="-glosses"]');
      if(id_inp){ id_inp.name = 'mel-' + n + '-id';     id_inp.id = 'mel-' + n + '-id'; }
      if(gl_inp){ gl_inp.name = 'mel-' + n + '-glosses'; gl_inp.id = 'mel-' + n + '-glosses'; }
    });
  }
  document.addEventListener('click', function(ev){
    if(ev.target && ev.target.id === 'addMelBtn'){
      var tr = document.createElement('tr');
      tr.innerHTML =
        '<td class="actions-col"><button type="button" class="btn btn-outline-danger btn-sm btn-icon btn-del-mel-row" title="Delete row">&#x2212;</button></td>'
        + '<td><input type="text" class="form-control form-control-sm" placeholder="id"></td>'
        + '<td><input type="text" class="form-control form-control-sm" placeholder="gloss1, gloss2"></td>';
      document.getElementById('mel-body').appendChild(tr);
      reindex();
      return;
    }
    var del = ev.target.closest('.btn-del-mel-row');
    if(del){ del.closest('tr').remove(); reindex(); }
  });
})();
        ]]></script>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
