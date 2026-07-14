<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:param name="formId" select="'toc-edit'"/>
    <xsl:output method="html" encoding="UTF-8" omit-xml-declaration="yes"/>
    <xsl:template match="/">
        <div>
                <xsl:apply-templates select="tableOfCorr"/>
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

            // Generic add/delete/reindex for simple (non-dialect) tables: Rules, Exceptions.
            function makeSimpleTable(tbodySel, rowIdPrefix, fieldPrefix, fields, delClass){
              function reindex(){
                var tbody = q(tbodySel); if(!tbody) return;
                qa('tr', tbody).forEach(function(tr, idx){
                  var r = idx + 1;
                  tr.id = rowIdPrefix + '-' + r;
                  fields.forEach(function(key, i){
                    var inp = tr.querySelector('td:nth-child(' + (i + 2) + ') input');
                    if(inp){
                      inp.name = fieldPrefix + '-' + r + '-' + key;
                      inp.id   = fieldPrefix + '-' + r + '-' + key;
                    }
                  });
                });
              }
              function add(){
                var tbody = q(tbodySel); if(!tbody) return;
                var tr = document.createElement('tr');
                var tdAct = document.createElement('td');
                tdAct.className = 'actions-col';
                var del = document.createElement('button');
                del.type = 'button';
                del.className = 'btn btn-outline-danger btn-sm btn-icon ' + delClass;
                del.title = 'Delete row';
                del.textContent = '−';
                tdAct.appendChild(del);
                tr.appendChild(tdAct);
                fields.forEach(function(){
                  var td = document.createElement('td');
                  var inp = document.createElement('input');
                  inp.type = 'text';
                  inp.className = 'form-control form-control-sm';
                  td.appendChild(inp);
                  tr.appendChild(td);
                });
                tbody.appendChild(tr);
                reindex();
              }
              return {add: add, reindex: reindex};
            }

            var ruleRows = makeSimpleTable('#rules-body', 'rule-row', 'rule',
              ['num','input','output','contextL','contextR','stage','languages'],
              'btn-del-rule-row');
            var quirkRows = makeSimpleTable('#quirks-body', 'quirk-row', 'quirk',
              ['id','source_id','lg','lx','gl','alternative','analysis_slot','analysis_value','note'],
              'btn-del-quirk-row');

            // Wire up add and delete
            document.addEventListener('click', function(ev){
              if(ev.target && ev.target.id === 'addRowBtn'){
                addRow();
                return;
              }
              if(ev.target && ev.target.id === 'addRuleRowBtn'){
                ruleRows.add();
                return;
              }
              if(ev.target && ev.target.id === 'addQuirkRowBtn'){
                quirkRows.add();
                return;
              }
              var del = ev.target.closest('.btn-del-row');
              if(del){
                var tr = del.closest('tr');
                if(tr){ tr.remove(); reindexRows(); }
                return;
              }
              var delRule = ev.target.closest('.btn-del-rule-row');
              if(delRule){
                var tr2 = delRule.closest('tr');
                if(tr2){ tr2.remove(); ruleRows.reindex(); }
                return;
              }
              var delQuirk = ev.target.closest('.btn-del-quirk-row');
              if(delQuirk){
                var tr3 = delQuirk.closest('tr');
                if(tr3){ tr3.remove(); quirkRows.reindex(); }
                return;
              }
            });
          })();
        ]]></script>
        </div>
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

                <div class="mb-3">
                    <label for="spec" class="form-label">Supra-segmentals</label>
                    <input type="text" class="form-control" id="spec" name="spec">
                        <xsl:attribute name="value">
                            <xsl:value-of select="parameters/spec/@value"/>
                        </xsl:attribute>
                    </input>
                </div>

                <div class="mb-3">
                    <label class="form-label d-block">Context match type</label>
                    <div class="form-check form-check-inline">
                        <input class="form-check-input" type="radio"
                               name="context_match_type" id="cmt-constituent" value="constituent">
                            <xsl:if test="not(parameters/context_match_type/@value = 'glyphs')">
                                <xsl:attribute name="checked">checked</xsl:attribute>
                            </xsl:if>
                        </input>
                        <label class="form-check-label" for="cmt-constituent">constituent</label>
                    </div>
                    <div class="form-check form-check-inline">
                        <input class="form-check-input" type="radio"
                               name="context_match_type" id="cmt-glyphs" value="glyphs">
                            <xsl:if test="parameters/context_match_type/@value = 'glyphs'">
                                <xsl:attribute name="checked">checked</xsl:attribute>
                            </xsl:if>
                        </input>
                        <label class="form-check-label" for="cmt-glyphs">glyphs</label>
                    </div>
                </div>

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

                                    <!-- Modern dialect columns: iterate over the CANONICAL column
                                         list so missing <modern> elements produce an empty cell in
                                         the correct column rather than shifting subsequent cells left. -->
                                    <xsl:variable name="this-corr" select="."/>
                                    <xsl:for-each select="../corr[1]/modern">
                                        <xsl:variable name="d"    select="@dialecte"/>
                                        <xsl:variable name="cell" select="$this-corr/modern[@dialecte = $d]"/>
                                        <td>
                                            <input type="text" class="form-control form-control-sm cell-input"
                                                   name="cell-r{$rpos}-c-{$d}" id="in-r{$rpos}-c-{$d}">
                                                <xsl:attribute name="value">
                                                    <xsl:for-each select="$cell/seg">
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
        <div class="card mb-3">
            <div class="card-header d-flex justify-content-between align-items-center fw-semibold">
                <span>Rules</span>
                <button type="button" id="addRuleRowBtn" class="btn btn-outline-primary btn-sm btn-icon"
                        title="Add rule">+
                </button>
            </div>
            <div class="card-body p-0">
                <div class="table-responsive">
                    <table class="table table-sm table-striped mb-0" id="rules-table">
                        <thead>
                            <tr>
                                <th class="actions-col"/>
                                <th>num</th>
                                <th>input</th>
                                <th>output</th>
                                <th>contextL</th>
                                <th>contextR</th>
                                <th>stage</th>
                                <th>languages</th>
                            </tr>
                        </thead>
                        <tbody id="rules-body">
                            <xsl:for-each select="rule">
                                <xsl:variable name="r" select="position()"/>
                                <tr id="rule-row-{$r}">
                                    <td class="actions-col">
                                        <button type="button" class="btn btn-outline-danger btn-sm btn-icon btn-del-rule-row"
                                                title="Delete rule">-
                                        </button>
                                    </td>
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

        <!-- Exceptions (quirks appear as direct children <quirk>) -->
        <div class="card mb-3">
            <div class="card-header d-flex justify-content-between align-items-center fw-semibold">
                <span>Exceptions</span>
                <button type="button" id="addQuirkRowBtn" class="btn btn-outline-primary btn-sm btn-icon"
                        title="Add exception">+
                </button>
            </div>
            <div class="card-body p-0">
                <div class="table-responsive">
                    <table class="table table-sm table-striped mb-0" id="quirks-table">
                        <thead>
                            <tr>
                                <th class="actions-col"/>
                                <th>id</th>
                                <th>source id</th>
                                <th>lang</th>
                                <th>lexeme</th>
                                <th>gloss</th>
                                <th>alternative</th>
                                <th>analysis slot</th>
                                <th>analysis value</th>
                                <th>notes</th>
                            </tr>
                        </thead>
                        <tbody id="quirks-body">
                            <xsl:for-each select="quirk">
                                <xsl:variable name="q" select="position()"/>
                                <tr id="quirk-row-{$q}">
                                    <td class="actions-col">
                                        <button type="button" class="btn btn-outline-danger btn-sm btn-icon btn-del-quirk-row"
                                                title="Delete exception">-
                                        </button>
                                    </td>
                                    <td>
                                        <input type="text" class="form-control form-control-sm"
                                               name="quirk-{$q}-id" id="quirk-{$q}-id">
                                            <xsl:attribute name="value">
                                                <xsl:value-of select="@id"/>
                                            </xsl:attribute>
                                        </input>
                                    </td>
                                    <td>
                                        <input type="text" class="form-control form-control-sm"
                                               name="quirk-{$q}-source_id" id="quirk-{$q}-source_id">
                                            <xsl:attribute name="value">
                                                <xsl:value-of select="normalize-space(source_id)"/>
                                            </xsl:attribute>
                                        </input>
                                    </td>
                                    <td>
                                        <input type="text" class="form-control form-control-sm"
                                               name="quirk-{$q}-lg" id="quirk-{$q}-lg">
                                            <xsl:attribute name="value">
                                                <xsl:value-of select="normalize-space(lg)"/>
                                            </xsl:attribute>
                                        </input>
                                    </td>
                                    <td>
                                        <input type="text" class="form-control form-control-sm"
                                               name="quirk-{$q}-lx" id="quirk-{$q}-lx">
                                            <xsl:attribute name="value">
                                                <xsl:value-of select="normalize-space(lx)"/>
                                            </xsl:attribute>
                                        </input>
                                    </td>
                                    <td>
                                        <input type="text" class="form-control form-control-sm"
                                               name="quirk-{$q}-gl" id="quirk-{$q}-gl">
                                            <xsl:attribute name="value">
                                                <xsl:value-of select="normalize-space(gl)"/>
                                            </xsl:attribute>
                                        </input>
                                    </td>
                                    <td>
                                        <input type="text" class="form-control form-control-sm"
                                               name="quirk-{$q}-alternative" id="quirk-{$q}-alternative">
                                            <xsl:attribute name="value">
                                                <xsl:value-of select="normalize-space(alternative)"/>
                                            </xsl:attribute>
                                        </input>
                                    </td>
                                    <td>
                                        <input type="text" class="form-control form-control-sm"
                                               name="quirk-{$q}-analysis_slot" id="quirk-{$q}-analysis_slot">
                                            <xsl:attribute name="value">
                                                <xsl:value-of select="normalize-space(analysis_slot)"/>
                                            </xsl:attribute>
                                        </input>
                                    </td>
                                    <td>
                                        <input type="text" class="form-control form-control-sm"
                                               name="quirk-{$q}-analysis_value" id="quirk-{$q}-analysis_value">
                                            <xsl:attribute name="value">
                                                <xsl:value-of select="normalize-space(analysis_value)"/>
                                            </xsl:attribute>
                                        </input>
                                    </td>
                                    <td>
                                        <input type="text" class="form-control form-control-sm"
                                               name="quirk-{$q}-note" id="quirk-{$q}-note">
                                            <xsl:attribute name="value">
                                                <xsl:for-each select="note">
                                                    <xsl:value-of select="normalize-space(.)"/>
                                                    <xsl:if test="position() != last()">; </xsl:if>
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
    </xsl:template>
</xsl:stylesheet>
