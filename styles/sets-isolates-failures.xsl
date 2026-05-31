<?xml version="1.0" encoding="utf-8"?>
<!--
  sets-isolates-failures.xsl
  Shared templates for the Isolates and Failures sections of a cognate-sets
  XML document.  Included (xsl:include) by sets2html.xsl and sets2tabular.xsl
  so both panes render these sections identically.
-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <!--
    linkify-rcn: split a space-separated rcn string into individual
    <a class="rcn-link"> elements so each correspondence ID is clickable.
    Shared by sets2tabular.xsl and sets2html.xsl via xsl:include.
  -->
  <!--
    sets-stats-toolbar: renders the n-sets / isolates / failures button bar
    that appears at the top of every Sets view (both paragraph and tabular).
    Defined here so sets2html.xsl and sets2tabular.xsl share one copy.
    Buttons carry data-target (named anchor to scroll to) and data-count
    (bare integer) so JavaScript can wire up scrollIntoView without parsing
    text content, and extract counts for the Research panel header.
  -->
  <xsl:template name="sets-stats-toolbar">
    <xsl:param name="n-sets"/>
    <xsl:param name="n-isolates"/>
    <xsl:param name="n-failures"/>
    <xsl:param name="createdat"/>
    <div class="tab-toolbar">
      <button class="btn btn-sm btn-outline-secondary sets-nav-btn"
              data-target="sets-top" data-count="{$n-sets}"><xsl:value-of select="$n-sets"/><xsl:text> sets</xsl:text></button>
      <button class="btn btn-sm btn-outline-secondary sets-nav-btn"
              data-target="isolates" data-count="{$n-isolates}"><xsl:value-of select="$n-isolates"/><xsl:text> isolates</xsl:text></button>
      <button class="btn btn-sm btn-outline-secondary sets-nav-btn"
              data-target="failures" data-count="{$n-failures}"><xsl:value-of select="$n-failures"/><xsl:text> failures</xsl:text></button>
      <span class="text-muted" style="font-size:0.85em; margin-left:.5rem;">created at: <xsl:value-of select="$createdat"/></span>
    </div>
  </xsl:template>

  <xsl:template name="linkify-rcn">
    <xsl:param name="text"/>
    <xsl:variable name="t" select="normalize-space($text)"/>
    <xsl:choose>
      <xsl:when test="contains($t, ' ')">
        <xsl:variable name="token" select="substring-before($t, ' ')"/>
        <a class="rcn-link" href="#" data-corr-id="{$token}"><xsl:value-of select="$token"/></a>
        <xsl:text> </xsl:text>
        <xsl:call-template name="linkify-rcn">
          <xsl:with-param name="text" select="normalize-space(substring-after($t, ' '))"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:when test="$t != ''">
        <a class="rcn-link" href="#" data-corr-id="{$t}"><xsl:value-of select="$t"/></a>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="isolates">
    <a name="isolates"/>
    <style>
      .iso-badge { display:inline-block; padding:1px 5px; border-radius:3px;
                   font-size:0.78em; margin:1px 2px; white-space:nowrap; }
      .iso-no-mel      { background:#fff3cd; color:#856404; }
      .iso-no-set      { background:#e2e3e5; color:#383d41; }
      .iso-in-set      { background:#cce5ff; color:#004085; }
      .iso-mel         { background:#d4edda; color:#155724; }
      .iso-excl        { background:#f8d7da; color:#721c24; }
      .iso-fail-reason { display:block; margin-bottom:2px; white-space:normal; }
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
              <div class="rcn"><xsl:call-template name="linkify-rcn"><xsl:with-param name="text" select="recon[1]/rcn"/></xsl:call-template></div>
              <xsl:if test="count(recon) > 1">
                <small style="color:#888;cursor:help;">(+<xsl:value-of select="count(recon)-1"/> more)</small>
              </xsl:if>
            </td>
            <td class="col-plg">
              <span class="rfx-interactive-link"
                    data-lang="{lg}"
                    data-reflex="{lx}"
                    data-gloss="{gl}"
                    title="Load in Interactive tab">
                <xsl:value-of select="@id"/>
              </span>
            </td>
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
            <td class="col-plg">
              <span class="rfx-interactive-link"
                    data-lang="{lg}"
                    data-reflex="{lx}"
                    data-gloss="{gl}"
                    title="Load in Interactive tab">
                <xsl:value-of select="@id"/>
              </span>
            </td>
            <td class="col-gloss">
              <xsl:for-each select="reasons/reason">
                <span>
                  <xsl:attribute name="class"><xsl:text>iso-badge iso-fail-reason </xsl:text><xsl:choose>
                    <xsl:when test="starts-with(., 'Syllable canon:')">fail-syllable-canon</xsl:when>
                    <xsl:when test="starts-with(., 'Syllable structure')">fail-syllable-final</xsl:when>
                    <xsl:when test="contains(., 'unmet at word-final')">fail-word-final</xsl:when>
                    <xsl:when test="contains(., 'Panini')">fail-panini</xsl:when>
                    <xsl:when test="starts-with(., 'left context') or starts-with(., 'right context')">fail-context</xsl:when>
                    <xsl:when test="starts-with(., 'Constituent ')">fail-constituent</xsl:when>
                    <xsl:when test="starts-with(., '…') or starts-with(., '...')">fail-more</xsl:when>
                    <xsl:otherwise>fail-constituent</xsl:otherwise>
                  </xsl:choose></xsl:attribute>
                  <xsl:value-of select="."/>
                </span>
              </xsl:for-each>
              <xsl:if test="not(reasons/reason)">
                <span class="text-muted" style="font-size:0.85em;">—</span>
              </xsl:if>
            </td>
          </tr>
        </xsl:for-each>
      </tbody>
    </table>
  </xsl:template>

</xsl:stylesheet>
