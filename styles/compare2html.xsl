<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<xsl:output method="html" indent="yes" encoding="utf-8"/>
<xsl:strip-space elements="*"/>

<!-- ══════════════════════════════════════════════════════════════════════════
     compare2html.xsl  –  Render a <compare> XML document as HTML.

     Input schema (run_compare.py → build_compare_xml):

       <compare project="TGTM" created="…" run_name_a="…" run_name_b="…">
         <run id="a|b" run_id="…" run_name="…" sets_found="true|false">
           <param key="recon|mel|fuzzy|upstream" value="…"/>
           <stat  key="sets|isolates|failures"   value="…"/>
         </run>
         <summary same="N" changed="N" lost="N" gained="N"/>
         <changed>
           <set>
             <melid/> <pfm_a/> <rcn_a/> <pfm_b/> <rcn_b/>
             <languages><lg/>…</languages>
             <members><m/>…</members>
           </set>…
         </changed>
         <lost>    <set><melid/><pfm/><rcn/><languages>…</languages><members>…</members></set>… </lost>
         <gained>  <set>…</set>… </gained>
       </compare>
     ══════════════════════════════════════════════════════════════════════════ -->

<xsl:template match="/">
  <div>
      <xsl:apply-templates select="compare"/>
  </div>
</xsl:template>


<!-- ══ Root: dispatch sections ════════════════════════════════════════════ -->
<xsl:template match="compare">

  <!-- ── Parameters & Statistics ── -->
  <xsl:call-template name="params-table"/>
  <xsl:call-template name="stats-table"/>
  <xsl:call-template name="lex-stats-table"/>

  <!-- ── Missing sets-file warnings ── -->
  <xsl:if test="run[@id='a']/@sets_found = 'false'">
    <p class="text-warning">
      <i class="fas fa-exclamation-triangle mr-1"/>
      Sets file not found for Run A (<xsl:value-of select="run[@id='a']/@run_name"/>).
    </p>
  </xsl:if>
  <xsl:if test="run[@id='b']/@sets_found = 'false'">
    <p class="text-warning">
      <i class="fas fa-exclamation-triangle mr-1"/>
      Sets file not found for Run B (<xsl:value-of select="run[@id='b']/@run_name"/>).
    </p>
  </xsl:if>

  <!-- ── Summary badges ── -->
  <p style="margin: .8rem 0 1rem 0;">
    <span class="cmp-badge cmp-same">
      <xsl:value-of select="summary/@same"/> identical
    </span>
    <span class="cmp-badge cmp-changed">
      <xsl:value-of select="summary/@changed"/> changed
    </span>
    <span class="cmp-badge cmp-lost">
      <xsl:value-of select="summary/@lost"/> lost
    </span>
    <span class="cmp-badge cmp-gained">
      <xsl:value-of select="summary/@gained"/> gained
    </span>
  </p>

  <!-- ── Changed reconstruction ── -->
  <xsl:if test="changed/set">
    <h5 style="margin-top:1.2rem">
      Changed reconstruction
      <small class="text-muted" style="font-size:.8em; font-weight:normal">
        n = <xsl:value-of select="count(changed/set)"/>
      </small>
    </h5>
    <table class="table table-sm table-striped table-bordered table-hover sortable cmp-table">
      <thead>
        <tr>
          <th>pfm (A)</th><th>MEL id</th><th>rcn (A)</th>
          <th>pfm (B)</th><th>rcn (B)</th><th>languages</th>
        </tr>
      </thead>
      <tbody>
        <xsl:for-each select="changed/set">
          <xsl:call-template name="changed-row"/>
        </xsl:for-each>
      </tbody>
    </table>
  </xsl:if>

  <!-- ── Lost sets ── -->
  <xsl:if test="lost/set">
    <h5 style="margin-top:1.2rem">
      Lost sets
      <small class="text-muted" style="font-size:.8em; font-weight:normal">
        in A only, n = <xsl:value-of select="count(lost/set)"/>
      </small>
    </h5>
    <table class="table table-sm table-striped table-bordered table-hover sortable cmp-table">
      <thead>
        <tr><th>pfm</th><th>MEL id</th><th>rcn</th><th>languages</th></tr>
      </thead>
      <tbody>
        <xsl:for-each select="lost/set">
          <xsl:call-template name="single-row"/>
        </xsl:for-each>
      </tbody>
    </table>
  </xsl:if>

  <!-- ── Gained sets ── -->
  <xsl:if test="gained/set">
    <h5 style="margin-top:1.2rem">
      Gained sets
      <small class="text-muted" style="font-size:.8em; font-weight:normal">
        in B only, n = <xsl:value-of select="count(gained/set)"/>
      </small>
    </h5>
    <table class="table table-sm table-striped table-bordered table-hover sortable cmp-table">
      <thead>
        <tr><th>pfm</th><th>MEL id</th><th>rcn</th><th>languages</th></tr>
      </thead>
      <tbody>
        <xsl:for-each select="gained/set">
          <xsl:call-template name="single-row"/>
        </xsl:for-each>
      </tbody>
    </table>
  </xsl:if>

  <!-- ── No differences ── -->
  <xsl:if test="not(changed/set) and not(lost/set) and not(gained/set)
                and run[@id='a']/@sets_found = 'true'
                and run[@id='b']/@sets_found = 'true'">
    <p class="text-muted" style="font-style:italic">No differences found.</p>
  </xsl:if>

  <!-- ── Timestamp ── -->
  <p style="font-size:0.78rem; color:#aaa; margin-top:1.5rem;">
    Comparison created: <xsl:value-of select="@created"/>
  </p>

</xsl:template>


<!-- ══ Parameters table ════════════════════════════════════════════════════ -->
<xsl:template name="params-table">
  <h5>Parameters</h5>
  <table class="table table-sm table-bordered cmp-table" style="max-width:680px">
    <thead>
      <tr>
        <th>Param</th>
        <th>
          Run A
          <small class="text-muted">&#160;<xsl:value-of select="/compare/@run_name_a"/></small>
        </th>
        <th>
          Run B
          <small class="text-muted">&#160;<xsl:value-of select="/compare/@run_name_b"/></small>
        </th>
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
          <td><xsl:choose>
            <xsl:when test="$va = ''">—</xsl:when>
            <xsl:otherwise><xsl:value-of select="$va"/></xsl:otherwise>
          </xsl:choose></td>
          <td><xsl:choose>
            <xsl:when test="$vb = ''">—</xsl:when>
            <xsl:otherwise><xsl:value-of select="$vb"/></xsl:otherwise>
          </xsl:choose></td>
        </tr>
      </xsl:for-each>
    </tbody>
  </table>
</xsl:template>


<!-- ══ Statistics table ════════════════════════════════════════════════════ -->
<xsl:template name="stats-table">
  <h5>Statistics</h5>
  <table class="table table-sm table-bordered cmp-table" style="max-width:480px">
    <thead>
      <tr><th>Stat</th><th>Run A</th><th>Run B</th><th>&#916;</th></tr>
    </thead>
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


<!-- ══ Row for a changed set ═══════════════════════════════════════════════ -->
<xsl:template name="changed-row">
  <tr>
    <!-- pfm (A) — highlight if pfm changed -->
    <td>
      <xsl:if test="pfm_a != pfm_b">
        <xsl:attribute name="class">cmp-pfm-diff</xsl:attribute>
      </xsl:if>
      <xsl:value-of select="pfm_a"/>
    </td>
    <!-- MEL id -->
    <td style="white-space:nowrap"><xsl:value-of select="melid"/></td>
    <!-- rcn (A) -->
    <td><xsl:value-of select="rcn_a"/></td>
    <!-- pfm (B) — highlight if pfm changed -->
    <td>
      <xsl:if test="pfm_a != pfm_b">
        <xsl:attribute name="class">cmp-pfm-diff</xsl:attribute>
      </xsl:if>
      <xsl:value-of select="pfm_b"/>
    </td>
    <!-- rcn (B) -->
    <td><xsl:value-of select="rcn_b"/></td>
    <!-- languages -->
    <td class="cmp-lgs">
      <xsl:for-each select="languages/lg">
        <xsl:value-of select="."/>
        <xsl:if test="position() != last()">, </xsl:if>
      </xsl:for-each>
    </td>
  </tr>
</xsl:template>


<!-- ══ Row for a lost or gained set ════════════════════════════════════════ -->
<xsl:template name="single-row">
  <tr>
    <td><xsl:value-of select="pfm"/></td>
    <td style="white-space:nowrap"><xsl:value-of select="melid"/></td>
    <td><xsl:value-of select="rcn"/></td>
    <td class="cmp-lgs">
      <xsl:for-each select="languages/lg">
        <xsl:value-of select="."/>
        <xsl:if test="position() != last()">, </xsl:if>
      </xsl:for-each>
    </td>
  </tr>
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
          <xsl:variable name="rfx_a"  select="number(rfx_a)"/>
          <xsl:variable name="rfx_b"  select="number(rfx_b)"/>
          <xsl:variable name="iso_a"  select="number(iso_a)"/>
          <xsl:variable name="iso_b"  select="number(iso_b)"/>
          <xsl:variable name="fail_a" select="number(fail_a)"/>
          <xsl:variable name="fail_b" select="number(fail_b)"/>
          <tr>
            <td><xsl:value-of select="@name"/></td>
            <!-- Rfx (A) -->
            <td><xsl:value-of select="rfx_a"/></td>
            <!-- Isol (A) -->
            <td>
              <xsl:if test="$iso_a &gt; 0">
                <xsl:attribute name="class">text-warning</xsl:attribute>
              </xsl:if>
              <xsl:value-of select="iso_a"/>
            </td>
            <!-- Fail (A) -->
            <td>
              <xsl:if test="$fail_a &gt; 0">
                <xsl:attribute name="class">text-danger</xsl:attribute>
              </xsl:if>
              <xsl:value-of select="fail_a"/>
            </td>
            <!-- Rfx (B) -->
            <td><xsl:value-of select="rfx_b"/></td>
            <!-- Isol (B) -->
            <td>
              <xsl:if test="$iso_b &gt; 0">
                <xsl:attribute name="class">text-warning</xsl:attribute>
              </xsl:if>
              <xsl:value-of select="iso_b"/>
            </td>
            <!-- Fail (B) -->
            <td>
              <xsl:if test="$fail_b &gt; 0">
                <xsl:attribute name="class">text-danger</xsl:attribute>
              </xsl:if>
              <xsl:value-of select="fail_b"/>
            </td>
          </tr>
        </xsl:for-each>
      </tbody>
    </table>
  </xsl:if>
</xsl:template>


<!-- ══ Helpers: human-readable labels ══════════════════════════════════════ -->
<xsl:template name="param-label">
  <xsl:param name="key"/>
  <xsl:choose>
    <xsl:when test="$key = 'recon'">Recon</xsl:when>
    <xsl:when test="$key = 'mel'">MEL</xsl:when>
    <xsl:when test="$key = 'fuzzy'">Fuzzy</xsl:when>
    <xsl:when test="$key = 'upstream'">Upstream</xsl:when>
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
