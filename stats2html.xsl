<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
                xmlns:ext="http://exslt.org/common"
>

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
                <p style="font-style: italic">created at: <xsl:value-of select=".//createdat"/></p>
                <h4>Summary statistics</h4>
                <xsl:apply-templates select=".//totals" mode="summary"/>
                <h4>Language statistics</h4>
                <xsl:apply-templates select=".//stats"/>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="totals" mode="summary">
        <table class="table table-striped sortable">
            <thead>
                <tr>
                    <th>Stat</th>
                    <th>Value</th>
                </tr>
            </thead>
            <xsl:for-each select="./*">
                <tr>
                    <td><xsl:value-of select ="name(.)"/></td>
                    <td><xsl:value-of select='format-number(@value, "###,###")' /></td>
                </tr>
            </xsl:for-each>
        </table>
    </xsl:template>

  <xsl:key name="elements" match="lexicon/*" use="name()"/>
  <xsl:key name="subtotals" match="totals/*" use="name()"/>

    <xsl:template match="stats">
        <table class="table table-striped sortable">
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
            <xsl:apply-templates select="lexicon"/>
            <tr>
              <th>totals</th>

                <xsl:for-each select="//*[generate-id(.)=generate-id(key('elements',name())[1])]">
                  <!-- xsl:sort select="name()"/ -->
                  <xsl:for-each select="key('subtotals', name())">
                    <xsl:if test="position()=1">
                      <th><xsl:value-of select='format-number(@value, "###,###")'/></th>
                    </xsl:if>
                  </xsl:for-each>
                </xsl:for-each>
            </tr>
        </table>
    </xsl:template>


    <xsl:template match="lexicon">
        <tr>
            <td>
                <xsl:value-of select="@language"/>
            </td>
            <xsl:for-each select="./*">
                <td><xsl:value-of select='format-number(./@value, "###,###")' /></td>
            </xsl:for-each>
        </tr>
    </xsl:template>


    <xsl:template match="lexicon">
        <tr>
            <td>
                <xsl:value-of select="@language"/>
            </td>
            <xsl:for-each select="./*">
                <td><xsl:value-of select='format-number(./@value, "###,###")' /></td>
            </xsl:for-each>
        </tr>
    </xsl:template>

    <xsl:template match="totals" mode="bottom">
        <tr>
            <td>
                Totals
            </td>
            <xsl:for-each select="./*">
                <td><xsl:value-of select='format-number(./@value, "###,###")' /></td>
            </xsl:for-each>
        </tr>
    </xsl:template>



  <xsl:template match="xxx">
      <tr>
        <xsl:for-each select="//*[generate-id(.)=generate-id(key('elements',name())[1])]">
          <!-- xsl:sort select="name()"/ -->
          <xsl:for-each select="key('elements', name())">
            <xsl:if test="position()=1">
              <th><xsl:value-of select="name()"/></th>
            </xsl:if>
          </xsl:for-each>
        </xsl:for-each>
      </tr>
  </xsl:template>


</xsl:stylesheet>
		