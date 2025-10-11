<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version="1.0">

  <xsl:output method="html" indent="yes" encoding="utf-8"/>

    <xsl:output
            method="html"
            indent="yes"
            encoding="utf-8"/>

    <xsl:template match="params">
        <h5>Parameters available</h5>
        <div>
            <table class="table table-responsive table-sm retable">
                <thead/>
                <tr>
                    <th class="table-primary" colspan="2">
                        <h6>Tables and languages ("reconstructions")</h6>
                    </th>
                </tr>
                <xsl:apply-templates select="reconstruction"/>
                <xsl:if test="fuzzy">
                    <tr>
                        <th class="table-primary" colspan="2">
                            <h6>Fuzzy files</h6>
                        </th>
                    </tr>
                    <xsl:apply-templates select="fuzzy"/>
                </xsl:if>
                <xsl:if test="mel">
                    <tr>
                        <th class="table-primary" colspan="2">
                            <h6>MELs</h6>
                        </th>
                    </tr>
                    <xsl:apply-templates select="mel"/>
                </xsl:if>
                <xsl:if test="csvdata">
                    <tr>
                        <th class="table-primary" colspan="2">
                            <h6>Tabular data files</h6>
                        </th>
                    </tr>
                    <xsl:apply-templates select="csvdata"/>
                </xsl:if>
                <xsl:if test="param">
                    <tr>
                        <th class="table-primary" colspan="2">
                            <h6>Other parameters</h6>
                        </th>
                    </tr>
                    <xsl:apply-templates select="param"/>
                </xsl:if>
                <tr>
                    <th class="table-primary" colspan="2">
                        <h6>Lexicons</h6>
                    </th>
                </tr>
                <tr>
                    <td>
                        <div>
                            <table class="table table-responsive table-sm sortable">
                                <thead>
                                    <tr>
                                        <th>Language</th>
                                        <th>File</th>
                                    </tr>
                                </thead>
                                <xsl:for-each select=".//attested">
                                    <tr>
                                        <td>
                                            <xsl:value-of select="@name"/>
                                        </td>
                                        <td>
                                            <xsl:value-of select="@file"/>
                                        </td>
                                    </tr>
                                </xsl:for-each>
                            </table>
                        </div>
                    </td>
                </tr>
                <xsl:if test="quirks">
                    <tr>
                        <th class="table-primary" colspan="2">
                            <h6>Exceptions</h6>
                        </th>
                    </tr>
                    <xsl:apply-templates select="quirks"/>
                </xsl:if>
            </table>
        </div>
    </xsl:template>

    <xsl:template match="reconstruction">
        <tr class="table-secondary">
            <th>
                "<xsl:value-of select="@name"/>"
            </th>
            <td>
                <i>
                    <xsl:value-of select="title/@value"/>
                </i>
            </td>
            <xsl:apply-templates select="proto_language"/>
            <xsl:apply-templates select="action"/>
        </tr>
    </xsl:template>

    <xsl:template match="title">
        <tr>
            <td>title</td>
        </tr>
    </xsl:template>

    <xsl:template match="proto_language">
        <tr>
            <td>
                <xsl:value-of select="@name"/>
            </td>
            <td>
                <xsl:value-of select="@correspondences"/>
            </td>
        </tr>
    </xsl:template>

    <xsl:template match="action">
        <tr>
            <xsl:choose>
                <xsl:when test="@target">
                    <td>target protolanguage</td>
                    <td>
                        <xsl:value-of select="@target"/>
                    </td>
                </xsl:when>
                <xsl:otherwise>
                    <td>upstream</td>
                    <td>
                        <xsl:value-of select="@from"/>
                        >
                        <xsl:value-of select="@to"/>
                    </td>
                </xsl:otherwise>
            </xsl:choose>
        </tr>
    </xsl:template>

    <xsl:template match="param">
        <tr>
            <td>
                <xsl:value-of select="@name"/>
            </td>
            <td>
                <xsl:value-of select="@value"/>
            </td>
        </tr>
    </xsl:template>

    <xsl:template match="fuzzy|mel|csvdata">
        <tr>
            <td>
                <xsl:value-of select="@name"/>
            </td>
            <td>
                <xsl:value-of select="@file"/>
            </td>
        </tr>
    </xsl:template>

    <xsl:template match="quirks">
          <h6>Exceptions</h6>
          <table class="table table-sm table-bordered">
            <thead>
              <tr class="table-secondary">
                <th scope="col">ID</th>
                <th scope="col">Source ID</th>
                <th scope="col">Lang</th>
                <th scope="col">Lexeme</th>
                <th scope="col">Gloss</th>
                <th scope="col">Analysis</th>
                <th scope="col">Alternative</th>
                <th scope="col">Notes</th>
              </tr>
            </thead>
            <tbody>
              <xsl:apply-templates select="quirk"/>
            </tbody>
          </table>
  </xsl:template>

  <xsl:template match="quirk">
    <tr>
      <td><xsl:value-of select="@id"/></td>
      <td><xsl:value-of select="sourceid"/></td>
      <td><xsl:value-of select="lg"/></td>
      <td><xsl:value-of select="lx"/></td>
      <td><xsl:value-of select="gl"/></td>
      <td>
        <xsl:variable name="slot"
          select="analysis/slot"/>
        <xsl:variable name="val"
          select="analysis/value"/>
        <xsl:value-of select="$slot"/>
        <xsl:if test="string($val)">=<xsl:value-of select="$val"/></xsl:if>
      </td>
      <td><xsl:value-of select="alt"/></td>
      <td>
        <xsl:for-each select="note">
          <xsl:value-of select="."/>
          <xsl:if test="position() != last()">; </xsl:if>
        </xsl:for-each>
      </td>
    </tr>
  </xsl:template>

  <xsl:template match="text()|@*"/>

</xsl:stylesheet>
