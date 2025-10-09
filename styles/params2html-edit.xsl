<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:param name="postTarget" select="'/edit'"/>
  <xsl:param name="formId" select="'params-edit-form'"/>
  <xsl:output method="html" indent="yes" encoding="utf-8"/>
  <xsl:template match="/">
    <html>
      <head>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1"/>
        <title>Parameters — Editor</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"/>
        <style>
          .actions-col { width:1%; white-space:nowrap; }
          .btn-icon { padding:.1rem .45rem; line-height:1; }
          .card + .card { margin-top:1rem; }
          .recon-card .card-header { display:flex; align-items:center; justify-content:space-between; }
          .small-input { max-width: 22rem; }
          .table td, .table th { vertical-align: middle; }
          .muted { color:#6c757d; }
        </style>
      </head>
      <body>
        <div class="container my-4">
          <h1 class="h5 mb-3">Master parameters — editable</h1>
          <form id="{$formId}" method="post" action="{$postTarget}" target="paramsSaveWindow">
            <textarea id="payload" name="xml" class="d-none"/>
            <xsl:apply-templates select="/params"/>
            <div class="mt-3">
              <button type="submit" class="btn btn-success">Save</button>
            </div>
          </form>
        </div>
        <script><![CDATA[
          (function(){
            function q(s,c){return (c||document).querySelector(s);}
            function qa(s,c){return Array.prototype.slice.call((c||document).querySelectorAll(s));}
            function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&apos;');}

            // ---- Reconstructions ----
            function addRecon(){
              var list = q('#recon-list');
              var card = document.createElement('div');
              card.className = 'card';
              card.setAttribute('data-type','reconstruction');
              card.innerHTML =
                '<div class="card-header d-flex justify-content-between align-items-center">'
                + '<div class="d-flex gap-2 align-items-center">'
                + '<span class="muted">name:</span>'
                + '<input type="text" class="form-control form-control-sm small-input" name="recon-new-name" value=""/>'
                + '</div>'
                + '<button type="button" class="btn btn-outline-danger btn-sm btn-icon btn-del-recon" title="Delete reconstruction">−</button>'
                + '</div>'
                + '<div class="card-body">'
                + '<div class="row g-3">'
                + '<div class="col-12 col-md-6"><label class="form-label small mb-1">proto_language @name</label><input type="text" class="form-control form-control-sm" name="recon-new-proto-name" value=""/></div>'
                + '<div class="col-12 col-md-6"><label class="form-label small mb-1">proto_language @correspondences</label><input type="text" class="form-control form-control-sm" name="recon-new-proto-corr" value=""/></div>'
                + '<div class="col-12"><label class="form-label small mb-1">title @value</label><input type="text" class="form-control form-control-sm" name="recon-new-title" value=""/></div>'
                + '</div>'
                + '<div class="mt-3">'
                + '<div class="d-flex justify-content-between align-items-center mb-2"><strong class="small">Actions</strong><button type="button" class="btn btn-outline-secondary btn-sm btn-icon btn-add-action" title="Add action">+</button></div>'
                + '<div class="table-responsive"><table class="table table-sm table-striped mb-0 action-table"><thead><tr><th class="actions-col"></th><th>name</th><th>target</th><th>from</th><th>to</th></tr></thead><tbody></tbody></table></div>'
                + '</div>'
                + '</div>';
              list.insertBefore(card, list.firstChild);
            }
            function addAction(btn){
              var card = btn.closest('.card');
              var tbody = card.querySelector('.action-table tbody');
              var tr = document.createElement('tr');
              tr.innerHTML = '<td class="actions-col"><button type="button" class="btn btn-outline-danger btn-sm btn-icon btn-del-action">−</button></td>'
                           + '<td><input type="text" class="form-control form-control-sm" name="action-new-name"/></td>'
                           + '<td><input type="text" class="form-control form-control-sm" name="action-new-target"/></td>'
                           + '<td><input type="text" class="form-control form-control-sm" name="action-new-from"/></td>'
                           + '<td><input type="text" class="form-control form-control-sm" name="action-new-to"/></td>';
              tbody.appendChild(tr);
            }

            // ---- Simple list helpers for tables ----
            function addRow(tbodySel, prefix){
              var tb = q(tbodySel); if(!tb) return;
              var idx = qa('tr', tb).length + 1;
              var tr = document.createElement('tr');
              tr.setAttribute('data-index', idx);
              tr.innerHTML = '<td class="actions-col"><button type="button" class="btn btn-outline-danger btn-sm btn-icon btn-del-generic">−</button></td>'
                           + '<td><input type="text" class="form-control form-control-sm" name="'+prefix+'-'+idx+'-name"/></td>'
                           + '<td><input type="text" class="form-control form-control-sm" name="'+prefix+'-'+idx+'-file"/></td>';
              tb.insertBefore(tr, tb.firstChild);
            }
            function addParamRow(){
              var tb = q('#param-body'); if(!tb) return;
              var idx = qa('tr', tb).length + 1;
              var tr = document.createElement('tr');
              tr.setAttribute('data-index', idx);
              tr.innerHTML = '<td class="actions-col"><button type="button" class="btn btn-outline-danger btn-sm btn-icon btn-del-generic">−</button></td>'
                           + '<td><input type="text" class="form-control form-control-sm" name="param-'+idx+'-name"/></td>'
                           + '<td><input type="text" class="form-control form-control-sm" name="param-'+idx+'-value"/></td>';
              tb.insertBefore(tr, tb.firstChild);
            }

            // ---- Delegated events ----
            document.addEventListener('click', function(ev){
              if(ev.target.id === 'add-recon'){ addRecon(); return; }
              if(ev.target.id === 'add-attested'){ addRow('#attested-body','attested'); return; }
              if(ev.target.id === 'add-mel'){ addRow('#mel-body','mel'); return; }
              if(ev.target.id === 'add-fuzzy'){ addRow('#fuzzy-body','fuzzy'); return; }
              if(ev.target.id === 'add-param'){ addParamRow(); return; }

              var btn;
              if((btn = ev.target.closest('.btn-add-action'))){ addAction(btn); return; }
              if((btn = ev.target.closest('.btn-del-recon'))){ btn.closest('.card').remove(); return; }
              if((btn = ev.target.closest('.btn-del-action'))){ btn.closest('tr').remove(); return; }
              if((btn = ev.target.closest('.btn-del-generic'))){ btn.closest('tr').remove(); return; }
            });

            // ---- Serialize to XML and submit ----
            function serialize(){
              var parts = [];
              parts.push('<?xml version="1.0" encoding="utf-8"?>');
              parts.push('<params>');

              // attested
              var att = q('#attested-body'); if(att){
                qa('#attested-body tr').forEach(function(tr){
                  var name = tr.querySelector('input[name*="-name"]').value || '';
                  var file = tr.querySelector('input[name*="-file"]').value || '';
                  if(name || file){
                    parts.push('<attested name="'+esc(name)+'" file="'+esc(file)+'"/>');
                  }
                });
              }

              // mel
              var mel = q('#mel-body'); if(mel){
                qa('#mel-body tr').forEach(function(tr){
                  var name = tr.querySelector('input[name*="-name"]').value || '';
                  var file = tr.querySelector('input[name*="-file"]').value || '';
                  if(name || file){
                    parts.push('<mel name="'+esc(name)+'" file="'+esc(file)+'"/>');
                  }
                });
              }

              // fuzzy
              var fz = q('#fuzzy-body'); if(fz){
                qa('#fuzzy-body tr').forEach(function(tr){
                  var name = tr.querySelector('input[name*="-name"]').value || '';
                  var file = tr.querySelector('input[name*="-file"]').value || '';
                  if(name || file){
                    parts.push('<fuzzy name="'+esc(name)+'" file="'+esc(file)+'"/>');
                  }
                });
              }

              // reconstructions
              qa('#recon-list > .card').forEach(function(card){
                var rname = (card.querySelector('input[name$="-name"]') || card.querySelector('input[name="recon-new-name"]') || {}).value || '';
                parts.push('<reconstruction name="'+esc(rname)+'">');

                var pname = (card.querySelector('input[name$="-proto-name"]') || card.querySelector('input[name="recon-new-proto-name"]') || {}).value || '';
                var pcorr = (card.querySelector('input[name$="-proto-corr"]') || card.querySelector('input[name="recon-new-proto-corr"]') || {}).value || '';
                parts.push('<proto_language name="'+esc(pname)+'" correspondences="'+esc(pcorr)+'"/>');

                qa(card.querySelectorAll('.action-table tbody tr')).forEach(function(tr){
                  var aname = (tr.querySelector('input[name$="-name"]') || tr.querySelector('input[name="action-new-name"]') || {}).value || '';
                  var atgt  = (tr.querySelector('input[name$="-target"]') || tr.querySelector('input[name="action-new-target"]') || {}).value || '';
                  var afrom = (tr.querySelector('input[name$="-from"]') || tr.querySelector('input[name="action-new-from"]') || {}).value || '';
                  var ato   = (tr.querySelector('input[name$="-to"]') || tr.querySelector('input[name="action-new-to"]') || {}).value || '';
                  parts.push('<action'
                              + (aname? ' name="'+esc(aname)+'"':'')
                              + (atgt?  ' target="'+esc(atgt)+'"':'')
                              + (afrom? ' from="'+esc(afrom)+'"':'')
                              + (ato?   ' to="'+esc(ato)+'"':'')
                              + '/>');
                });

                var title = (card.querySelector('input[name$="-title"]') || card.querySelector('input[name="recon-new-title"]') || {}).value || '';
                parts.push('<title value="'+esc(title)+'"/>');

                parts.push('</reconstruction>');
              });

              // other params
              var op = q('#param-body'); if(op){
                qa('#param-body tr').forEach(function(tr){
                  var name = tr.querySelector('input[name*="-name"]').value || '';
                  var val  = tr.querySelector('input[name*="-value"]').value || '';
                  if(name || val){
                    parts.push('<param name="'+esc(name)+'" value="'+esc(val)+'"/>');
                  }
                });
              }

              parts.push('</params>');
              return parts.join('');
            }

            var form = q('#params-edit-form');
            if(form){
              form.addEventListener('submit', function(ev){
                var xml = serialize();
                q('#payload').value = xml;
                window.open('about:blank','paramsSaveWindow');
              });
            }
          })();
        ]]></script>
      </body>
    </html>
  </xsl:template>
  <xsl:template match="params">
    <!-- Reconstructions -->
    <div class="card recon-card">
      <div class="card-header">
        <strong>Reconstructions</strong>
        <div>
          <button type="button" id="add-recon" class="btn btn-outline-primary btn-sm btn-icon" title="Add reconstruction">+</button>
        </div>
      </div>
      <div class="card-body">
        <div id="recon-list" class="d-flex flex-column gap-3">
          <xsl:apply-templates select="reconstruction"/>
        </div>
      </div>
    </div>
    <!-- Lexicons (attested) -->
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <strong>Lexicons (attested)</strong>
        <button type="button" id="add-attested" class="btn btn-outline-primary btn-sm btn-icon" title="Add attested">+</button>
      </div>
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-sm table-striped mb-0" id="attested-table">
            <thead>
              <tr>
                <th class="actions-col"/>
                <th>name</th>
                <th>file</th>
              </tr>
            </thead>
            <tbody id="attested-body">
              <xsl:for-each select="attested">
                <xsl:variable name="k" select="position()"/>
                <tr data-index="{$k}">
                  <td class="actions-col">
                    <button type="button" class="btn btn-outline-danger btn-sm btn-icon btn-del-generic">−</button>
                  </td>
                  <td>
                    <input type="text" class="form-control form-control-sm" name="attested-{$k}-name" value="{@name}"/>
                  </td>
                  <td>
                    <input type="text" class="form-control form-control-sm" name="attested-{$k}-file" value="{@file}"/>
                  </td>
                </tr>
              </xsl:for-each>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    <!-- MELs -->
    <xsl:if test="mel">
      <div class="card">
        <div class="card-header d-flex justify-content-between align-items-center">
          <strong>MELs</strong>
          <button type="button" id="add-mel" class="btn btn-outline-primary btn-sm btn-icon">+</button>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-sm table-striped mb-0" id="mel-table">
              <thead>
                <tr>
                  <th class="actions-col"/>
                  <th>name</th>
                  <th>file</th>
                </tr>
              </thead>
              <tbody id="mel-body">
                <xsl:for-each select="mel">
                  <xsl:variable name="k" select="position()"/>
                  <tr data-index="{$k}">
                    <td class="actions-col">
                      <button type="button" class="btn btn-outline-danger btn-sm btn-icon btn-del-generic">−</button>
                    </td>
                    <td>
                      <input type="text" class="form-control form-control-sm" name="mel-{$k}-name" value="{@name}"/>
                    </td>
                    <td>
                      <input type="text" class="form-control form-control-sm" name="mel-{$k}-file" value="{@file}"/>
                    </td>
                  </tr>
                </xsl:for-each>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </xsl:if>
    <!-- Fuzzy -->
    <xsl:if test="fuzzy">
      <div class="card">
        <div class="card-header d-flex justify-content-between align-items-center">
          <strong>Fuzzy files</strong>
          <button type="button" id="add-fuzzy" class="btn btn-outline-primary btn-sm btn-icon">+</button>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-sm table-striped mb-0" id="fuzzy-table">
              <thead>
                <tr>
                  <th class="actions-col"/>
                  <th>name</th>
                  <th>file</th>
                </tr>
              </thead>
              <tbody id="fuzzy-body">
                <xsl:for-each select="fuzzy">
                  <xsl:variable name="k" select="position()"/>
                  <tr data-index="{$k}">
                    <td class="actions-col">
                      <button type="button" class="btn btn-outline-danger btn-sm btn-icon btn-del-generic">−</button>
                    </td>
                    <td>
                      <input type="text" class="form-control form-control-sm" name="fuzzy-{$k}-name" value="{@name}"/>
                    </td>
                    <td>
                      <input type="text" class="form-control form-control-sm" name="fuzzy-{$k}-file" value="{@file}"/>
                    </td>
                  </tr>
                </xsl:for-each>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </xsl:if>
    <!-- Other params -->
    <xsl:if test="param">
      <div class="card">
        <div class="card-header d-flex justify-content-between align-items-center">
          <strong>Other parameters</strong>
          <button type="button" id="add-param" class="btn btn-outline-primary btn-sm btn-icon">+</button>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-sm table-striped mb-0" id="param-table">
              <thead>
                <tr>
                  <th class="actions-col"/>
                  <th>name</th>
                  <th>value</th>
                </tr>
              </thead>
              <tbody id="param-body">
                <xsl:for-each select="param">
                  <xsl:variable name="k" select="position()"/>
                  <tr data-index="{$k}">
                    <td class="actions-col">
                      <button type="button" class="btn btn-outline-danger btn-sm btn-icon btn-del-generic">−</button>
                    </td>
                    <td>
                      <input type="text" class="form-control form-control-sm" name="param-{$k}-name" value="{@name}"/>
                    </td>
                    <td>
                      <input type="text" class="form-control form-control-sm" name="param-{$k}-value" value="{@value}"/>
                    </td>
                  </tr>
                </xsl:for-each>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </xsl:if>
  </xsl:template>
  <xsl:template match="reconstruction">
    <xsl:variable name="ridx" select="position()"/>
    <div class="card" data-type="reconstruction" data-ridx="{$ridx}">
      <div class="card-header d-flex justify-content-between align-items-center">
        <div class="d-flex gap-2 align-items-center">
          <span class="muted">name:</span>
          <input type="text" class="form-control form-control-sm small-input" name="recon-{$ridx}-name" value="{@name}"/>
        </div>
        <button type="button" class="btn btn-outline-danger btn-sm btn-icon btn-del-recon" title="Delete reconstruction">−</button>
      </div>
      <div class="card-body">
        <div class="row g-3">
          <div class="col-12 col-md-6">
            <label class="form-label small mb-1">proto_language @name</label>
            <input type="text" class="form-control form-control-sm" name="recon-{$ridx}-proto-name" value="{proto_language/@name}"/>
          </div>
          <div class="col-12 col-md-6">
            <label class="form-label small mb-1">proto_language @correspondences</label>
            <input type="text" class="form-control form-control-sm" name="recon-{$ridx}-proto-corr" value="{proto_language/@correspondences}"/>
          </div>
          <div class="col-12">
            <label class="form-label small mb-1">title @value</label>
            <input type="text" class="form-control form-control-sm" name="recon-{$ridx}-title" value="{title/@value}"/>
          </div>
        </div>
        <div class="mt-3">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <strong class="small">Actions</strong>
            <button type="button" class="btn btn-outline-secondary btn-sm btn-icon btn-add-action" title="Add action">+</button>
          </div>
          <div class="table-responsive">
            <table class="table table-sm table-striped mb-0 action-table">
              <thead>
                <tr>
                  <th class="actions-col"/>
                  <th>name</th>
                  <th>target</th>
                  <th>from</th>
                  <th>to</th>
                </tr>
              </thead>
              <tbody>
                <xsl:for-each select="action">
                  <xsl:variable name="aidx" select="position()"/>
                  <tr data-aidx="{$aidx}">
                    <td class="actions-col">
                      <button type="button" class="btn btn-outline-danger btn-sm btn-icon btn-del-action" title="Delete action">−</button>
                    </td>
                    <td>
                      <input type="text" class="form-control form-control-sm" name="recon-{$ridx}-action-{$aidx}-name" value="{@name}"/>
                    </td>
                    <td>
                      <input type="text" class="form-control form-control-sm" name="recon-{$ridx}-action-{$aidx}-target" value="{@target}"/>
                    </td>
                    <td>
                      <input type="text" class="form-control form-control-sm" name="recon-{$ridx}-action-{$aidx}-from" value="{@from}"/>
                    </td>
                    <td>
                      <input type="text" class="form-control form-control-sm" name="recon-{$ridx}-action-{$aidx}-to" value="{@to}"/>
                    </td>
                  </tr>
                </xsl:for-each>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </xsl:template>
</xsl:stylesheet>
