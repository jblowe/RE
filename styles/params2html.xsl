<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        version="1.0">


    <xsl:output
            method="html"
            indent="yes"
            encoding="utf-8"/>

    <xsl:template match="/">
        <html>
            <head>
            </head>
            <body>
                <h3>Parameters</h3>
                <xsl:apply-templates select=".//params"/>
                <div>
                    <h4>Lexicons</h4>
                    <table class="table table-striped sortable sticky-top">
                        <thead>
                            <tr>
                                <th>Language</th>
                                <th>File</th>
                            </tr>
                        </thead>
                        <xsl:for-each select=".//attested">
                            <tr>
                                <td><xsl:value-of select="@name"/></td>
                                <td><xsl:value-of select="@file"/></td>
                            </tr>
                        </xsl:for-each>
                    </table>
                </div>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="proto_language">
        <div>
            Name: <xsl:value-of select="@name"/>
            Correspondences: <xsl:value-of select="@correspondences"/>
        </div>
    </xsl:template>

    <xsl:template match="action">
        <div>
            Run: <xsl:value-of select="@name"/>
            : from <xsl:value-of select="@from"/>
            to <xsl:value-of select="@to"/>
        </div>
    </xsl:template>
    <xsl:template match="param">
        <div>
            <xsl:value-of select="@name"/>
            =
            <xsl:choose>
                <xsl:when test="@name='fuzzy'">
                    <xsl:value-of select="@value"/>
                    <table class="table table-striped sortable sticky-top">
                        <thead>
                            <tr>
                                <th>Dialect</th>
                                <th>From</th>
                                <th>To</th>
                            </tr>
                        </thead>
                        <xsl:for-each select="document(@value)/fuzzy/item">
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
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="@value"/>
                </xsl:otherwise>
            </xsl:choose>
        </div>
    </xsl:template>

</xsl:stylesheet>
		