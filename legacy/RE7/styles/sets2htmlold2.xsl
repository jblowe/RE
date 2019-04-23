<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
	xmlns:xalan="http://xml.apache.org/xalan"
	exclude-result-prefixes="xalan"
>

  <xsl:param name="isolates"   select="'null'"/>

  <xsl:output
      method="html"
      indent="yes"
      encoding="utf-8"/>

  <xsl:template match="/">
    <html>
      <head>
      </head>
      <body>
	<xsl:apply-templates select=".//sets"/>
      </body>
    </html>
  </xsl:template>

  <xsl:template match="sets">
    <xsl:for-each select="set">
      <table border="1">
	<tr><td>
	  <table border="1">
	    <tr>
	      <td><xsl:value-of select="id"/></td>
	      <td><xsl:value-of select="rcn"/></td>
	      <td><xsl:value-of select="pfm"/></td>
	    </tr>
	  </table>
	  <xsl:apply-templates select="sf"/>
	</td></tr>
      </table>
    </xsl:for-each>
  </xsl:template>

  <xsl:template match="sf">
    <table border="1">
      <xsl:for-each select="rfx">
	<tr>	 
	  <td><i><xsl:apply-templates select="lg"/></i></td>
	  <td><b><span><xsl:apply-templates select="lx"/></span></b></td>
	  <td><i><xsl:apply-templates select="gl"/></i></td>
	</tr>
      </xsl:for-each>
    </table>
  </xsl:template>

  <xsl:template match="gl|hw">
    <xsl:apply-templates/>
  </xsl:template>

</xsl:stylesheet>
