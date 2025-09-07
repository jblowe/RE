<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

    <xsl:output
            method="html"
            indent="yes"
            encoding="utf-8"/>

    <xsl:strip-space
            elements="*"/>

    <xsl:template match="stats">
        <html>
            <head>
            </head>
            <body>
                <p style="font-style: italic">created at: <xsl:value-of select=".//createdat"/></p>
                <h5>Comparison</h5>
                <ol>
                    <xsl:apply-templates select="file"/>
                </ol>
                <xsl:apply-templates select=".//totals" mode="summary"/>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="totals" mode="summary">
        <div class="table-responsive">
        <table class="table-sm table-striped sortable">
            <thead>
                <tr>
                    <th>Stat</th>
                    <xsl:for-each select="../file">
                        <th><xsl:number/></th>
                    </xsl:for-each>
                </tr>
            </thead>
            <xsl:for-each select="./*">
                <tr>
                    <td><xsl:value-of select ="name(.)"/></td>
                    <xsl:for-each select="*">
                        <!-- td><xsl:value-of select='format-number(., "###,###")' /></td -->
                        <td><xsl:value-of select='.' /></td>
                    </xsl:for-each>
                </tr>
            </xsl:for-each>
        </table>
        </div>
    </xsl:template>

    <xsl:template match="file">
        <li><xsl:value-of select='.' /></li>
    </xsl:template>

</xsl:stylesheet>
