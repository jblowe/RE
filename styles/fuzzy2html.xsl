<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

    <xsl:output
            method="html"
            indent="yes"
            encoding="utf-8"/>

    <xsl:strip-space
            elements="*"/>

    <xsl:template match="/">
        <div>
                <h4>Fuzzy</h4>
                <xsl:apply-templates select=".//fuzzy"/>
            </div>
    </xsl:template>

    <xsl:template match="fuzzy">
        <table class="table table-sm table-striped sortable">
            <thead>
                <tr>
                    <th>Language</th>
                    <th>From (input values)</th>
                    <th>To (fuzzied value)</th>
                </tr>
            </thead>
            <xsl:for-each select="./*">
                <tr>
                    <td style="vertical-align:top; white-space:nowrap">
                        <xsl:value-of select="@dial"/>
                    </td>
                    <td style="overflow-wrap:break-word; word-break:break-word; vertical-align:top; white-space:normal">
                        <xsl:for-each select="from">
                            <xsl:choose>
                                <!-- Coverage annotated: uses="0" → greyed out -->
                                <xsl:when test="@uses = '0'">
                                    <span class="cov-unused" title="unused">
                                        <xsl:value-of select="."/>
                                    </span>
                                </xsl:when>
                                <!-- Coverage annotated: uses > 0 → show count in subscript -->
                                <xsl:when test="@uses">
                                    <xsl:value-of select="."/>
                                    <sub class="cov-uses">&#160;<xsl:value-of select="@uses"/></sub>
                                </xsl:when>
                                <!-- No coverage data (raw fuzzy file) → plain text -->
                                <xsl:otherwise>
                                    <xsl:value-of select="."/>
                                </xsl:otherwise>
                            </xsl:choose>
                            <xsl:if test="position()!=last()">, </xsl:if>
                        </xsl:for-each>
                    </td>
                    <td style="overflow-wrap:break-word; word-break:break-word; vertical-align:top; white-space:normal">
                        <xsl:value-of select="@to"/>
                        <xsl:if test="@to_uses">
                            <sub class="cov-uses">&#160;<xsl:value-of select="@to_uses"/></sub>
                        </xsl:if>
                    </td>
                </tr>
            </xsl:for-each>
        </table>
    </xsl:template>

</xsl:stylesheet>
