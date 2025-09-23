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
                <a name="{@dialecte}"/>
                <h5>
                    <xsl:value-of select="@dialecte"/>
                </h5>
                <div style="float: left; width:60px;">
                    <b>n =
                        <xsl:value-of select="count(lexicon/entry)"/>
                    </b>
                </div>
                <div style="float: left; width:220px;">
                    <i>created at:
                        <xsl:value-of select=".//createdat"/>
                    </i>
                </div>
                <div style="float: left; width:160px;">
                    <a href="?paragraph">switch to paragraph display</a>
                </div>
                <div style="clear:both;"></div>
                <xsl:apply-templates select=".//lexicon"/>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="lexicon">
        <div>
            <div class="table-responsive">
            <table class="table table-sm table-striped sortable">
                <thead>
                    <tr>
                        <th>Form</th>
                        <th>Gloss</th>
                        <th>Computed (Alternate) Gloss</th>
                        <th>ID</th>
                    </tr>
                </thead>
                <xsl:for-each select="entry">
                    <tr>
                        <td><xsl:apply-templates select="hw"/></td>
                        <td>
                            <xsl:for-each select="gl">
                                <i><xsl:value-of select="." /></i>
                                <xsl:if test="position() != last()">, </xsl:if>
                            </xsl:for-each>
                        </td>
                        <td>
                            <xsl:for-each select="ngl">
                                <i><xsl:value-of select="." /></i>
                                <xsl:if test="position() != last()">, </xsl:if>
                            </xsl:for-each>
                        </td>
                        <td><xsl:apply-templates select="@id"/></td>
                    </tr>
                </xsl:for-each>
            </table>
            </div>
        </div>
    </xsl:template>

    <xsl:template match="gl|hw">
            <xsl:apply-templates/>
    </xsl:template>

</xsl:stylesheet>
