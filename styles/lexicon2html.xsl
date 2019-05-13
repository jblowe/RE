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
                <h3>Lexiques</h3>
                <ul>
                    <xsl:for-each select=".//lexicon">
                        <li>
                            <a href="#{@dialecte}">
                                <xsl:value-of select="@dialecte"/>
                            </a>
                        </li>
                    </xsl:for-each>
                </ul>
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
            <table class="table table-striped sortable">
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
                        <td><xsl:apply-templates select="ngl"/></td>
                        <td><xsl:apply-templates select="@id"/></td>
                    </tr>
                </xsl:for-each>
            </table>
        </div>
    </xsl:template>

    <xsl:template match="gl|hw|ngl">
            <xsl:apply-templates/>
    </xsl:template>

</xsl:stylesheet>
