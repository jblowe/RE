<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<xsl:output method="html" indent="yes" encoding="utf-8"/>
<xsl:strip-space elements="*"/>

<xsl:template match="/">
  <html>
    <head><title>Coverage</title></head>
    <body>
      <!-- Style block in body — head is stripped by xml_to_html(). -->
      <style>
        .cov-table td, .cov-table th { padding: .15rem .3rem !important; font-size: 0.8rem; }
        .cov-unused { background: #fff3cd; padding: 1px 3px; border-radius: 2px; }
        .cov-uses   { color: #888; font-size: 0.75em; }
      </style>
      <xsl:variable name="mel_fn" select="stats/settings/parm[@key='mel_filename']/@value"/>
      <xsl:if test="$mel_fn != ''">
        <!-- Extract basename: take text after the last '/' or '\' -->
        <xsl:variable name="mel_base">
          <xsl:call-template name="basename">
            <xsl:with-param name="path" select="$mel_fn"/>
          </xsl:call-template>
        </xsl:variable>
        <p style="font-size:0.85rem; font-weight:600; margin-bottom:.2rem;">
          <xsl:value-of select="$mel_base"/>
        </p>
      </xsl:if>
      <p style="font-style:italic; font-size:0.8rem; margin-bottom:.5rem;">
        created at: <xsl:value-of select=".//createdat"/>
      </p>
      <xsl:apply-templates select="stats/lexicons"/>
      <xsl:apply-templates select="stats/totals"/>
      <xsl:apply-templates select="stats/semantics"/>
      <xsl:apply-templates select="stats/unmatched_glosses"/>
    </body>
  </html>
</xsl:template>

<!-- ── Utility: extract basename from a file path ───────────────────────── -->
<xsl:template name="basename">
  <xsl:param name="path"/>
  <xsl:choose>
    <xsl:when test="contains($path, '/') or contains($path, '\')">
      <xsl:variable name="after-slash">
        <xsl:choose>
          <xsl:when test="contains($path, '/')">
            <xsl:call-template name="basename">
              <xsl:with-param name="path" select="substring-after($path, '/')"/>
            </xsl:call-template>
          </xsl:when>
          <xsl:otherwise>
            <xsl:call-template name="basename">
              <xsl:with-param name="path" select="substring-after($path, '\')"/>
            </xsl:call-template>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:variable>
      <xsl:value-of select="$after-slash"/>
    </xsl:when>
    <xsl:otherwise><xsl:value-of select="$path"/></xsl:otherwise>
  </xsl:choose>
</xsl:template>

<!-- ── Per-language coverage table ──────────────────────────────────────── -->
<xsl:template match="lexicons">
  <h5>Coverage by language</h5>
  <table class="table table-sm table-hover table-bordered sortable cov-table">
    <thead>
      <tr>
        <th>language</th>
        <!-- derive column headers dynamically from first lexicon's children -->
        <xsl:for-each select="lexicon[1]/*">
          <th><xsl:value-of select="name()"/></th>
        </xsl:for-each>
      </tr>
    </thead>
    <tbody>
      <xsl:for-each select="lexicon">
        <tr>
          <td><xsl:value-of select="@language"/></td>
          <xsl:for-each select="./*">
            <td><xsl:value-of select="@value"/></td>
          </xsl:for-each>
        </tr>
      </xsl:for-each>
    </tbody>
  </table>
</xsl:template>

<!-- ── Summary totals ───────────────────────────────────────────────────── -->
<xsl:template match="totals">
  <h5>Summary</h5>
  <table class="table table-sm table-bordered cov-table">
    <thead>
      <tr><th>Stat</th><th>Value</th></tr>
    </thead>
    <tbody>
      <xsl:for-each select="./*">
        <tr>
          <td><xsl:value-of select="name()"/></td>
          <td><xsl:value-of select="@value"/></td>
        </tr>
      </xsl:for-each>
    </tbody>
  </table>
</xsl:template>

<!-- ── MEL usage (semantics section) ────────────────────────────────────── -->
<xsl:template match="semantics">
  <h5>MEL usage
    <small class="text-muted" style="font-size:0.8em; font-weight:normal;">
      &#160;
      <span class="cov-unused" style="padding:1px 6px;">unused glosses</span>
      &#160; usage count in subscript
    </small>
  </h5>
  <table class="table table-sm table-hover table-bordered sortable cov-table">
    <thead>
      <tr>
        <th>MEL id</th>
        <th>Glosses</th>
      </tr>
    </thead>
    <tbody>
      <xsl:for-each select="mel">
        <tr>
          <td style="vertical-align:top; white-space:nowrap">
            <xsl:value-of select="@id"/>
          </td>
          <td class="col-gloss">
            <xsl:for-each select="gl">
              <xsl:choose>
                <xsl:when test="@uses = '0'">
                  <span class="cov-unused"><xsl:value-of select="."/></span>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="."/>
                  <sub class="cov-uses">&#160;<xsl:value-of select="@uses"/></sub>
                </xsl:otherwise>
              </xsl:choose>
              <xsl:if test="position() != last()"><xsl:text>; </xsl:text></xsl:if>
            </xsl:for-each>
          </td>
        </tr>
      </xsl:for-each>
    </tbody>
  </table>
</xsl:template>

<!-- ── Unmatched glosses ─────────────────────────────────────────────────── -->
<xsl:template match="unmatched_glosses">
  <h5>Unmatched glosses
    <small class="text-muted" style="font-size:0.8em; font-weight:normal;">
      n = <xsl:value-of select="count(.//gl)"/>
    </small>
  </h5>
  <p style="font-size:0.85rem; line-height:1.8;">
    <xsl:for-each select=".//gl">
      <xsl:value-of select="."/>
      <xsl:if test="position() != last()"><xsl:text>, </xsl:text></xsl:if>
    </xsl:for-each>
  </p>
</xsl:template>

</xsl:stylesheet>
