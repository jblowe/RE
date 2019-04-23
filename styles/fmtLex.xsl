<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<!-- xsl:param name="lg" select="'default value'"/ -->
<xsl:output
	method="xml"
	indent="yes"
	encoding="utf-8"/>
<xsl:template match="lexicon">
	<!-- lexicon dialecte="{$lg}" -->
	<lexicon>
		<xsl:attribute name="dialecte">
			<xsl:value-of select="@dialecte" />
		</xsl:attribute>
		<xsl:for-each select="entry">
			<entry>
			<xsl:attribute name="id">
				<xsl:value-of select="@id" />
  			</xsl:attribute>

			<xsl:choose>
			<xsl:when test="hw">
				<hw><xsl:value-of select="hw"/></hw>
			</xsl:when>
			<xsl:when test="mar">
				<hw><xsl:value-of select="mar"/></hw>
			</xsl:when>
			<xsl:when test="tag">
				<hw><xsl:value-of select="tag"/></hw>
			</xsl:when>
			<xsl:when test="sya">
				<hw><xsl:value-of select="sya"/></hw>
			</xsl:when>
			<xsl:otherwise>
            			<hw><xsl:value-of select="concat('hw',@N)" /></hw>
          		</xsl:otherwise>
			</xsl:choose>

			<xsl:choose>
			<xsl:when test="dfe">
				<gl><xsl:value-of select="dfe"/></gl>
			</xsl:when>
			<xsl:when test="gl">
				<gl><xsl:value-of select="gl"/></gl>
			</xsl:when>
			<xsl:when test="mode/dfe">
				<gl><xsl:value-of select="mode/dfe"/></gl>
			</xsl:when>
			<xsl:otherwise>
				<gl><xsl:value-of select="concat('gloss',@N)" /></gl>
          		</xsl:otherwise>
			</xsl:choose>

			</entry>
		</xsl:for-each>
	</lexicon>
</xsl:template>

</xsl:stylesheet>