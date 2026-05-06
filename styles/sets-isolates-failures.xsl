<?xml version="1.0" encoding="utf-8"?>
<!--
  sets-isolates-failures.xsl
  Shared templates for the Isolates and Failures sections of a cognate-sets
  XML document.  Included (xsl:include) by sets2html.xsl and sets2tabular.xsl
  so both panes render these sections identically.
-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:template match="isolates">
    <a name="isolates"/>
    <style>
      .iso-badge { display:inline-block; padding:1px 5px; border-radius:3px;
                   font-size:0.78em; margin:1px 2px; white-space:nowrap; }
      .iso-no-mel { background:#fff3cd; color:#856404; }
      .iso-no-set { background:#e2e3e5; color:#383d41; }
      .iso-in-set { background:#cce5ff; color:#004085; }
      .iso-mel    { background:#d4edda; color:#155724; }
      .iso-excl   { background:#f8d7da; color:#721c24; }
    </style>
    <h5>Isolates
      <small class="text-muted" style="font-size:0.8em; font-weight:normal;">
        n = <xsl:value-of select="count(rfx)"/>
      </small>
    </h5>
    <table class="table table-sm table-striped table-hover table-bordered sortable">
      <thead>
        <tr>
          <th class="col-plg">lg</th>
          <th class="col-pfm">lx</th>
          <th class="col-gloss">gl</th>
          <th class="col-pfm">pfm</th>
          <th class="col-rcn">rcn</th>
          <th class="col-plg">id</th>
          <th class="col-gloss">Reasons</th>
        </tr>
      </thead>
      <tbody>
        <xsl:for-each select="rfx">
          <tr>
            <td class="col-plg"><xsl:value-of select="lg"/></td>
            <td class="col-pfm">
              <xsl:choose>
                <xsl:when test="lxf">
                  <xsl:value-of select="lxf"/>
                  <small style="color:#888;"> &lt;&lt; <xsl:value-of select="lx"/></small>
                </xsl:when>
                <xsl:otherwise><xsl:value-of select="lx"/></xsl:otherwise>
              </xsl:choose>
            </td>
            <td class="col-gloss"><xsl:value-of select="gl"/></td>
            <!-- pfm: show first reconstruction; extras listed in hover title -->
            <td class="col-pfm">
              <xsl:if test="count(recon) > 1">
                <xsl:attribute name="title">
                  <xsl:for-each select="recon[position() > 1]">
                    <xsl:value-of select="pfm"/>
                    <xsl:text> [</xsl:text><xsl:value-of select="rcn"/><xsl:text>]</xsl:text>
                    <xsl:if test="position() != last()"><xsl:text>; </xsl:text></xsl:if>
                  </xsl:for-each>
                </xsl:attribute>
              </xsl:if>
              <div class="pfm"><xsl:value-of select="recon[1]/pfm"/></div>
              <xsl:if test="count(recon) > 1">
                <small style="color:#888;cursor:help;">(+<xsl:value-of select="count(recon)-1"/> more)</small>
              </xsl:if>
            </td>
            <!-- rcn: show first reconstruction; extras listed in hover title -->
            <td class="col-rcn">
              <xsl:if test="count(recon) > 1">
                <xsl:attribute name="title">
                  <xsl:for-each select="recon[position() > 1]">
                    <xsl:value-of select="pfm"/>
                    <xsl:text> [</xsl:text><xsl:value-of select="rcn"/><xsl:text>]</xsl:text>
                    <xsl:if test="position() != last()"><xsl:text>; </xsl:text></xsl:if>
                  </xsl:for-each>
                </xsl:attribute>
              </xsl:if>
              <div class="rcn"><xsl:value-of select="recon[1]/rcn"/></div>
              <xsl:if test="count(recon) > 1">
                <small style="color:#888;cursor:help;">(+<xsl:value-of select="count(recon)-1"/> more)</small>
              </xsl:if>
            </td>
            <td class="col-plg"><xsl:value-of select="@id"/></td>
            <td class="col-gloss">
              <!-- No matching MEL -->
              <xsl:if test="not(matched_mel)">
                <span class="iso-badge iso-no-mel">No matching MEL</span>
              </xsl:if>
              <!-- No matching set -->
              <xsl:if test="not(in_set)">
                <span class="iso-badge iso-no-set">No matching set</span>
              </xsl:if>
              <!-- Found in set(s): one badge per set, hover shows pfm/rcn/mel summary -->
              <xsl:for-each select="in_set">
                <span class="iso-badge iso-in-set"
                      title="{@pfm} [{@rcn}] {@melid}: {@mel}">Set&#160;<xsl:value-of select="@num"/></span>
              </xsl:for-each>
              <!-- Matched MEL(s): one badge per MEL, hover shows all glosses -->
              <xsl:for-each select="matched_mel">
                <span class="iso-badge iso-mel"
                      title="{@glosses}"><xsl:value-of select="@id"/>:&#160;<xsl:value-of select="substring-before(concat(@glosses, ','), ',')"/></span>
              </xsl:for-each>
              <!-- Excluded by semantics: in a real set AND matched a MEL, yet still isolated -->
              <xsl:if test="in_set and matched_mel">
                <span class="iso-badge iso-excl">Excluded by semantics</span>
              </xsl:if>
            </td>
          </tr>
        </xsl:for-each>
      </tbody>
    </table>
  </xsl:template>

  <xsl:template match="failures">
    <a name="failures"/>
    <h5>Failures
      <small class="text-muted" style="font-size:0.8em; font-weight:normal;">
        n = <xsl:value-of select="count(rfx)"/>
      </small>
    </h5>
    <table class="table table-sm table-striped table-hover table-bordered sortable">
      <thead>
        <tr>
          <th class="col-plg">lg</th>
          <th class="col-pfm">lx</th>
          <th class="col-gloss">gl</th>
          <th class="col-plg">id</th>
        </tr>
      </thead>
      <tbody>
        <xsl:for-each select="rfx">
          <tr>
            <td class="col-plg"><xsl:value-of select="lg"/></td>
            <td class="col-pfm">
              <xsl:choose>
                <xsl:when test="lxf">
                  <xsl:value-of select="lxf"/>
                  <small style="color:#888;"> &lt;&lt; <xsl:value-of select="lx"/></small>
                </xsl:when>
                <xsl:otherwise><xsl:value-of select="lx"/></xsl:otherwise>
              </xsl:choose>
            </td>
            <td class="col-gloss"><xsl:value-of select="gl"/></td>
            <td class="col-plg"><xsl:value-of select="@id"/></td>
          </tr>
        </xsl:for-each>
      </tbody>
    </table>
  </xsl:template>

</xsl:stylesheet>
