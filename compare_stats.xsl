<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output
	method="xml"
	indent="yes"
	encoding="utf-8"/>


  <xsl:template match="/">
    <stats>
        <xsl:for-each select="files/file">
          <xsl:value-of select="."/>
          <xsl:copy-of select="document(.)/*"/>
        </xsl:for-each>
    </stats>
  </xsl:template>

  <xsl:template match="*">
    <xsl:apply-templates select="totals"/>
    <xsl:apply-templates select="lexicon"/>
  </xsl:template>

  <xsl:template match="totals">
    <xsl:for-each select=".">
        <xsl:copy-of select="."/>
    </xsl:for-each>
  </xsl:template>

  <xsl:template match="lexicon">
    <xsl:for-each select=".">
        <xsl:copy-of select="."/>
    </xsl:for-each>
  </xsl:template>

</xsl:stylesheet>