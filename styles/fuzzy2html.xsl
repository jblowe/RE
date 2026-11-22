<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

    <xsl:output
            method="html"
            indent="yes"
            encoding="utf-8"/>

    <xsl:strip-space
            elements="*"/>

    <!-- diff marks for the Browse pane's "Compare local with an earlier commit";
         no effect on a file that has no diff annotations -->
    <xsl:include href="diff-common.xsl"/>


    <xsl:template match="/">
        <div>
                <xsl:apply-templates select=".//fuzzy"/>
            </div>
    </xsl:template>

    <xsl:template match="fuzzy">
        <h5>Fuzzy values
          <small class="text-muted" style="font-size:0.8em; font-weight:normal;">
            &#160;
            <span class="badge cov-gl-zero me-1">unused value</span>
            &#160; usage count in subscript
          </small>
        </h5>
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
                    <xsl:call-template name="rowclass"/>
                    <td style="vertical-align:top; white-space:nowrap">
                        <xsl:call-template name="dattrs"><xsl:with-param name="f" select="'dial'"/></xsl:call-template>
                        <xsl:call-template name="dmark"/>
                        <xsl:value-of select="@dial"/>
                    </td>
                    <td style="overflow-wrap:break-word; word-break:break-word; vertical-align:top; white-space:normal">
                        <xsl:for-each select="from">
                          <xsl:call-template name="dspan"><xsl:with-param name="content">
                            <xsl:choose>
                                <!-- Coverage annotated: uses="0" → greyed out -->
                                <xsl:when test="@uses = '0'">
                                    <span class="badge cov-gl-zero" title="unused value">
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
                          </xsl:with-param></xsl:call-template>
                            <xsl:if test="position()!=last()">, </xsl:if>
                        </xsl:for-each>
                    </td>
                    <td style="overflow-wrap:break-word; word-break:break-word; vertical-align:top; white-space:normal">
                        <xsl:call-template name="dattrs"><xsl:with-param name="f" select="'to'"/></xsl:call-template>
                        <xsl:call-template name="dold"><xsl:with-param name="f" select="'to'"/></xsl:call-template>
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
