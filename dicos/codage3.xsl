<?xml version="1.0" encoding="iso-8859-1"?> 
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
		xmlns:java="http://xml.apache.org/xslt/java"
 		exclude-result-prefixes="java"
		version="1.0">

<xsl:output 
	method="xml" 
	indent="yes" 
	encoding="utf-8"/>

<xsl:strip-space elements="*"/>

<!-- les regles par default pour les elements, les textes et les attributs -->
<xsl:template match="*">
	<xsl:variable name="tag" select="name()"/>
	<xsl:variable name="ns" select="namespace-uri()"/>
	<xsl:element name="{$tag}" namespace="{$ns}">
		<xsl:for-each select="@*">
			<xsl:apply-templates select="."/>
		</xsl:for-each>
		<xsl:apply-templates/>
	</xsl:element>
</xsl:template>
<xsl:template match="processing-instruction()">
	<xsl:copy-of select="."/>
</xsl:template>
<xsl:template match="comment()">
	<xsl:copy-of select="."/>
</xsl:template>
<xsl:template match="@*">
	<xsl:if test="not(.='')"><xsl:copy-of select="."/></xsl:if>
</xsl:template>

<!-- les regles specifiques -->

<xsl:template match="*[.='']"/>

<xsl:template match="binom/text()|dfbot/text()|dfbotX/text()|dfe/text()|dfeold/text()|dff/text()|dffold/text()|dfi/text()|dfie/text()|dfn/text()|dfnX/text()|dfnold/text()|dfsem/text()|dfzoo/text()|dfeX/text()|dffX/text()|remark/text()">
	<!-- <xsl:variable name="str"        select="java:java.lang.String.new(.)"/>
	<xsl:variable name="str"        select="java:replaceAll($str, '&lt;[^&lt;&gt;]*&gt;', '')"/>
	<xsl:value-of                   select="translate($str,'*', '')"/> -->
	<xsl:value-of                   select="translate(.,'*', '')"/>
</xsl:template>
<xsl:template match="span[@class='slash']">
	<xsl:apply-templates/>
</xsl:template>
<xsl:template match="*/item[1]/text()|span[not(@class='pourcentage')]/text()|hdr/text()|hw/text()|il/text()|phr/text()|xr/text()|cf/text()|hwdial/text()|hwX/text()|hwdialX/text()|var/text()|dial/text()|old/text()|comp/text()">
	<xsl:variable name="str"        select="java:java.lang.String.new(translate(.,'012345:AEONT', '&#x2070;¹²³&#x2074;&#x2075;&#x02d0;&#x0259;&#x025b;&#x0254;&#x014b;&#x0288;'))"/>
	<xsl:variable name="str"        select="java:replaceAll($str, 'ng', '&#x014b;')"/>
	<xsl:variable name="str"        select="java:replaceAll($str, 'aM', 'a&#x0303;')"/>
	<xsl:variable name="str"        select="java:replaceAll($str, 'eM', 'e&#x0303;')"/>
	<xsl:variable name="str"        select="java:replaceAll($str, 'iM', 'i&#x0303;')"/>
	<xsl:variable name="str"        select="java:replaceAll($str, 'oM', 'o&#x0303;')"/>
	<xsl:variable name="str"        select="java:replaceAll($str, 'uM', 'u&#x0303;')"/>
	<xsl:variable name="str"        select="java:replaceAll($str, 'ph', 'p&#x02b0;')"/>
	<xsl:variable name="str"        select="java:replaceAll($str, 'th', 't&#x02b0;')"/>
	<xsl:variable name="str"        select="java:replaceAll($str, 'ch', 'c&#x02b0;')"/>
	<xsl:variable name="str"        select="java:replaceAll($str, 'kh', 'k&#x02b0;')"/>
	<xsl:variable name="str"        select="java:replaceAll($str, '&#x0288;h', '&#x0288;&#x02b0;')"/>
	<!-- <xsl:variable name="str"        select="java:replaceAll($str, '&lt;[^&lt;&gt;]*&gt;', '')"/> -->
	<xsl:value-of select="$str"/>
</xsl:template>
<xsl:template match="text()">
	<!-- <xsl:variable name="str"        select="java:java.lang.String.new(.)"/>
	<xsl:variable name="newStr"     select="java:replaceAll($str, '&lt;[^&lt;&gt;]*&gt;', '')"/>
	<xsl:value-of select="$newStr"/> -->
	<xsl:value-of select="."/>
</xsl:template>
</xsl:stylesheet>
