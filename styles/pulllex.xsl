<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:param name="lg" select="'default value'"/>
<xsl:output
	method="xml"
	indent="yes"
	encoding="utf-8"/>
<xsl:template match="LEXICON">
	<lexicon dialecte="{$lg}">
		<xsl:for-each select="ENTRY">
			<entry>
			<xsl:attribute name="id">
				<xsl:value-of select="concat($lg,@N)" />
  			</xsl:attribute>
			<xsl:choose>
			<xsl:when test="DFE">
				<gl><xsl:value-of select="DFE"/></gl>
			</xsl:when>
			<xsl:when test="not(DFE) and DFF">
				<!-- gl lang="fr"><xsl:value-of select="DFF"/></gl -->
				<gl><xsl:value-of select="DFF"/></gl>
			</xsl:when>
			<xsl:when test="GL">
				<gl><xsl:value-of select="GL"/></gl>
			</xsl:when>
			<xsl:when test="MODE/DFE">
				<gl><xsl:value-of select="MODE/DFE"/></gl>
			</xsl:when>       
			<xsl:otherwise>
				<gl><xsl:value-of select="concat('gloss',@N)" /></gl>
          		</xsl:otherwise>
			</xsl:choose>

			<xsl:choose>
			<xsl:when test="HW">
				<hw><xsl:value-of select="HW"/></hw>
			</xsl:when>
			<xsl:when test="MAR">
				<hw><xsl:value-of select="MAR"/></hw>
			</xsl:when>
			<xsl:when test="TAG">
				<hw><xsl:value-of select="TAG"/></hw>
			</xsl:when>
			<xsl:when test="SYA">
				<hw><xsl:value-of select="SYA"/></hw>
			</xsl:when>
			<xsl:otherwise>
            			<hw><xsl:value-of select="concat('hw',@N)" /></hw>
          		</xsl:otherwise>

			</xsl:choose>
			</entry>
		</xsl:for-each>
	</lexicon>
</xsl:template>

</xsl:stylesheet>