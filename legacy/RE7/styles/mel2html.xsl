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

                <xsl:apply-templates select=".//semantics"/>
                <!--
                <mel id="wn1">
                    <gl>american ginseng</gl>
                -->
            </body>
        </html>
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
                    <xsl:value-of select="."/>
                    <xsl:if test="position() != last()">, </xsl:if>
                </xsl:for-each>
            </td>
        </tr>
    </xsl:template>


    <xsl:template match="gl">
            <span><xsl:apply-templates/></span>
    </xsl:template>

</xsl:stylesheet>
		