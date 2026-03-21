<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<xsl:output method="html" indent="yes" encoding="utf-8"/>

<!-- Reusable named template: compute background-color style for a freq value -->
<xsl:template name="freq-style">
  <xsl:param name="freq"/>
  <xsl:choose>
    <xsl:when test="number($freq) = 0">background-color:#dc3545;color:white;</xsl:when>
    <xsl:when test="number($freq) = 1">background-color:#f8d7da;</xsl:when>
    <xsl:otherwise></xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="/">
  <xsl:apply-templates select=".//tableOfCorr"/>
</xsl:template>

<xsl:template match="tableOfCorr">
  <div>
    <h6>Parameters</h6>
    <table>
      <xsl:if test="parameters/canon">
        <tr>
          <td><b>Syllable canon</b></td>
          <td><xsl:value-of select="parameters/canon/@value"/></td>
        </tr>
      </xsl:if>
      <xsl:if test="parameters/context_match_type">
        <tr>
          <td><b>Context match type</b></td>
          <td><xsl:value-of select="parameters/context_match_type/@value"/></td>
        </tr>
      </xsl:if>
    </table>
    <p/>
    <h6>Macro-classes (used in Contexts)</h6>
    <div>
      <table class="table table-sm table-striped sortable">
        <thead>
          <tr>
            <th>Class</th>
            <th>Members</th>
          </tr>
        </thead>
        <xsl:for-each select="parameters/class">
          <tr>
            <td><xsl:value-of select="@name"/></td>
            <td><xsl:value-of select="@value"/></td>
          </tr>
        </xsl:for-each>
      </table>
    </div>

    <h6>Table of correspondences
      <small class="text-muted ml-2" style="font-size:0.8em; font-weight:normal;">
        &#160;
        <span style="background:#dc3545;color:white;padding:1px 6px;border-radius:3px;">0 uses</span>
        &#160;
        <span style="background:#f8d7da;padding:1px 6px;border-radius:3px;">1 use</span>
      </small>
    </h6>
    <div>
      <table class="table table-sm table-hover table-bordered sets sortable">
        <thead class="sticky-top top-0">
          <tr>
            <th>uses</th>
            <th>num</th>
            <th>*</th>
            <th>syll</th>
            <th>left</th>
            <th>right</th>
            <xsl:for-each select="corr[1]/modern">
              <th><xsl:value-of select="@dialecte"/></th>
            </xsl:for-each>
          </tr>
        </thead>
        <xsl:for-each select="corr">
          <xsl:variable name="row-freq" select="@freq"/>
          <tr>
            <!-- "uses" column: coloured by row frequency -->
            <xsl:variable name="uses-style">
              <xsl:call-template name="freq-style">
                <xsl:with-param name="freq" select="$row-freq"/>
              </xsl:call-template>
            </xsl:variable>
            <td style="{$uses-style}"><xsl:value-of select="$row-freq"/></td>

            <!-- Fixed columns: no colouring -->
            <td><xsl:value-of select="@num"/></td>
            <td><xsl:value-of select="proto"/></td>
            <td><xsl:value-of select="proto/@syll"/></td>
            <td><xsl:value-of select="proto/@contextL"/></td>
            <td><xsl:value-of select="proto/@contextR"/></td>

            <!-- Dialect cells: coloured individually by cell frequency -->
            <xsl:for-each select="modern">
              <xsl:variable name="cell-style">
                <xsl:call-template name="freq-style">
                  <xsl:with-param name="freq" select="@freq"/>
                </xsl:call-template>
              </xsl:variable>
              <td style="{$cell-style}">
                <xsl:for-each select="seg">
                  <xsl:if test="@statut='doute'">=</xsl:if>
                  <xsl:value-of select="."/>
                  <xsl:if test="(position()!=last()) or (@statut!='doute')">,</xsl:if>
                </xsl:for-each>
              </td>
            </xsl:for-each>
          </tr>
        </xsl:for-each>
      </table>
    </div>

    <h5>Rules</h5>
    <div>
      <table class="table table-sm table-hover table-bordered sets sortable">
        <thead class="sticky-top top-0">
          <tr>
            <th>num</th>
            <th>input</th>
            <th>output</th>
            <th>contextL</th>
            <th>contextR</th>
            <th>stage</th>
            <th>language</th>
          </tr>
        </thead>
        <xsl:for-each select="rule">
          <tr>
            <td><xsl:value-of select="@num"/></td>
            <td><xsl:value-of select="input"/></td>
            <td><xsl:value-of select="outcome"/></td>
            <td><xsl:value-of select="input/@contextL"/></td>
            <td><xsl:value-of select="input/@contextR"/></td>
            <td><xsl:value-of select="@stage"/></td>
            <td><xsl:value-of select="outcome/@languages"/></td>
          </tr>
        </xsl:for-each>
      </table>
    </div>
  </div>
</xsl:template>

</xsl:stylesheet>
