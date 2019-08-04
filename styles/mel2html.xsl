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
                <h3>Meaning Equivalence List</h3>
                <h4>MEL statistics</h4>
                <xsl:apply-templates select=".//totals"/>
                <h4>MELs</h4>
                <xsl:apply-templates select=".//semantics"/>
                <!-- e.g.
                <mel id="wn1">
                    <gl>ginseng</gl>
                -->
            </body>
        </html>
    </xsl:template>

    <xsl:template match="totals">
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
                    <td><xsl:value-of select ="@value"/></td>
                </tr>
            </xsl:for-each>
        </table>
    </xsl:template>

    <xsl:template match="semantics">
        <table class="table table-striped sortable">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Glosses</th>
                </tr>
            </thead>
            <xsl:apply-templates select="mel"/>
        </table>
    </xsl:template>

    <xsl:template match="mel">
        <tr>
            <td>
                <xsl:value-of select="@id"/>
            </td>
            <td>
                <xsl:for-each select=".//gl">
                    <span style="background-color: dodgerblue;color: white"><xsl:value-of select="."/></span>
                    <xsl:if test="position() != last()">, </xsl:if>
                </xsl:for-each>
            </td>
        </tr>
    </xsl:template>


    <xsl:template match="gl">
            <span class=".bg-info"><xsl:apply-templates/></span>
    </xsl:template>

</xsl:stylesheet>
		