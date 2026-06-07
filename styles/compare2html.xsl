<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<xsl:output method="html" indent="yes" encoding="utf-8"/>
<xsl:strip-space elements="*"/>

<!-- ══════════════════════════════════════════════════════════════════════════
     compare2html.xsl  –  Side-by-side diff view for two RE upstream runs.

     Table structure (11 columns — no centre divider):
       [type] [sign|lg|lx|gl|id  A-side] [sign|lg|lx|gl|id  B-side]

     Row types:
       cmp-run-hdr  – sticky thead: blank | A—name | B—name
       cmp-set-hdr  – type label | *pfm_a rcn_a [melid] | *pfm_b rcn_b [melid]
       rfx "both"   – blank | form (colspan=10, shown once)
       rfx "removed"– blank | −  lg  lx  gl  id [red] | blank×5 [grey]
       rfx "added"  – blank | blank×5 [grey]  | + lg  lx  gl  id [green]
     ══════════════════════════════════════════════════════════════════════════ -->

<xsl:template match="/">
  <div><xsl:apply-templates select="compare"/></div>
</xsl:template>


<!-- ══ Root ════════════════════════════════════════════════════════════════ -->
<xsl:template match="compare">

  <!-- Parameters / Statistics / Lexicon stats — side by side -->
  <div style="display:flex; flex-wrap:wrap; gap:1.5rem; align-items:flex-start; margin-bottom:1rem">
    <div><xsl:call-template name="params-table"/></div>
    <div><xsl:call-template name="stats-table"/></div>
    <div style="flex:1 1 auto; min-width:360px"><xsl:call-template name="lex-stats-table"/></div>
  </div>

  <xsl:if test="run[@id='a']/@sets_found = 'false'">
    <p class="text-warning">Sets file not found for Run A (<xsl:value-of select="run[@id='a']/@run_name"/>).</p>
  </xsl:if>
  <xsl:if test="run[@id='b']/@sets_found = 'false'">
    <p class="text-warning">Sets file not found for Run B (<xsl:value-of select="run[@id='b']/@run_name"/>).</p>
  </xsl:if>

  <!-- Summary badges -->
  <p style="margin:.5rem 0 .8rem 0">
    <span class="cmp-badge cmp-same"><xsl:value-of select="summary/@same"/> identical</span>
    <xsl:if test="number(summary/@changed_recon) &gt; 0">
      <span class="cmp-badge cmp-changed"><xsl:value-of select="summary/@changed_recon"/> recon changed</span>
    </xsl:if>
    <xsl:if test="number(summary/@changed_members) &gt; 0">
      <span class="cmp-badge cmp-split"><xsl:value-of select="summary/@changed_members"/> membership diff</span>
    </xsl:if>
    <xsl:if test="number(summary/@unmatched_lost) &gt; 0">
      <span class="cmp-badge cmp-lost"><xsl:value-of select="summary/@unmatched_lost"/> only in A</span>
    </xsl:if>
    <xsl:if test="number(summary/@unmatched_gained) &gt; 0">
      <span class="cmp-badge cmp-gained"><xsl:value-of select="summary/@unmatched_gained"/> only in B</span>
    </xsl:if>
  </p>

  <!-- ═══ One unified diff table ══════════════════════════════════════════ -->
  <xsl:if test="diffs/diff">
    <table class="table table-sm table-bordered cmp-diff-table">
      <colgroup>
        <col class="col-type"/>
        <col class="col-sign"/>
        <col class="col-lg"/>
        <col class="col-lx"/>
        <col class="col-gl"/>
        <col class="col-id"/>
        <col class="col-sign"/>
        <col class="col-lg"/>
        <col class="col-lx"/>
        <col class="col-gl"/>
        <col class="col-id"/>
      </colgroup>
      <thead>
        <tr class="cmp-run-hdr">
          <th/>
          <th colspan="5" class="cmp-a-head">
            A&#160;&#8212;&#160;<xsl:value-of select="@run_name_a"/>
          </th>
          <th colspan="5" class="cmp-b-head">
            B&#160;&#8212;&#160;<xsl:value-of select="@run_name_b"/>
          </th>
        </tr>
      </thead>
      <tbody>

        <xsl:for-each select="diffs[@type='changed_recon']/diff">
          <xsl:call-template name="diff-rows">
            <xsl:with-param name="dtype">recon only</xsl:with-param>
          </xsl:call-template>
        </xsl:for-each>

        <xsl:for-each select="diffs[@type='changed_members']/diff">
          <xsl:call-template name="diff-rows">
            <xsl:with-param name="dtype">support diff</xsl:with-param>
          </xsl:call-template>
        </xsl:for-each>

        <xsl:for-each select="diffs[@type='lost']/diff">
          <xsl:call-template name="diff-rows">
            <xsl:with-param name="dtype">only in A</xsl:with-param>
          </xsl:call-template>
        </xsl:for-each>

        <xsl:for-each select="diffs[@type='gained']/diff">
          <xsl:call-template name="diff-rows">
            <xsl:with-param name="dtype">only in B</xsl:with-param>
          </xsl:call-template>
        </xsl:for-each>

      </tbody>
    </table>
  </xsl:if>

  <xsl:if test="not(diffs/diff)">
    <p class="text-muted" style="font-style:italic">No differences found.</p>
  </xsl:if>

  <p style="font-size:.78rem;color:#aaa;margin-top:1.5rem">
    Comparison created: <xsl:value-of select="@created"/>
  </p>

</xsl:template>


<!-- ══ One set's header row + reflex rows ══════════════════════════════════
     dtype param: "recon changed" | "membership diff" | "only in A" | "only in B"
     Current node: a <diff> element.                                        -->
<xsl:template name="diff-rows">
  <xsl:param name="dtype"/>

  <!-- ── Set-pair header row ── -->
  <tr class="cmp-set-hdr">
    <!-- type label (col 1) — coloured to match the summary badge palette -->
    <td>
      <xsl:attribute name="class">
        <xsl:text>cmp-type-label </xsl:text>
        <xsl:choose>
          <xsl:when test="$dtype = 'recon only'">cmp-type-recon</xsl:when>
          <xsl:when test="$dtype = 'support diff'">cmp-type-diff</xsl:when>
          <xsl:when test="$dtype = 'only in A'">cmp-type-lost</xsl:when>
          <xsl:otherwise>cmp-type-gained</xsl:otherwise>
        </xsl:choose>
      </xsl:attribute>
      <xsl:value-of select="$dtype"/>
    </td>
    <!-- A proto-form (cols 2-6) -->
    <td colspan="5" class="cmp-a-set-hdr">
      <xsl:choose>
        <xsl:when test="pfm_a">
          <strong>*<xsl:value-of select="pfm_a"/></strong>
          <xsl:if test="rcn_a != ''">
            <code style="font-size:.75em;margin-left:.4em"><xsl:value-of select="rcn_a"/></code>
          </xsl:if>
          <xsl:if test="melid != ''">
            <span class="text-muted" style="font-size:.82em;margin-left:.5em">[<xsl:value-of select="melid"/>]</span>
          </xsl:if>
        </xsl:when>
        <xsl:otherwise><span class="text-muted">—</span></xsl:otherwise>
      </xsl:choose>
    </td>
    <!-- B proto-form (cols 7-11) -->
    <td colspan="5" class="cmp-b-set-hdr">
      <xsl:choose>
        <xsl:when test="pfm_b">
          <strong>*<xsl:value-of select="pfm_b"/></strong>
          <xsl:if test="rcn_b != ''">
            <code style="font-size:.75em;margin-left:.4em"><xsl:value-of select="rcn_b"/></code>
          </xsl:if>
          <xsl:if test="melid != ''">
            <span class="text-muted" style="font-size:.82em;margin-left:.5em">[<xsl:value-of select="melid"/>]</span>
          </xsl:if>
        </xsl:when>
        <xsl:otherwise><span class="text-muted">—</span></xsl:otherwise>
      </xsl:choose>
    </td>
  </tr>

  <!-- ── Reflex rows ── -->
  <xsl:for-each select="reflexes/rfx">
    <xsl:choose>

      <!-- "both" — form appears in A and B -->
      <xsl:when test="@status = 'both'">
        <tr>
          <td/>  <!-- type col: blank -->
          <xsl:choose>
            <!-- support diff: show the shared form on BOTH sides so the full
                 A and B support lists are visible side-by-side -->
            <xsl:when test="$dtype = 'support diff'">
              <td/>
              <td style="white-space:nowrap"><xsl:value-of select="@lg"/></td>
              <td><xsl:call-template name="lx-cell"/></td>
              <td class="cmp-gl"><xsl:value-of select="@gl"/></td>
              <td class="cmp-id"><xsl:value-of select="@id"/></td>
              <td/>
              <td style="white-space:nowrap"><xsl:value-of select="@lg"/></td>
              <td><xsl:call-template name="lx-cell"/></td>
              <td class="cmp-gl"><xsl:value-of select="@gl"/></td>
              <td class="cmp-id"><xsl:value-of select="@id"/></td>
            </xsl:when>
            <!-- all other types: form shown once, spanning A+B cols -->
            <xsl:otherwise>
              <td/>
              <td style="white-space:nowrap"><xsl:value-of select="@lg"/></td>
              <td><xsl:call-template name="lx-cell"/></td>
              <td class="cmp-gl"><xsl:value-of select="@gl"/></td>
              <td class="cmp-id"><xsl:value-of select="@id"/></td>
              <td/><td/><td/><td/><td/>
            </xsl:otherwise>
          </xsl:choose>
        </tr>
      </xsl:when>

      <!-- "removed" — A only: A side red, B side blank/grey -->
      <xsl:when test="@status = 'removed'">
        <tr>
          <td/>
          <td class="diff-sign diff-a-removed">−</td>
          <td class="diff-a-removed" style="white-space:nowrap"><xsl:value-of select="@lg"/></td>
          <td class="diff-a-removed"><xsl:call-template name="lx-cell"/></td>
          <td class="diff-a-removed cmp-gl"><xsl:value-of select="@gl"/></td>
          <td class="diff-a-removed cmp-id"><xsl:value-of select="@id"/></td>
          <td class="diff-blank"/><td class="diff-blank"/><td class="diff-blank"/>
          <td class="diff-blank"/><td class="diff-blank"/>
        </tr>
      </xsl:when>

      <!-- "added" — B only: A side blank/grey, B side green -->
      <xsl:when test="@status = 'added'">
        <tr>
          <td/>
          <td class="diff-blank"/><td class="diff-blank"/><td class="diff-blank"/>
          <td class="diff-blank"/><td class="diff-blank"/>
          <td class="diff-sign diff-b-added">+</td>
          <td class="diff-b-added" style="white-space:nowrap"><xsl:value-of select="@lg"/></td>
          <td class="diff-b-added"><xsl:call-template name="lx-cell"/></td>
          <td class="diff-b-added cmp-gl"><xsl:value-of select="@gl"/></td>
          <td class="diff-b-added cmp-id"><xsl:value-of select="@id"/></td>
        </tr>
      </xsl:when>

    </xsl:choose>
  </xsl:for-each>

</xsl:template>


<!-- ══ Render lx (with optional lxf annotation) ════════════════════════════ -->
<xsl:template name="lx-cell">
  <xsl:choose>
    <xsl:when test="@lxf != ''">
      <xsl:value-of select="@lxf"/>
      <small style="color:#888"> &#171;&#171; <xsl:value-of select="@lx"/></small>
    </xsl:when>
    <xsl:otherwise>
      <xsl:value-of select="@lx"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>


<!-- ══ Parameters table ════════════════════════════════════════════════════ -->
<xsl:template name="params-table">
  <h5>Parameters</h5>
  <table class="table table-sm table-bordered cmp-table">
    <thead>
      <tr>
        <th>Param</th>
        <th>Run A <small class="text-muted">&#160;<xsl:value-of select="/compare/@run_name_a"/></small></th>
        <th>Run B <small class="text-muted">&#160;<xsl:value-of select="/compare/@run_name_b"/></small></th>
      </tr>
    </thead>
    <tbody>
      <xsl:for-each select="/compare/run[@id='a']/param">
        <xsl:variable name="k"  select="@key"/>
        <xsl:variable name="va" select="@value"/>
        <xsl:variable name="vb" select="/compare/run[@id='b']/param[@key=$k]/@value"/>
        <tr>
          <xsl:if test="$va != $vb">
            <xsl:attribute name="class">table-warning</xsl:attribute>
          </xsl:if>
          <td><xsl:call-template name="param-label"><xsl:with-param name="key" select="$k"/></xsl:call-template></td>
          <td><xsl:choose><xsl:when test="$va = ''">—</xsl:when><xsl:otherwise><xsl:value-of select="$va"/></xsl:otherwise></xsl:choose></td>
          <td><xsl:choose><xsl:when test="$vb = ''">—</xsl:when><xsl:otherwise><xsl:value-of select="$vb"/></xsl:otherwise></xsl:choose></td>
        </tr>
      </xsl:for-each>
    </tbody>
  </table>
</xsl:template>


<!-- ══ Statistics table ════════════════════════════════════════════════════ -->
<xsl:template name="stats-table">
  <h5>Statistics</h5>
  <table class="table table-sm table-bordered cmp-table">
    <thead><tr><th>Stat</th><th>Run A</th><th>Run B</th><th>&#916;</th></tr></thead>
    <tbody>
      <xsl:for-each select="/compare/run[@id='a']/stat">
        <xsl:variable name="k"     select="@key"/>
        <xsl:variable name="va"    select="number(@value)"/>
        <xsl:variable name="vb"    select="number(/compare/run[@id='b']/stat[@key=$k]/@value)"/>
        <xsl:variable name="delta" select="$vb - $va"/>
        <tr>
          <td><xsl:call-template name="stat-label"><xsl:with-param name="key" select="$k"/></xsl:call-template></td>
          <td><xsl:value-of select="@value"/></td>
          <td><xsl:value-of select="/compare/run[@id='b']/stat[@key=$k]/@value"/></td>
          <td>
            <xsl:attribute name="class">
              <xsl:choose>
                <xsl:when test="$delta &gt; 0">text-success</xsl:when>
                <xsl:when test="$delta &lt; 0">text-danger</xsl:when>
                <xsl:otherwise>text-muted</xsl:otherwise>
              </xsl:choose>
            </xsl:attribute>
            <xsl:choose>
              <xsl:when test="$delta &gt; 0">+<xsl:value-of select="$delta"/></xsl:when>
              <xsl:otherwise><xsl:value-of select="$delta"/></xsl:otherwise>
            </xsl:choose>
          </td>
        </tr>
      </xsl:for-each>
    </tbody>
  </table>
</xsl:template>


<!-- ══ Lexicon statistics table ════════════════════════════════════════════ -->
<xsl:template name="lex-stats-table">
  <xsl:if test="/compare/lexicon_stats/lang">
    <h5>Lexicon statistics</h5>
    <table class="table table-sm table-striped table-bordered table-hover sortable cmp-table">
      <thead>
        <tr>
          <th>Language</th>
          <th>Rfx (A)</th><th>Isol (A)</th><th>Fail (A)</th>
          <th>Rfx (B)</th><th>Isol (B)</th><th>Fail (B)</th>
        </tr>
      </thead>
      <tbody>
        <xsl:for-each select="/compare/lexicon_stats/lang">
          <xsl:sort select="@name"/>
          <tr>
            <td><xsl:value-of select="@name"/></td>
            <td><xsl:value-of select="rfx_a"/></td>
            <td>
              <xsl:if test="number(iso_a) &gt; 0"><xsl:attribute name="class">text-warning</xsl:attribute></xsl:if>
              <xsl:value-of select="iso_a"/>
            </td>
            <td>
              <xsl:if test="number(fail_a) &gt; 0"><xsl:attribute name="class">text-danger</xsl:attribute></xsl:if>
              <xsl:value-of select="fail_a"/>
            </td>
            <td><xsl:value-of select="rfx_b"/></td>
            <td>
              <xsl:if test="number(iso_b) &gt; 0"><xsl:attribute name="class">text-warning</xsl:attribute></xsl:if>
              <xsl:value-of select="iso_b"/>
            </td>
            <td>
              <xsl:if test="number(fail_b) &gt; 0"><xsl:attribute name="class">text-danger</xsl:attribute></xsl:if>
              <xsl:value-of select="fail_b"/>
            </td>
          </tr>
        </xsl:for-each>
      </tbody>
    </table>
  </xsl:if>
</xsl:template>


<!-- ══ Helpers ════════════════════════════════════════════════════════════ -->
<xsl:template name="param-label">
  <xsl:param name="key"/>
  <xsl:choose>
    <xsl:when test="$key = 'recon'">Recon</xsl:when>
    <xsl:when test="$key = 'mel'">MEL</xsl:when>
    <xsl:when test="$key = 'fuzzy'">Fuzzy</xsl:when>
    <xsl:when test="$key = 'upstream'">Upstream</xsl:when>
    <xsl:when test="$key = 'context_match_type'">Context match</xsl:when>
    <xsl:when test="$key = 'spec'">Supra-segmentals</xsl:when>
    <xsl:otherwise><xsl:value-of select="$key"/></xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template name="stat-label">
  <xsl:param name="key"/>
  <xsl:choose>
    <xsl:when test="$key = 'sets'">Sets</xsl:when>
    <xsl:when test="$key = 'reflexes'">Reflexes</xsl:when>
    <xsl:when test="$key = 'isolates'">Isolates</xsl:when>
    <xsl:when test="$key = 'failures'">Failures</xsl:when>
    <xsl:otherwise><xsl:value-of select="$key"/></xsl:otherwise>
  </xsl:choose>
</xsl:template>

</xsl:stylesheet>
