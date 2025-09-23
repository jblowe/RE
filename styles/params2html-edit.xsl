<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <!-- Config -->
  <xsl:param name="postTarget" select="'/save'"/>
  <xsl:param name="formId" select="'re-edit-form'"/>

  <xsl:output method="html" encoding="UTF-8" omit-xml-declaration="yes"/>

  <!-- Lightweight detection of sections present in DIS.*.correspondences.xml -->
  <xsl:variable name="rootName" select="name(/*)"/>
  <xsl:variable name="macro"
    select="/*/*[contains(translate(local-name(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'macro')][1]"/>
  <xsl:variable name="canon"
    select="/*/*[contains(translate(local-name(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'canon')][1]"/>
  <xsl:variable name="table"
    select="(/*/*[local-name()='correspondences' or local-name()='table' or local-name()='rows'])[1]"/>
  <xsl:variable name="rows" select="$table/*"/>
  <xsl:variable name="firstRow" select="$rows[1]"/>
  <xsl:variable name="hasTable" select="count($rows)&gt;0"/>
  <xsl:variable name="otherLeaf"
    select="/*/*[not(*) and
                 not(name()=name($macro)) and
                 not(name()=name($canon)) and
                 not(name()=name($table))]"/>

  <xsl:template match="/">
    <html lang="en">
      <head>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1"/>
        <title><xsl:value-of select="$rootName"/> — Editor</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"/>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css"/>
        <style>
          .table td, .table th { vertical-align: middle; }
          .cell-input { min-width: 6ch; }
          .actions-col { white-space: nowrap; }
          .sticky-actions { position: sticky; top: 0; z-index: 1030; background: #fff; padding: .5rem 0 1rem 0; }
        </style>
      </head>
      <body>
        <div class="container my-4">
          <header class="mb-3">
            <h1 class="h4 mb-0"><code><xsl:value-of select="$rootName"/></code> editor</h1>
            <small class="text-muted">Editable view (Bootstrap 5)</small>
          </header>

          <div class="sticky-actions d-flex gap-2 mb-3">
            <button type="button" id="saveBtn" class="btn btn-success">
              <i class="fa fa-floppy-disk"></i> Save
            </button>
            <xsl:if test="$hasTable">
              <button type="button" id="addRowTop" class="btn btn-outline-primary">
                <i class="fa fa-plus"></i> Add row
              </button>
            </xsl:if>
          </div>

          <form id="{$formId}" method="post" action="{$postTarget}" target="reSaveWindow">
            <!-- Hidden field that will carry the full serialized XML on Save -->
            <textarea id="payload" name="xml" class="d-none"></textarea>

            <!-- Macro-classes -->
            <xsl:if test="$macro">
              <div class="card mb-3">
                <div class="card-header fw-semibold">
                  Macro-classes
                  <small class="text-muted ms-2">(element: <code><xsl:value-of select="name($macro)"/></code>)</small>
                </div>
                <div class="card-body row g-3" id="macro">
                  <xsl:for-each select="$macro/*">
                    <xsl:variable name="mTag" select="name()"/>
                    <xsl:variable name="mName" select="@name"/>
                    <div class="col-12 col-md-6 col-lg-4">
                      <label class="form-label" for="macro-{$mTag}{@name}">
                        <code id="col-{$mTag}">
                          <xsl:choose>
                            <xsl:when test="$mName != ''"><xsl:value-of select="$mName"/></xsl:when>
                            <xsl:otherwise><xsl:value-of select="$mTag"/></xsl:otherwise>
                          </xsl:choose>
                        </code>
                      </label>
                      <input type="text"
                             class="form-control form-control-sm macro-inp"
                             id="macro-{$mTag}{@name}"
                             data-item-tag="{$mTag}"
                             data-item-name="{$mName}"
                             value="{normalize-space(.)}"/>
                    </div>
                  </xsl:for-each>
                </div>
              </div>
            </xsl:if>

            <!-- Syllable canon -->
            <xsl:if test="$canon">
              <div class="card mb-3">
                <div class="card-header fw-semibold">
                  Syllable canon
                  <small class="text-muted ms-2">(element: <code><xsl:value-of select="name($canon)"/></code>)</small>
                </div>
                <div class="card-body">
                  <input type="text" class="form-control" id="canon-input"
                         data-elt="{name($canon)}"
                         value="{normalize-space($canon)}"/>
                </div>
              </div>
            </xsl:if>

            <!-- Other leaf params -->
            <xsl:if test="count($otherLeaf)&gt;0">
              <div class="card mb-3">
                <div class="card-header fw-semibold">Other parameters</div>
                <div class="card-body row g-3" id="other-params">
                  <xsl:for-each select="$otherLeaf">
                    <div class="col-12 col-md-6 col-lg-4">
                      <label class="form-label" for="param-{name()}"><code id="col-{name()}"><xsl:value-of select="name()"/></code></label>
                      <input type="text" class="form-control form-control-sm param-inp"
                             id="param-{name()}" data-elt="{name()}" value="{normalize-space(.)}"/>
                    </div>
                  </xsl:for-each>
                </div>
              </div>
            </xsl:if>

            <!-- Correspondences table -->
            <xsl:if test="$hasTable">
              <div class="card mb-3">
                <div class="card-header fw-semibold">
                  Table of correspondences
                  <small class="text-muted ms-2">(table: <code><xsl:value-of select="name($table)"/></code>, row: <code><xsl:value-of select="name($rows[1])"/></code>)</small>
                </div>
                <div class="card-body p-0">
                  <div class="table-responsive">
                    <table class="table table-striped table-hover table-sm mb-0" id="corr-table">
                      <thead class="table-light">
                        <tr id="row-0">
                          <xsl:for-each select="$firstRow/*">
                            <th id="col-{name()}"><xsl:value-of select="name()"/></th>
                          </xsl:for-each>
                          <th class="actions-col">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        <xsl:for-each select="$rows">
                          <tr id="row-{position()}" data-row-index="{position()}">
                            <xsl:for-each select="*">
                              <td id="cell-r{../position()}-c{name()}" data-col="{name()}">
                                <input type="text" class="form-control form-control-sm cell-input"
                                       id="cell-r{../../position()}-c{name()}"
                                       data-col="{name()}"
                                       value="{normalize-space(.)}"/>
                              </td>
                            </xsl:for-each>
                            <td class="actions-col">
                              <button type="button" class="btn btn-outline-danger btn-sm btn-del-row" title="Delete row">
                                <i class="fa fa-minus"></i>
                              </button>
                            </td>
                          </tr>
                        </xsl:for-each>
                      </tbody>
                    </table>
                  </div>
                </div>
                <div class="card-footer">
                  <button type="button" id="addRowBottom" class="btn btn-outline-primary">
                    <i class="fa fa-plus"></i> Add row
                  </button>
                </div>
              </div>
            </xsl:if>
          </form>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
          (function(){
            var ROOT = "<xsl:value-of select='$rootName'/>";
            var MACRO_TAG = "<xsl:value-of select='name($macro)'/>";
            var CANON_TAG = "<xsl:value-of select='name($canon)'/>";
            var TABLE_TAG = "<xsl:value-of select='name($table)'/>";
            var ROW_TAG   = "<xsl:value-of select='name($rows[1])'/>";

            var COLS = [
              <xsl:for-each select="$firstRow/*">"<xsl:value-of select='name()'/>"<xsl:if test="position()!=last()">,</xsl:if></xsl:for-each>
            ];

            function q(s, c){return (c||document).querySelector(s);}
            function qa(s, c){return Array.prototype.slice.call((c||document).querySelectorAll(s));}
            function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&apos;');}

            function createRow(idx){
              var tr = document.createElement('tr');
              tr.id = 'row-'+idx;
              tr.setAttribute('data-row-index', idx);
              COLS.forEach(function(cn){
                var td = document.createElement('td');
                td.id = 'cell-r'+idx+'-c'+cn;
                td.setAttribute('data-col', cn);
                var inp = document.createElement('input');
                inp.type = 'text';
                inp.className = 'form-control form-control-sm cell-input';
                inp.id = 'cell-r'+idx+'-c'+cn;
                inp.setAttribute('data-col', cn);
                td.appendChild(inp);
                tr.appendChild(td);
              });
              var act = document.createElement('td');
              act.className = 'actions-col';
              act.innerHTML = '<button type="button" class="btn btn-outline-danger btn-sm btn-del-row" title="Delete row"><i class="fa fa-minus"></i></button>';
              tr.appendChild(act);
              return tr;
            }

            function addRow(){
              var tb = q('#corr-table tbody'); if(!tb) return;
              var rows = qa('tr', tb);
              var last = rows.length ? rows[rows.length-1] : null;
              var idx = last ? (parseInt(last.getAttribute('data-row-index')||'0',10)+1) : 1;
              tb.appendChild(createRow(idx));
            }

            var topBtn = q('#addRowTop'), botBtn = q('#addRowBottom');
            if(topBtn) topBtn.addEventListener('click', addRow);
            if(botBtn) botBtn.addEventListener('click', addRow);

            var tbody = q('#corr-table tbody');
            if(tbody){
              tbody.addEventListener('click', function(ev){
                var b = ev.target.closest('.btn-del-row'); if(!b) return;
                var tr = b.closest('tr'); if(tr) tr.remove();
              });
            }

            var save = q('#saveBtn');
            if(save){
              save.addEventListener('click', function(){
                var parts = [];
                parts.push('<?xml version="1.0" encoding="UTF-8"?>');
                parts.push('<'+ROOT+'>');

                if(MACRO_TAG){
                  parts.push('<'+MACRO_TAG+'>');
                  qa('#macro .macro-inp').forEach(function(inp){
                    var t = inp.getAttribute('data-item-tag') || 'item';
                    var n = inp.getAttribute('data-item-name') || '';
                    if(n){
                      parts.push('<'+t+' name="'+esc(n)+'">'+esc(inp.value)+'</'+t+'>');
                    }else{
                      parts.push('<'+t+'>'+esc(inp.value)+'</'+t+'>');
                    }
                  });
                  parts.push('</'+MACRO_TAG+'>');
                }

                if(CANON_TAG){
                  var ci = q('#canon-input');
                  parts.push('<'+CANON_TAG+'>'+esc(ci ? ci.value : '')+'</'+CANON_TAG+'>');
                }

                qa('#other-params .param-inp').forEach(function(inp){
                  var tag = inp.getAttribute('data-elt') || 'param';
                  parts.push('<'+tag+'>'+esc(inp.value)+'</'+tag+'>');
                });

                if(TABLE_TAG && ROW_TAG && COLS.length){
                  parts.push('<'+TABLE_TAG+'>');
                  qa('#corr-table tbody tr').forEach(function(tr){
                    parts.push('<'+ROW_TAG+'>');
                    COLS.forEach(function(cn){
                      var v = (tr.querySelector('input[data-col="'+cn+'"]')||{}).value || '';
                      parts.push('<'+cn+'>'+esc(v)+'</'+cn+'>');
                    });
                    parts.push('</'+ROW_TAG+'>');
                  });
                  parts.push('</'+TABLE_TAG+'>');
                }

                parts.push('</'+ROOT+'>');
                q('#payload').value = parts.join('');
                window.open('about:blank','reSaveWindow');
                document.getElementById('<xsl:value-of select="$formId"/>').submit();
              });
            }
          })();
        </script>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
