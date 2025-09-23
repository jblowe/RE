<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <!-- Config -->
    <xsl:param name="postTarget" select="'/edit'"/>
    <xsl:param name="formId" select="'toc-edit'"/>
    <xsl:param name="document_path" select="'/#tree#|#project#|#experiment#|#filename#'"

    <xsl:output method="html" encoding="UTF-8" omit-xml-declaration="yes"/>

    <!-- Root -->
    <xsl:template match="/">
        <html lang="en">
            <head>
                <meta charset="utf-8"/>
                <meta name="viewport" content="width=device-width, initial-scale=1"/>
                <title>Table of Correspondences</title>
                <style>
                    .table td, .table th { vertical-align: middle; }
                    .cell-input { min-width: 6ch; }
                    .actions-col { width: 1%; white-space: nowrap; }
                    .btn-icon { padding: .1rem .4rem; line-height: 1; }
                </style>
            </head>
            <body>
                <form id="{$formId}" method="post" action="{$postTarget}/">
                    <div class="container my-4">
                        <div class="col-md-12 mb-2">
                            <input type="hidden" name="document_path" value="{$document_path}"/>
                            <button type="submit" name="action" value="save" class="btn btn-success me-3">Save</button>
                            <button type="submit" name="action" value="upstream" class="btn btn-success me-3">Upstream</button>
                            <button type="submit" name="action" value="revert" class="btn btn-warning me-3">Revert</button>
                            <button type="submit" name="action" value="display" class="btn btn-warning me-3">Exit</button>
                        </div>
                        <xsl:apply-templates select=".//tableOfCorr"/>
                    </div>

                    <script><![CDATA[
          (function(){
            function q(s, c){return (c||document).querySelector(s);}
            function qa(s, c){return Array.prototype.slice.call((c||document).querySelectorAll(s));}

            function getDialects(){
              return qa('#corr-table thead th[data-dialect]').map(function(th){
                return th.getAttribute('data-dialect');
              });
            }

            function reindexRows(){
              var tbody = q('#corr-body'); if(!tbody) return;
              var rows = qa('tr', tbody);
              rows.forEach(function(tr, idx){
                var r = idx + 1;
                tr.id = 'row-' + r;
                // First five fixed columns in order: num, proto, syll, left, right
                var fixed = ['num','proto','syll','left','right'];
                fixed.forEach(function(key, i){
                  var inp = tr.querySelector('td:nth-child(' + (i+2) + ') input'); // +2 because col1 is actions
                  if(inp){
                    inp.name = 'r' + r + '-' + key;
                    inp.id   = 'in-r' + r + '-' + key;
                  }
                });
                // Dialect columns
                var dialects = getDialects();
                dialects.forEach(function(d, i){
                  var inp = tr.querySelector('td:nth-child(' + (i + 7) + ') input'); // actions(1) + 5 fixed = 6, so start at 7
                  if(inp){
                    inp.name = 'cell-r' + r + '-c-' + d;
                    inp.id   = 'in-r' + r + '-c-' + d;
                  }
                });
              });
            }

            function createRow(){
              var dialects = getDialects();
              var tr = document.createElement('tr');

              // Actions cell (delete button)
              var tdAct = document.createElement('td');
              tdAct.className = 'actions-col';
              var del = document.createElement('button');
              del.type = 'button';
              del.className = 'btn btn-outline-danger btn-sm btn-icon btn-del-row';
              del.title = 'Delete row';
              del.textContent = '−';
              tdAct.appendChild(del);
              tr.appendChild(tdAct);

              function makeCell(ph){
                var td = document.createElement('td');
                var inp = document.createElement('input');
                inp.type = 'text';
                inp.className = 'form-control form-control-sm cell-input';
                if(ph) inp.placeholder = ph;
                td.appendChild(inp);
                return td;
              }

              // Fixed cells
              tr.appendChild(makeCell('#'));      // num
              tr.appendChild(makeCell('*'));      // proto
              tr.appendChild(makeCell('syll'));   // syll
              tr.appendChild(makeCell('left'));   // left
              tr.appendChild(makeCell('right'));  // right

              // Dialect cells
              dialects.forEach(function(d){
                tr.appendChild(makeCell(d));
              });

              return tr;
            }

            // Add row
            function addRow(){
              var tbody = q('#corr-body'); if(!tbody) return;
              var tr = createRow();
              tbody.appendChild(tr);
              reindexRows();
            }

            // Wire up add and delete
            document.addEventListener('click', function(ev){
              if(ev.target && ev.target.id === 'addRowBtn'){
                addRow();
                return;
              }
              var del = ev.target.closest('.btn-del-row');
              if(del){
                var tr = del.closest('tr');
                if(tr){ tr.remove(); reindexRows(); }
                return;
              }
            });
          })();
        ]]></script>
                </form>
            </body>
        </html>
    </xsl:template>

    <!-- Render main structure -->
    <xsl:template match="tableOfCorr">
        <!-- Parameters -->
        <div class="card mb-3">
            <div class="card-header fw-semibold">Parameters</div>
            <div class="card-body">
                <!-- Canon (supports either parameters/canon or direct canon) -->
                <xsl:if test="parameters/canon or canon">
                    <div class="mb-3">
                        <label for="canon" class="form-label">canon</label>
                        <input type="text" class="form-control" id="canon" name="canon">
                            <xsl:attribute name="value">
                                <xsl:value-of select="(parameters/canon/@value | canon/@value)[1]"/>
                            </xsl:attribute>
                        </input>
                    </div>
                </xsl:if>

                <xsl:if test="parameters/context_match_type">
                    <div class="mb-3">
                        <label for="canon" class="form-label">context match type</label>
                        <input type="text" class="form-control" id="context_match_type" name="context_match_type">
                            <xsl:attribute name="value">
                                <xsl:value-of select="parameters/context_match_type/@value"/>
                            </xsl:attribute>
                        </input>
                    </div>
                </xsl:if>

                <!-- Classes (supports parameters/class or direct class) -->
                <xsl:if test="parameters/class or class">
                    <div class="table-responsive">
                        <table class="table table-sm table-striped" id="class-table">
                            <thead>
                                <tr>
                                    <th>class name</th>
                                    <th>members (value)</th>
                                </tr>
                            </thead>
                            <tbody>
                                <xsl:for-each select="parameters/class | class">
                                    <xsl:variable name="cpos" select="position()"/>
                                    <tr id="class-row-{$cpos}">
                                        <td>
                                            <input type="text" class="form-control form-control-sm"
                                                   name="class-{$cpos}-name" id="class-{$cpos}-name">
                                                <xsl:attribute name="value">
                                                    <xsl:value-of select="@name"/>
                                                </xsl:attribute>
                                            </input>
                                        </td>
                                        <td>
                                            <input type="text" class="form-control form-control-sm"
                                                   name="class-{$cpos}-value" id="class-{$cpos}-value">
                                                <xsl:attribute name="value">
                                                    <xsl:value-of select="@value"/>
                                                </xsl:attribute>
                                            </input>
                                        </td>
                                    </tr>
                                </xsl:for-each>
                            </tbody>
                        </table>
                    </div>
                </xsl:if>
            </div>
        </div>

        <!-- Correspondences (corr are direct children of tableOfCorr) -->
        <div class="card mb-3">
            <div class="card-header fw-semibold">Correspondences</div>
            <div class="card-body p-0">
                <div class="table-responsive">
                    <table class="table table-sm table-hover table-bordered mb-0" id="corr-table">
                        <thead class="table-light">
                            <tr>
                                <th class="actions-col">
                                    <button type="button" id="addRowBtn" class="btn btn-outline-primary btn-sm btn-icon"
                                            title="Add row">+
                                    </button>
                                </th>
                                <th>num</th>
                                <th>*</th>
                                <th>syll</th>
                                <th>left</th>
                                <th>right</th>
                                <xsl:for-each select="corr[1]/modern">
                                    <th data-dialect="{@dialecte}">
                                        <xsl:value-of select="@dialecte"/>
                                    </th>
                                </xsl:for-each>
                            </tr>
                        </thead>
                        <tbody id="corr-body">
                            <xsl:for-each select="corr">
                                <xsl:variable name="rpos" select="position()"/>
                                <tr id="row-{$rpos}">
                                    <!-- actions (delete) -->
                                    <td class="actions-col">
                                        <button type="button" class="btn btn-outline-danger btn-sm btn-icon btn-del-row"
                                                title="Delete row">-
                                        </button>
                                    </td>

                                    <!-- num -->
                                    <td>
                                        <input type="text" class="form-control form-control-sm cell-input"
                                               name="r{$rpos}-num" id="in-r{$rpos}-num">
                                            <xsl:attribute name="value">
                                                <xsl:value-of select="@num"/>
                                            </xsl:attribute>
                                        </input>
                                    </td>

                                    <!-- proto text -->
                                    <td>
                                        <input type="text" class="form-control form-control-sm cell-input"
                                               name="r{$rpos}-proto" id="in-r{$rpos}-proto">
                                            <xsl:attribute name="value">
                                                <xsl:value-of select="normalize-space(proto)"/>
                                            </xsl:attribute>
                                        </input>
                                    </td>

                                    <!-- proto/@syll -->
                                    <td>
                                        <input type="text" class="form-control form-control-sm cell-input"
                                               name="r{$rpos}-syll" id="in-r{$rpos}-syll">
                                            <xsl:attribute name="value">
                                                <xsl:value-of select="proto/@syll"/>
                                            </xsl:attribute>
                                        </input>
                                    </td>

                                    <!-- proto/@contextL -->
                                    <td>
                                        <input type="text" class="form-control form-control-sm cell-input"
                                               name="r{$rpos}-left" id="in-r{$rpos}-left">
                                            <xsl:attribute name="value">
                                                <xsl:value-of select="proto/@contextL"/>
                                            </xsl:attribute>
                                        </input>
                                    </td>

                                    <!-- proto/@contextR -->
                                    <td>
                                        <input type="text" class="form-control form-control-sm cell-input"
                                               name="r{$rpos}-right" id="in-r{$rpos}-right">
                                            <xsl:attribute name="value">
                                                <xsl:value-of select="proto/@contextR"/>
                                            </xsl:attribute>
                                        </input>
                                    </td>

                                    <!-- Modern dialect columns -->
                                    <xsl:for-each select="modern">
                                        <xsl:variable name="dial" select="@dialecte"/>
                                        <td>
                                            <input type="text" class="form-control form-control-sm cell-input"
                                                   name="cell-r{$rpos}-c-{$dial}" id="in-r{$rpos}-c-{$dial}">
                                                <xsl:attribute name="value">
                                                    <xsl:for-each select="seg">
                                                        <xsl:if test="@statut='doute'">=</xsl:if>
                                                        <xsl:value-of select="normalize-space(.)"/>
                                                        <xsl:if test="position()!=last()">,</xsl:if>
                                                    </xsl:for-each>
                                                </xsl:attribute>
                                            </input>
                                        </td>
                                    </xsl:for-each>
                                </tr>
                            </xsl:for-each>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Rules (rules appear as direct children <rule>) -->
        <xsl:if test="rule">
            <div class="card mb-3">
                <div class="card-header fw-semibold">Rules</div>
                <div class="card-body p-0">
                    <div class="table-responsive">
                        <table class="table table-sm table-striped mb-0" id="rules-table">
                            <thead>
                                <tr>
                                    <th>num</th>
                                    <th>input</th>
                                    <th>output</th>
                                    <th>contextL</th>
                                    <th>contextR</th>
                                    <th>stage</th>
                                    <th>languages</th>
                                </tr>
                            </thead>
                            <tbody>
                                <xsl:for-each select="rule">
                                    <xsl:variable name="r" select="position()"/>
                                    <tr id="rule-row-{$r}">
                                        <td>
                                            <input type="text" class="form-control form-control-sm"
                                                   name="rule-{$r}-num" id="rule-{$r}-num">
                                                <xsl:attribute name="value">
                                                    <xsl:value-of select="@num"/>
                                                </xsl:attribute>
                                            </input>
                                        </td>
                                        <td>
                                            <input type="text" class="form-control form-control-sm"
                                                   name="rule-{$r}-input" id="rule-{$r}-input">
                                                <xsl:attribute name="value">
                                                    <xsl:value-of select="normalize-space(input)"/>
                                                </xsl:attribute>
                                            </input>
                                        </td>
                                        <td>
                                            <input type="text" class="form-control form-control-sm"
                                                   name="rule-{$r}-output" id="rule-{$r}-output">
                                                <xsl:attribute name="value">
                                                    <xsl:value-of select="normalize-space(outcome)"/>
                                                </xsl:attribute>
                                            </input>
                                        </td>
                                        <td>
                                            <input type="text" class="form-control form-control-sm"
                                                   name="rule-{$r}-contextL" id="rule-{$r}-contextL">
                                                <xsl:attribute name="value">
                                                    <xsl:value-of select="input/@contextL"/>
                                                </xsl:attribute>
                                            </input>
                                        </td>
                                        <td>
                                            <input type="text" class="form-control form-control-sm"
                                                   name="rule-{$r}-contextR" id="rule-{$r}-contextR">
                                                <xsl:attribute name="value">
                                                    <xsl:value-of select="input/@contextR"/>
                                                </xsl:attribute>
                                            </input>
                                        </td>
                                        <td>
                                            <input type="text" class="form-control form-control-sm"
                                                   name="rule-{$r}-stage" id="rule-{$r}-stage">
                                                <xsl:attribute name="value">
                                                    <xsl:value-of select="@stage"/>
                                                </xsl:attribute>
                                            </input>
                                        </td>
                                        <td>
                                            <input type="text" class="form-control form-control-sm"
                                                   name="rule-{$r}-languages" id="rule-{$r}-languages">
                                                <xsl:attribute name="value">
                                                    <xsl:value-of select="outcome/@languages"/>
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
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>
