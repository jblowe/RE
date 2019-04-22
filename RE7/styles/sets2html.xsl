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
	<link rel="stylesheet" type="text/css" href="/static/reconengine.css"/>
      </head>
      <body>
	<xsl:apply-templates select=".//sets"/>
      </body>
    </html>
  </xsl:template>

  <xsl:template match="sets">
    <xsl:for-each select="set">
      <table id="set">
	<tr><td>
	  <table id="row">
	    <tr>
	      <td id="id"><xsl:value-of select="id"/></td>
	      <td id="pfm"><xsl:value-of select="pfm"/></td>
	      <td id="pgl"><xsl:value-of select="pgl"/></td>
	      <td id="rcn">[<xsl:value-of select="rcn"/>]</td>
	    </tr>
	  </table>
	  <xsl:apply-templates select="sf"/>
	</td></tr>
      </table>
    </xsl:for-each>
  </xsl:template>

  <xsl:template match="sf">
    <table id="sf">
      <xsl:for-each select="rfx">
	<tr>	 
	  <td id="lg"><xsl:apply-templates select="lg"/></td>
	  <td id="lx"><xsl:apply-templates select="lx"/></td>
	  <td id="gl"><xsl:apply-templates select="gl"/></td>
	  <td id="nn">[<xsl:apply-templates select="rn"/>:<xsl:apply-templates select="hn"/>]</td>
	</tr>
      </xsl:for-each>
    </table>
  </xsl:template>

  <xsl:template match="gl|hw">
    <xsl:apply-templates/>
  </xsl:template>

</xsl:stylesheet>
