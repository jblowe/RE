<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        version="1.0">


    <xsl:output
            method="html"
            indent="yes"
            encoding="utf-8"/>

    <xsl:template match="params">
        <html>
            <head>
            </head>
            <body>
                <h5>Parameters available</h5>
                <div>
                <table class="table table-responsive table-sm retable">
                    <thead/>
                    <tr><th class="table-primary" colspan="2"><h6>Tables and languages ("reconstructions")</h6></th></tr>
                    <xsl:apply-templates select="reconstruction"/>
                    <xsl:if test="fuzzy">
                        <tr><th class="table-primary" colspan="2"><h6>Fuzzy files</h6></th></tr>
                        <xsl:apply-templates select="fuzzy"/>
                    </xsl:if>
                    <xsl:if test="mel">
                        <tr><th class="table-primary" colspan="2"><h6>MELs</h6></th></tr>
                        <xsl:apply-templates select="mel"/>
                    </xsl:if>
                    <xsl:if test="csvdata">
                        <tr><th class="table-primary" colspan="2"><h6>Tabular data files</h6></th></tr>
                        <xsl:apply-templates select="csvdata"/>
                    </xsl:if>
                    <xsl:if test="param">
                        <tr><th class="table-primary" colspan="2"><h6>Other parameters</h6></th></tr>
                        <xsl:apply-templates select="param"/>
                    </xsl:if>
                    <tr><th class="table-primary" colspan="2">
                        <h6>Lexicons</h6>
                    </th></tr>
                    <tr><td>
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
                                    <td><xsl:value-of select="@name"/></td>
                                    <td><xsl:value-of select="@file"/></td>
                                </tr>
                            </xsl:for-each>
                        </table>
                        </div>
                    </td></tr>
                </table>
                </div>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="reconstruction">
        <tr class="table-secondary">
            <th>
                "<xsl:value-of select="@name"/>"
            </th>
            <td>
                <i><xsl:value-of select="title/@value"/></i>
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
        <td><xsl:value-of select="@name"/></td>
        <td><xsl:value-of select="@correspondences"/></td>
        </tr>
    </xsl:template>

    <xsl:template match="action">
        <tr>
          <xsl:choose>
            <xsl:when test="@target">
                <td>target protolanguage</td><td><xsl:value-of select="@target"/></td>
            </xsl:when>
            <xsl:otherwise>
                <td>upstream</td><td><xsl:value-of select="@from"/>
                >
                <xsl:value-of select="@to"/></td>
            </xsl:otherwise>
            </xsl:choose>
        </tr>
    </xsl:template>

    <xsl:template match="param">
        <tr>
            <td><xsl:value-of select="@name"/></td>
            <td><xsl:value-of select="@value"/></td>
        </tr>
    </xsl:template>

    <xsl:template match="fuzzy|mel|csvdata">
        <tr>
            <td><xsl:value-of select="@name"/></td>
            <td><xsl:value-of select="@file"/></td>
        </tr>
    </xsl:template>

</xsl:stylesheet>
		