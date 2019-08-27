<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

    <xsl:output
            method="html"
            indent="yes"
            encoding="utf-8"/>

    <xsl:strip-space elements="*"/>

    <xsl:template match="/">
        <html>
            <head>
            </head>
            <body>
                <p style="font-style: italic">created at: <xsl:value-of select=".//createdat"/></p>
                <h4>Summary statistics</h4>
                <xsl:apply-templates select=".//settings"/>
                <xsl:apply-templates select=".//totals" mode="summary"/>
                <xsl:apply-templates select=".//stats"/>
            </body>
        </html>
    </xsl:template>


    <xsl:template match="settings">
        <h4>Experiment settings</h4>
        <xsl:apply-templates select=".//settings"/>
    </xsl:template>

    <xsl:template match="stats">
        <h4>Language statistics</h4>
        <xsl:apply-templates select=".//stats"/>
    </xsl:template>

    <xsl:template match="totals" mode="summary">
        <table class="table table-striped sortable sticky-top">
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

  <xsl:key name="elements" match="lexicons/lexicon/*" use="name()"/>
  <xsl:key name="subtotals" match="totals/*" use="name()"/>

    <xsl:template match="stats">
        <table class="table table-striped sortable sticky-top">
            <thead>
              <tr>
                  <th>language</th>
                <xsl:for-each select="//*[generate-id(.)=generate-id(key('elements',name())[1])]">
                  <!-- xsl:sort select="name()"/ -->
                  <xsl:for-each select="key('elements', name())">
                    <xsl:if test="position()=1">
                      <th><xsl:value-of select="name()"/></th>
                    </xsl:if>
                  </xsl:for-each>
                </xsl:for-each>
              </tr>
            </thead>
            <xsl:apply-templates select="lexicons/lexicon"/>
            <tr>
              <th>totals</th>
                <xsl:for-each select="//*[generate-id(.)=generate-id(key('elements',name())[1])]">
                  <!-- xsl:sort select="name()"/ -->
                  <xsl:for-each select="key('subtotals', name())">
                    <xsl:if test="position()=1">
                      <th><xsl:value-of select ="@value"/></th>
                    </xsl:if>
                  </xsl:for-each>
                </xsl:for-each>
            </tr>
        </table>

        <table class="table table-striped sortable sticky-top">
            <thead>
              <tr>
                  <th>correspondence</th>
                  <th>in reconstructions</th>
                  <th>in sets</th>
              </tr>
            </thead>
            <tbody>
                <xsl:apply-templates select="correspondences/correspondence"/>
            </tbody>
        </table>
        <p>correspondences_used: <xsl:value-of select=".//correspondences_used[@value]"/></p>
    </xsl:template>


    <xsl:template match="settings">
        <table class="table table-striped sortable sticky-top">
            <thead>
              <tr>
                  <th>Setting</th>
                  <th>Value</th>
              </tr>
            </thead>
            <tbody>
                <xsl:apply-templates select="parm"/>
            </tbody>
        </table>
    </xsl:template>


    <xsl:template match="correspondences/correspondence">
        <tr>
            <td><xsl:value-of select="@value"/></td>
            <xsl:for-each select="./*">
                <td><xsl:value-of select ="@value"/></td>
            </xsl:for-each>
        </tr>
    </xsl:template>

    <xsl:template match="parm">
        <tr>
            <td><xsl:value-of select="@key"/></td>
            <td><xsl:value-of select="@value"/></td>
        </tr>
    </xsl:template>

    <xsl:template match="lexicons/lexicon">
        <tr>
            <td>
                <xsl:value-of select="@language"/>
            </td>
            <xsl:for-each select="./*">
                <td><xsl:value-of select ="@value"/></td>
            </xsl:for-each>
        </tr>
    </xsl:template>


    <xsl:template match="totals" mode="bottom">
        <tr>
            <td>
                Totals
            </td>
            <xsl:for-each select="./*">
                <td><xsl:value-of select ="@value"/></td>
            </xsl:for-each>
        </tr>
    </xsl:template>

    <xsl:template match="*[@type = 'string']">
        <xsl:value-of select='@value'/>
    </xsl:template>
    <xsl:template match="*[@type = 'float']">
        <xsl:value-of select='format-number(@value, "##.###")'/>
    </xsl:template>
    <xsl:template match="*[@type = 'integer']">
        <xsl:value-of select='format-number(@value, "###,###")'/>
    </xsl:template>

</xsl:stylesheet>
		