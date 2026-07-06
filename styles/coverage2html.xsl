<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<xsl:output method="html" indent="yes" encoding="utf-8"/>
<xsl:strip-space elements="*"/>

<xsl:template match="/">
  <div>
    <!-- MEL filename: settings/parm (coverage docs) or @basedon (mel_lexicon docs) -->
    <xsl:variable name="mel_fn_settings"
                  select="mel_analysis/settings/parm[@key='mel_filename']/@value"/>
    <xsl:variable name="mel_fn_basedon" select="mel_analysis/@basedon"/>
    <xsl:choose>
      <xsl:when test="$mel_fn_settings != ''">
        <xsl:variable name="mel_base">
          <xsl:call-template name="basename">
            <xsl:with-param name="path" select="$mel_fn_settings"/>
          </xsl:call-template>
        </xsl:variable>
        <p style="font-size:0.85rem; font-weight:600; margin-bottom:.2rem;">
          <xsl:value-of select="$mel_base"/>
        </p>
      </xsl:when>
      <xsl:when test="$mel_fn_basedon != ''">
        <p style="font-size:0.85rem; font-weight:600; margin-bottom:.2rem;">
          <xsl:value-of select="$mel_fn_basedon"/>
        </p>
      </xsl:when>
    </xsl:choose>
    <p style="font-style:italic; font-size:0.8rem; margin-bottom:.5rem;">
      report created at: <xsl:value-of select=".//createdat"/>
    </p>
    <!-- Row 1: Summary + Coverage by language side by side (coverage docs only) -->
    <xsl:if test="mel_analysis/totals or mel_analysis/lexicons">
      <div class="row g-3 mb-3">
        <div class="col-md-auto">
          <xsl:apply-templates select="mel_analysis/totals"/>
        </div>
        <div class="col">
          <xsl:apply-templates select="mel_analysis/lexicons"/>
          <xsl:if test="mel_analysis/unmatched_by_language">
            <p style="font-size:0.85rem; margin-top:.25rem;">
              <a href="#unmatched-by-lg">
                <xsl:value-of select="count(mel_analysis/unmatched_by_language/lg/gl)"/>
                <xsl:text> unmatched glosses by language &#x2193;</xsl:text>
              </a>
            </p>
          </xsl:if>
        </div>
      </div>
    </xsl:if>
    <!-- Row 2: annotated MEL table + unmatched glosses (full width) -->
    <xsl:apply-templates select="mel_analysis/semantics"/>
    <xsl:apply-templates select="mel_analysis/unmatched_by_language"/>
  </div>
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

<!-- ── MEL usage (non-annotated semantics: old coverage docs without languages) -->
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
          <td class="col-gloss cov-gl-col">
            <xsl:for-each select="gl">
              <xsl:choose>
                <xsl:when test="@uses = '0'">
                  <span class="cov-unused"><xsl:value-of select="."/></span>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="."/>
                </xsl:otherwise>
              </xsl:choose>
              <xsl:if test="@xml:lang">
                <sub><xsl:value-of select="@xml:lang"/></sub>
              </xsl:if>
              <xsl:if test="@uses != '0'">
                <sub class="cov-uses">&#160;<xsl:value-of select="@uses"/></sub>
              </xsl:if>
              <xsl:if test="position() != last()"><xsl:text>; </xsl:text></xsl:if>
            </xsl:for-each>
          </td>
        </tr>
      </xsl:for-each>
    </tbody>
  </table>
</xsl:template>

<!-- ── Shared: one gloss item with uses count and optional xml:lang sub ─── -->
<xsl:template match="gl" mode="gl-item">
  <xsl:choose>
    <xsl:when test="@pseudo='true'"><em><xsl:value-of select="."/></em></xsl:when>
    <xsl:when test="@uses='0'"><span class="cov-gl-zero"><xsl:value-of select="."/></span></xsl:when>
    <xsl:otherwise><xsl:value-of select="."/></xsl:otherwise>
  </xsl:choose>
  <xsl:if test="@xml:lang">
    <sub><xsl:value-of select="@xml:lang"/></sub>
  </xsl:if>
  <xsl:if test="@uses and @uses != '0'">
    <sub class="cov-uses">&#160;<xsl:value-of select="@uses"/></sub>
  </xsl:if>
</xsl:template>

<!-- ── Shared: one reconstruction badge ─────────────────────────────────── -->
<xsl:template name="reconstruction-badge">
  <span>
    <xsl:attribute name="class">
      <xsl:text>badge me-1 </xsl:text>
      <xsl:choose>
        <xsl:when test="@status='set'">cov-badge-set</xsl:when>
        <xsl:when test="@status='isolate'">cov-badge-isolate</xsl:when>
        <xsl:otherwise>cov-badge-failure</xsl:otherwise>
      </xsl:choose>
    </xsl:attribute>
    <xsl:text>*</xsl:text><xsl:value-of select="."/>
  </span>
</xsl:template>

<!-- ── Annotated semantics (coverage docs and mel_lexicon docs) ──────────── -->
<xsl:template match="semantics[../languages]">
  <!-- True when any MEL has reconstructions (coverage docs); absent in mel_lexicon docs -->
  <xsl:variable name="has_reconstructions" select="count(mel/reconstruction) &gt; 0"/>
  <h5>MELs and the forms that match them
    <button type="button" class="btn btn-sm btn-outline-secondary ms-2"
            id="btn-toggle-coverage-glosses">Show glosses</button>
    <small class="text-muted" style="font-size:0.8em; font-weight:normal;">
      &#160;
      <xsl:choose>
        <xsl:when test="$has_reconstructions">
          <span class="badge cov-badge-set me-1">set</span>
          <span class="badge cov-badge-isolate me-1">isolate</span>
          <span class="badge cov-badge-failure me-1">failure</span>
        </xsl:when>
        <xsl:otherwise>
          <span class="badge cov-badge-lex me-1">lexicon form</span>
        </xsl:otherwise>
      </xsl:choose>
      <span class="badge cov-mel-unused me-1">unused MEL</span>
      <span class="badge cov-gl-zero me-1">unused gloss</span>
      &#160; usage count in subscript
    </small>
  </h5>
  <div class="cov-annotated-wrap">
  <table class="table table-sm table-hover table-bordered sortable cov-table cov-annotated">
    <thead>
      <tr>
        <th style="white-space:nowrap">MEL</th>
        <th>Gloss</th>
        <xsl:if test="$has_reconstructions">
          <th>Protoform</th>
        </xsl:if>
        <xsl:for-each select="../languages/lg">
          <th style="white-space:nowrap"><xsl:value-of select="."/></th>
        </xsl:for-each>
      </tr>
    </thead>
    <tbody>
      <xsl:for-each select="mel">
        <xsl:variable name="mel_node" select="."/>
        <tr>
          <xsl:if test="@pseudo='true'">
            <xsl:attribute name="class">table-secondary</xsl:attribute>
          </xsl:if>
          <td style="vertical-align:top; white-space:nowrap; font-size:0.8em">
            <xsl:choose>
              <xsl:when test="@pseudo='true'"><span class="text-muted">—</span></xsl:when>
              <xsl:when test="@unused='true'">
                <span class="cov-mel-unused"><xsl:value-of select="@id"/></span>
              </xsl:when>
              <xsl:when test="count(lg/form) = 0 and count(reconstruction) = 0 and not(@unused)">
                <span class="cov-mel-unused"><xsl:value-of select="@id"/></span>
              </xsl:when>
              <xsl:otherwise><xsl:value-of select="@id"/></xsl:otherwise>
            </xsl:choose>
          </td>
          <td style="vertical-align:top" class="cov-hm-cell cov-gl-hm">
            <span class="cov-hm-full">
              <xsl:for-each select="gl">
                <xsl:apply-templates select="." mode="gl-item"/>
                <xsl:if test="position() != last()"><xsl:text>; </xsl:text></xsl:if>
              </xsl:for-each>
            </span>
            <span class="cov-hm-short">
              <xsl:apply-templates select="gl[1]" mode="gl-item"/>
            </span>
            <xsl:if test="count(gl) &gt; 1">
              <button type="button" class="btn btn-link btn-sm p-0 ms-1 cov-hm-toggle"
                      data-more-count="{count(gl) - 1}"
                      title="Show all glosses for this MEL">+<xsl:value-of select="count(gl) - 1"/></button>
            </xsl:if>
          </td>
          <xsl:if test="$has_reconstructions">
            <td style="vertical-align:top" class="cov-hm-cell cov-pf-hm">
              <span class="cov-hm-full">
                <xsl:for-each select="reconstruction">
                  <xsl:call-template name="reconstruction-badge"/>
                </xsl:for-each>
              </span>
              <span class="cov-hm-short">
                <xsl:for-each select="reconstruction[1]">
                  <xsl:call-template name="reconstruction-badge"/>
                </xsl:for-each>
              </span>
              <xsl:if test="count(reconstruction) &gt; 1">
                <button type="button" class="btn btn-link btn-sm p-0 ms-1 cov-hm-toggle"
                        data-more-count="{count(reconstruction) - 1}"
                        title="Show all reconstructions for this MEL">+<xsl:value-of select="count(reconstruction) - 1"/></button>
              </xsl:if>
            </td>
          </xsl:if>
          <xsl:for-each select="../../languages/lg">
            <xsl:variable name="lgname" select="."/>
            <td style="vertical-align:top">
              <xsl:for-each select="$mel_node/lg[@name=$lgname]/form">
                <span>
                  <xsl:attribute name="class">
                    <xsl:text>badge me-1 </xsl:text>
                    <xsl:choose>
                      <xsl:when test="@status='set'">cov-badge-set</xsl:when>
                      <xsl:when test="@status='isolate'">cov-badge-isolate</xsl:when>
                      <xsl:when test="@status='failure'">cov-badge-failure</xsl:when>
                      <xsl:otherwise>cov-badge-lex</xsl:otherwise>
                    </xsl:choose>
                  </xsl:attribute>
                  <xsl:value-of select="."/>
                </span>
                <xsl:if test="@gl != ''">
                  <span class="cov-gloss" style="font-size:0.75em; color:#666; margin-right:0.4em">
                    <xsl:value-of select="@gl"/>
                  </span>
                </xsl:if>
              </xsl:for-each>
            </td>
          </xsl:for-each>
        </tr>
      </xsl:for-each>
    </tbody>
  </table>
  </div>
</xsl:template>

<!-- ── Unmatched glosses by language ─────────────────────────────────────── -->
<xsl:template match="unmatched_by_language">
  <a name="unmatched-by-lg"/>
  <h5>Unmatched glosses by language
    <small class="text-muted" style="font-size:0.8em; font-weight:normal;">
      &#160;
      <span class="cov-repeated" style="padding:1px 6px;">in multiple languages</span>
    </small>
  </h5>
  <table class="table table-sm table-hover table-bordered sortable cov-table">
    <thead>
      <tr>
        <th>Language</th>
        <th>Count</th>
        <th>Unmatched glosses</th>
      </tr>
    </thead>
    <tbody>
      <xsl:for-each select="lg">
        <tr>
          <td style="white-space:nowrap; vertical-align:top">
            <xsl:value-of select="@id"/>
          </td>
          <td style="vertical-align:top">
            <xsl:value-of select="count(gl)"/>
          </td>
          <td class="col-gloss cov-gl-col">
            <xsl:for-each select="gl">
              <xsl:choose>
                <xsl:when test="@repeated = 'true'">
                  <span class="cov-repeated"><xsl:value-of select="."/></span>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="."/>
                </xsl:otherwise>
              </xsl:choose>
              <xsl:if test="position() != last()"><xsl:text>, </xsl:text></xsl:if>
            </xsl:for-each>
          </td>
        </tr>
      </xsl:for-each>
    </tbody>
  </table>
</xsl:template>

</xsl:stylesheet>
