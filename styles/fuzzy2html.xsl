<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

    <xsl:output
            method="html"
            indent="yes"
            encoding="utf-8"/>

    <xsl:strip-space
            elements="*"/>

    <xsl:template match="/">
        <html>
            <head>
            </head>
            <body>
                <h4>Fuzzy</h4>
                <xsl:apply-templates select=".//fuzzy"/>
                <!-- e.g.
                <mel id="wn1">
                    <gl>ginseng</gl>
                -->
            </body>
        </html>
    </xsl:template>

    <xsl:template match="fuzzy">
        <div class="table-responsive">
        <table class="table-sm table-striped sortable">
            <thead>
                <tr>
                    <th>Language</th>
                    <th>Input data values</th>
                    <th>Fuzzied value</th>
                </tr>
            </thead>
            <xsl:for-each select="./*">
                <tr>
                    <td><xsl:value-of select="@dial"/></td>
                    <td>
                        <xsl:for-each select="from">
                            <xsl:value-of select="."/>
                            <xsl:if test="position()!=last()">,</xsl:if>
                        </xsl:for-each>
                    </td>
                    <td><xsl:value-of select="@to"/></td>
                </tr>
            </xsl:for-each>
        </table>
        </div>
    </xsl:template>


    <xsl:template match="from">
            <span class=".bg-info"><xsl:apply-templates/>, </span>
    </xsl:template>

</xsl:stylesheet>
		