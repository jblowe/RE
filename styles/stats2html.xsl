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
                <h3>Statistics</h3>
                <h5>Summary statistics</h5>
                <xsl:apply-templates select=".//totals" mode="summary"/>
                <h5>Language statistics</h5>
                <xsl:apply-templates select=".//stats"/>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="totals" mode="summary">
        <table class="table table-striped sortable">
            <thead>
                <tr>
                    <th>Stat</th>
                    <th>Value</th>
                </tr>
            </thead>
            <xsl:for-each select="./*">
                <tr>
                    <td><xsl:value-of select ="name(.)"/></td>
                    <td><xsl:value-of select='format-number(@value, "###,###")' /></td>
                </tr>
            </xsl:for-each>
        </table>
    </xsl:template>

    <xsl:template match="stats">
        <table class="table table-striped sortable">
            <thead>
                <tr>
                    <th>Language</th>
                    <th>Forms</th>
                    <th>No Parses</th>
                    <th>Reconstructions</th>
                </tr>
            </thead>
            <xsl:apply-templates select="lexicon"/>
            <xsl:apply-templates select="totals" mode="bottom"/>
        </table>
    </xsl:template>

    <xsl:template match="lexicon">
        <tr>
            <td>
                <xsl:value-of select="@language"/>
            </td>
            <td><xsl:value-of select='format-number(forms/@value, "###,###")' /></td>
            <td><xsl:value-of select='format-number(no_parses/@value, "###,###")' /></td>
            <td><xsl:value-of select='format-number(reconstructions/@value, "###,###")' /></td>
        </tr>
    </xsl:template>

    <xsl:template match="totals" mode="bottom">
        <tr>
            <td>
                Totals
            </td>
            <td><xsl:value-of select='format-number(forms/@value, "###,###")' /></td>
            <td><xsl:value-of select='format-number(no_parses/@value, "###,###")' /></td>
            <td><xsl:value-of select='format-number(reconstructions/@value, "###,###")' /></td>
        </tr>
    </xsl:template>


</xsl:stylesheet>
		