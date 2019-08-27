<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

    <xsl:output
            method="html"
            indent="yes"
            encoding="utf-8"/>

    <xsl:template match="/">
        <html>
            <head>
            </head>
            <body>
                <xsl:apply-templates select=".//lexicon"/>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="lexicon">
        <div>
            <a name="{@dialecte}"/>
            <h3>
                <xsl:value-of select="@dialecte"/>
            </h3>
            <h5>n = <xsl:value-of select="count(entry)" /></h5>
            <table class="table table-striped sortable sticky-top">
                <thead>
                    <tr>
                        <th>Form</th>
                        <th>Source Gloss</th>
                        <th>Computed (Alternate) Gloss</th>
                        <th>ID</th>
                    </tr>
                </thead>
                <xsl:for-each select="entry">
                    <tr>
                        <td><xsl:apply-templates select="hw"/></td>
                        <td><xsl:apply-templates select="gl"/></td>
                        <td>
                            <xsl:for-each select="ngl">
                                <xsl:value-of select="." />
                                <xsl:if test="position() != last()">, </xsl:if>
                            </xsl:for-each>
                        </td>
                        <td><xsl:apply-templates select="@id"/></td>
                    </tr>
                </xsl:for-each>
            </table>
        </div>
    </xsl:template>

    <xsl:template match="gl|hw">
            <xsl:apply-templates/>
    </xsl:template>

</xsl:stylesheet>
