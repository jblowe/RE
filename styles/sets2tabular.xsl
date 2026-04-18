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

  <xsl:template match="/">
    <html>
      <head>
        <link rel="stylesheet" type="text/css" href="/static/reconengine.css"/>
      </head>
      <body>
        <div class="row">
          <div class="col">
            <h5>Regular cognate sets</h5>
            <div style="float: left; width:60px;">
              <b>n =
                <xsl:value-of select="count(.//sets/set)"/>
              </b>
            </div>
            <div style="float: left; width:300px;">
              <i>created at:
                <xsl:value-of select=".//createdat"/>
              </i>
            </div>
            <div style="float: left; width:180px;">
              <a href="#isolates">
                <xsl:value-of select="count(.//isolates/rfx)"/>
                isolates
              </a>
            </div>
            <div style="float: left; width:180px;">
              <a href="#failures">
                <xsl:value-of select="count(.//failures/rfx)"/>
                failures
              </a>
            </div>
          </div>
        </div>
        <!-- TODO: figure out what class, if any makes table both sortable and header-sticky -->
        <div class="row">
          <div class="col">
            <table class="table table-sm table-hover table-bordered sets sortable">
              <thead class="sticky-top top-0">
                <tr>
                  <th class="col-num">num</th>
                  <th class="col-plg">plg</th>
                  <th class="col-pfm">pfm</th>
                  <!-- th>pgl</th -->
                  <th class="col-rcn">rcn</th>
                  <th class="col-mel">mel</th>
                  <xsl:apply-templates select=".//languages"/>
                </tr>
              </thead>
              <xsl:call-template name="sets">
                <xsl:with-param name="lgs" select=".//languages"/>
              </xsl:call-template>
            </table>
          </div>
        </div>
        <div class="row">
          <div class="col">
            <xsl:apply-templates select=".//isolates"/>
          </div>
        </div>
        <div class="row">
          <div class="col">
            <xsl:apply-templates select=".//failures"/>
          </div>
        </div>
      </body>
    </html>
  </xsl:template>

  <xsl:template name="sets">
    <xsl:param name="lgs"/>
    <xsl:for-each select=".//sets/set">
      <tr>
        <td class="col-num">
          <xsl:value-of select="id"/>
        </td>

        <xsl:choose>
          <xsl:when test="multi">
            <td class="col-plg">
              <span class="">
                <xsl:value-of select=".//plg"/>
              </span>
            </td>
            <td class="col-pfm">
              <span class="multiple">
                <xsl:attribute name="title">
                  <xsl:for-each select=".//pfm">
                    <xsl:if test="position() != 1">
                      <xsl:text>,</xsl:text>
                    </xsl:if>
                    <xsl:value-of select="."/>
                  </xsl:for-each>
                </xsl:attribute>
                <xsl:value-of select="multi/pfm"/>
              </span>
            </td>
            <td class="col-rcn">
              <span>
                <xsl:attribute name="title">
                  <xsl:for-each select=".//rcn">
                    <xsl:if test="position() != 1">
                      <xsl:text>,</xsl:text>
                    </xsl:if>
                    <xsl:value-of select="."/>
                  </xsl:for-each>
                </xsl:attribute>
                <xsl:value-of select="multi/rcn"/>
              </span>
            </td>
          </xsl:when>
          <xsl:otherwise>
            <td class="col-plg">
              <xsl:value-of select="plg"/>
            </td>
            <td class="col-pfm">
              <xsl:value-of select="pfm"/>
            </td>
            <td class="col-rcn">
              <xsl:value-of select="rcn"/>
            </td>
          </xsl:otherwise>
        </xsl:choose>
        <td class="col-mel" title="{mel}">
          <xsl:value-of select="melid"/>:
          <xsl:value-of select="substring-before(concat(mel, ',' ) , ',')"/>
        </td>
        <xsl:variable name="reflexes" select="sf"/>
        <xsl:for-each select="$lgs/*">
          <xsl:variable name="label" select="."/>
          <td class="col-lg" style="vertical-align:top">
            <!-- Leaf language reflexes: search at any depth -->
            <xsl:for-each select="$reflexes//rfx">
              <xsl:if test="lg = $label">
                <!-- Each form gets its own line; gloss shown inline so that
                     multiple tone/semantic variants in one cell stay legible.
                     class rfx-gloss is toggled by the "Show/Hide glosses"
                     button via #sets-content.glosses-hidden .rfx-gloss. -->
                <div title="{id}">
                  <xsl:apply-templates select="lx"/>
                  <xsl:if test="gl != ''">
                    <xsl:text> </xsl:text>
                    <small class="rfx-gloss" style="color:#888"><xsl:value-of select="gl"/></small>
                  </xsl:if>
                </div>
              </xsl:if>
            </xsl:for-each>
            <!-- Intermediate proto-language reconstructions: match subset by plg -->
            <xsl:for-each select="$reflexes//subset">
              <xsl:if test="plg = $label">
                <div title="{id}">
                  <xsl:value-of select="pfm"/>
                  <xsl:if test="rcn != ''">
                    <xsl:text> </xsl:text>
                    <small class="rfx-gloss" style="color:#888"><xsl:value-of select="rcn"/></small>
                  </xsl:if>
                </div>
              </xsl:if>
            </xsl:for-each>
          </td>
        </xsl:for-each>
      </tr>
    </xsl:for-each>
  </xsl:template>


  <xsl:template match="multi">
    <td>
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
    </td>
  </xsl:template>


  <xsl:template match="languages">
    <xsl:for-each select="*">
      <th class="col-lg">
        <xsl:value-of select="."/>
      </th>
    </xsl:for-each>
  </xsl:template>

  <xsl:template match="set" name="set">
    <li class="sf">
      <div class="wrapper etymonrow">
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
        <div class="mel" title="{mel}"><xsl:value-of select="melid"/>:
          <xsl:value-of select="substring-before(concat(mel, ',' ) , ',')"/>
        </div>
      </div>
      <xsl:apply-templates select="sf"/>
    </li>
  </xsl:template>

  <xsl:template match="sf">
    <xsl:apply-templates select="rfx"/>
    <xsl:apply-templates select="subset"/>
  </xsl:template>

  <xsl:template match="subset">
    <div class="level{@level}">
      <li>
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
      </li>
      <ul class="list-unstyled">
        <xsl:apply-templates select="sf2"/>
      </ul>
    </div>
  </xsl:template>

  <xsl:template match="rfx">
    <li>
      <div class="wrapper">
        <div class="lg">
          <xsl:apply-templates select="lg"/>
        </div>
        <div class="lx">
          <xsl:apply-templates select="lx"/>
        </div>
        <div class="gl">
          <xsl:apply-templates select="gl"/>
        </div>
        <xsl:choose>
          <xsl:when test="hn">
            <div class="nn">[<xsl:apply-templates select="hn"/>]
            </div>
          </xsl:when>
          <xsl:when test="id">
            <div class="nn">[<xsl:apply-templates select="id"/>]
            </div>
          </xsl:when>
          <xsl:otherwise/>
        </xsl:choose>
      </div>
    </li>
  </xsl:template>

  <xsl:template match="gl|hw|lx">
    <xsl:apply-templates/>
  </xsl:template>

</xsl:stylesheet>
