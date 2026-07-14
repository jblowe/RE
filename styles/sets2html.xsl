<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:exsl="http://xmlns.opentechnology.org/xslt-extensions/functions"
                xmlns:re="http://exslt.org/re"
>

  <xsl:include href="sets-isolates-failures.xsl"/>

  <xsl:output
          method="html"
          indent="yes"
          encoding="utf-8"/>

  <!-- When lazy='1' the isolates and failures sections are replaced with
       lightweight stubs; the client fetches them on demand. -->
  <xsl:param name="lazy" select="'0'"/>

  <xsl:template match="/">
    <div>
      <h5>Regular cognate sets</h5>
      <xsl:call-template name="sets-stats-toolbar">
        <xsl:with-param name="n-sets"     select="count(.//sets/set)"/>
        <xsl:with-param name="n-isolates" select="count(.//isolates/rfx)"/>
        <xsl:with-param name="n-failures" select="count(.//failures/rfx)"/>
        <xsl:with-param name="createdat"  select=".//createdat"/>
      </xsl:call-template>
      <a name="sets-top"/>
      <xsl:apply-templates select=".//sets"/>
      <xsl:choose>
        <xsl:when test="$lazy = '1'">
          <a name="isolates"/>
          <div class="iso-fail-stub" data-section="isolates">
            <button class="btn btn-sm btn-outline-secondary iso-fail-load-btn mt-2">
              <xsl:text>Load </xsl:text><xsl:value-of select="count(.//isolates/rfx)"/><xsl:text> isolates</xsl:text>
            </button>
          </div>
          <a name="failures"/>
          <div class="iso-fail-stub" data-section="failures">
            <button class="btn btn-sm btn-outline-secondary iso-fail-load-btn mt-2">
              <xsl:text>Load </xsl:text><xsl:value-of select="count(.//failures/rfx)"/><xsl:text> failures</xsl:text>
            </button>
          </div>
        </xsl:when>
        <xsl:otherwise>
          <xsl:apply-templates select=".//isolates"/>
          <xsl:apply-templates select=".//failures"/>
        </xsl:otherwise>
      </xsl:choose>
    </div>
  </xsl:template>

  <xsl:param name="isolates" select="'null'"/>

  <xsl:template match="sets" name="sets">
    <ul class="list-unstyled">
      <xsl:apply-templates select="set"/>
    </ul>
  </xsl:template>

  <xsl:template match="set">
    <li class="sf">
      <div class="wrapper etymonrow">
        <div class="id">
          <span class="set-interactive-link" data-set-num="{id}" title="Load in Interactive tab">
            <xsl:value-of select="id"/>
          </span>
        </div>
        <xsl:choose>
          <xsl:when test="multi">
            <xsl:if test="count(multi) &gt; 1">
              <button type="button" class="cov-hm-toggle"
                      data-bs-toggle="collapse"
                      data-bs-target="{concat('#set-multi-', generate-id(.))}"
                      data-more-count="{count(multi) - 1}"
                      aria-expanded="false"
                      title="Show all reconstructions">+<xsl:value-of select="count(multi) - 1"/></button>
            </xsl:if>
            <xsl:apply-templates select="multi[1]"/>
            <xsl:if test="count(multi) &gt; 1">
              <div class="collapse" id="{concat('set-multi-', generate-id(.))}">
                <xsl:apply-templates select="multi[position() &gt; 1]"/>
              </div>
            </xsl:if>
          </xsl:when>
          <xsl:otherwise>
            <div class="plg">
              <xsl:value-of select="plg"/>
            </div>
            <div class="pfm">
              <xsl:value-of select="pfm"/>
            </div>
            <div class="pgl">
              <xsl:value-of select="pgl"/>
            </div>
            <div class="rcn">[<xsl:call-template name="linkify-rcn"><xsl:with-param name="text" select="rcn"/></xsl:call-template>]
            </div>
          </xsl:otherwise>
        </xsl:choose>
        <div class="mel" title="{mel}"><xsl:value-of select="melid"/>:
          <xsl:value-of select="substring-before(concat(mel, ',' ) , ',')"/>
        </div>
      </div>
      <xsl:apply-templates select="sf"/>
    </li>
  </xsl:template>

  <xsl:template match="sf">
    <!-- rfx rows rendered as a real table so columns align -->
    <xsl:if test="rfx">
      <table class="sfx-table">
        <tbody>
          <xsl:apply-templates select="rfx"/>
        </tbody>
      </table>
    </xsl:if>
    <xsl:apply-templates select="subset"/>
  </xsl:template>

  <xsl:template match="multi">
    <div>
      <div class="plg">
        <xsl:value-of select="plg"/>
      </div>
      <div class="pfm">
        <xsl:value-of select="pfm"/>
      </div>
      <div class="pgl">
        <xsl:value-of select="pgl"/>
      </div>
      <div class="rcn">[<xsl:value-of select="rcn"/>]
      </div>
    </div>
  </xsl:template>

  <xsl:template match="subset">
    <div class="level{@level}">
      <div class="wrapper subsetrow">
        <div class="id">
          <xsl:value-of select="id"/>
        </div>
        <div class="plg">
          <xsl:value-of select="plg"/>
        </div>
        <div class="pfm">
          <xsl:value-of select="pfm"/>
        </div>
        <div class="pgl">
          <xsl:value-of select="pgl"/>
        </div>
        <div class="rcn">[<xsl:value-of select="rcn"/>]
        </div>
      </div>
      <xsl:apply-templates select="sf"/>
    </div>
  </xsl:template>

  <xsl:template match="rfx">
    <tr class="{membership}">
      <td class="lg"><xsl:apply-templates select="lg"/></td>
      <td class="lx">
        <xsl:choose>
          <xsl:when test="lxf">
            <xsl:value-of select="lxf"/>
            <small style="color:#888;"> &#171;<xsl:value-of select="lx"/></small>
          </xsl:when>
          <xsl:when test="lxq">
            <xsl:value-of select="lx"/>
            <small style="color:#888;"> &#8674; <xsl:value-of select="lxq"/></small>
          </xsl:when>
          <xsl:otherwise>
            <xsl:apply-templates select="lx"/>
          </xsl:otherwise>
        </xsl:choose>
      </td>
      <td class="gl"><xsl:apply-templates select="gl"/></td>
      <td class="nn">
        <xsl:choose>
          <xsl:when test="hn">[<xsl:apply-templates select="hn"/>]</xsl:when>
          <xsl:when test="id">[<xsl:apply-templates select="id"/>]</xsl:when>
          <xsl:otherwise/>
        </xsl:choose>
      </td>
    </tr>
  </xsl:template>

  <xsl:template match="gl|hw">
    <xsl:apply-templates/>
  </xsl:template>

</xsl:stylesheet>
