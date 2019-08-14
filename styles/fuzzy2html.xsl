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
                <h3>Fuzzy</h3>
                <xsl:apply-templates select=".//fuzzy"/>
                <!-- e.g.
                <mel id="wn1">
                    <gl>ginseng</gl>
                -->
            </body>
        </html>
    </xsl:template>

    <xsl:template match="fuzzy">
        <table class="table table-striped sortable">
            <thead>
                <tr>
                    <th>Language</th>
                    <th>To</th>
                    <th>From</th>
                </tr>
            </thead>
            <xsl:for-each select="./*">
                <tr>
                    <td><xsl:value-of select ="@dial"/></td>
                    <td width="50%"><xsl:apply-templates select="from"/></td>
                    <td><xsl:value-of select ="@to"/></td>
                </tr>
            </xsl:for-each>
        </table>
    </xsl:template>


    <xsl:template match="from">
            <span class=".bg-info"><xsl:apply-templates/>, </span>
    </xsl:template>

</xsl:stylesheet>
		