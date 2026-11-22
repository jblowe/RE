<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

    <xsl:output
            method="html"
            indent="yes"
            encoding="utf-8"/>

    <!-- diff marks for the Browse pane's "Compare local with an earlier commit";
         no effect on a file that has no diff annotations -->
    <xsl:include href="diff-common.xsl"/>

    <xsl:template match="/">
        <div>
            <div style="float: left; width:60px;">
                <b>n =
                    <xsl:value-of select="count(lexicon/entry[not(@diff = 'deleted')])"/>
                </b>
            </div>
            <div style="float: left; width:300px;">
                <i>created at:
                    <xsl:value-of select=".//createdat"/>
                </i>
            </div>
            <div style="clear:both;"></div>
            <xsl:apply-templates select=".//lexicon"/>
        </div>
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
                        <xsl:call-template name="rowclass"/>
                        <td>
                            <xsl:call-template name="dattrs"><xsl:with-param name="f" select="'hw'"/></xsl:call-template>
                            <xsl:call-template name="dmark"/>
                            <xsl:call-template name="dold"><xsl:with-param name="f" select="'hw'"/></xsl:call-template>
                            <xsl:apply-templates select="hw"/>
                        </td>
                        <td>
                            <xsl:call-template name="dattrs"><xsl:with-param name="f" select="'gl'"/></xsl:call-template>
                            <xsl:call-template name="dold"><xsl:with-param name="f" select="'gl'"/></xsl:call-template>
                            <xsl:for-each select="gl">
                                <i><xsl:value-of select="." /></i>
                                <xsl:if test="position() != last()">, </xsl:if>
                            </xsl:for-each>
                        </td>
                        <td>
                            <xsl:call-template name="dattrs"><xsl:with-param name="f" select="'ngl'"/></xsl:call-template>
                            <xsl:call-template name="dold"><xsl:with-param name="f" select="'ngl'"/></xsl:call-template>
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
