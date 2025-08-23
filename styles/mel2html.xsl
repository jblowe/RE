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
                <link rel="stylesheet" type="text/css" href="/static/reconengine.css"/>
            </head>
            <body>
                <a name="top">
                    <h4>Meaning Equivalence List</h4>
                </a>
                <div style="float: right; width:200px;">
                    <a href="#unmatched">
                        <xsl:value-of select="count(.//unmatched/mel/gl)"/>
                        unmatched glosses by language
                    </a>
                </div>
                <xsl:apply-templates select=".//totals"/>
                <xsl:apply-templates select=".//semantics"/>
                <!-- e.g.
                <mel id="wn1">
                    <gl>ginseng</gl>
                -->
                <xsl:apply-templates select=".//unmatched"/>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="totals">
        <h5>MEL statistics</h5>
        <div class="table-responsive">
        <table class="table-sm table-striped sortable">
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
        </div>
    </xsl:template>

    <xsl:template match="semantics">
        <h5>MELs</h5>
        <xsl:call-template name="mel_header"/>
    </xsl:template>

    <xsl:template match="unmatched">
        <a name="unmatched">
            <h5>Unmatched Glosses, by language</h5>
        </a>
        <div style="float: right; width:200px;">
            <a href="#top">
                top
            </a>
        </div>
        <xsl:call-template name="mel_header"/>
    </xsl:template>

    <xsl:template name="mel_header">
        <div class="table-responsive">
        <table class="table-sm table-striped sortable">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Glosses</th>
                </tr>
            </thead>
            <xsl:apply-templates select="mel"/>
        </table>
        </div>
    </xsl:template>

    <xsl:template match="mel">
        <tr>
            <td style="vertical-align: top">
                <xsl:value-of select="@id"/>
            </td>
            <td>
                <xsl:for-each select=".//gl">
                    <xsl:choose>
                    <xsl:when test="@pivot">
                        <span style="background-color: pink;color: white"><xsl:value-of select="."/></span>
                    </xsl:when>
                    <xsl:when test="@uses = '0'">
                        <span style="background-color: hotpink;color: white"><xsl:value-of select="."/></span>
                    </xsl:when>
                    <xsl:otherwise>
                        <span style="background-color: antiquewhite;color: black"><xsl:value-of select="."/></span>
                    </xsl:otherwise>
                    </xsl:choose>
                    <xsl:if test="@xml:lang">
                        <sub><xsl:value-of select="@xml:lang"/></sub>
                    </xsl:if>
                    <xsl:if test="@uses">
                        &#160;<xsl:value-of select="@uses"/>
                    </xsl:if>
                    <xsl:if test="position() != last()">, </xsl:if>
                </xsl:for-each>
            </td>
        </tr>
    </xsl:template>


    <xsl:template match="gl">
            <span class=".bg-info"><xsl:apply-templates/></span>
    </xsl:template>

</xsl:stylesheet>
		