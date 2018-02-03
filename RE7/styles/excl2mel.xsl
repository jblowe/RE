<?xml version="1.0" encoding="iso-8859-1"?> 
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
	xmlns:xalan="http://xml.apache.org/xalan"
	exclude-result-prefixes="xalan"
>
<xsl:output 
	method="xml" 
	indent="yes" 
	encoding="iso-8859-1"/>
<xsl:strip-space 
	elements="*"/>


<xsl:template match="semantics">
	<semantics>
		<xsl:variable name="mel">
			<xsl:for-each select="excl/set1[count(gl) &gt; 1]">
				<mel>
					<xsl:copy-of select="gl"/>
				</mel>
			</xsl:for-each>
			<xsl:for-each select="excl/set2[count(gl) &gt; 1]">
				<mel>
					<xsl:copy-of select="gl"/>
				</mel>
			</xsl:for-each>
		</xsl:variable>
		<xsl:for-each select="xalan:distinct(xalan:nodeset($mel)/mel)">
			<mel id="excl2mel_{position()}">
				<xsl:copy-of select="gl"/>
			</mel>
		</xsl:for-each>
	</semantics>
</xsl:template>  

</xsl:stylesheet>
		