<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
	xmlns:xalan="http://xml.apache.org/xalan"
	exclude-result-prefixes="xalan"
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
			<xsl:variable name="nbEntry" select="count(xalan:distinct(//lexicon/entry/@id))"/>
			<xsl:variable name="nbFind"  select="count(xalan:distinct(//actionResult[@to='proto']//references/ref/@idref))"/>
			Nb rejets: <xsl:value-of select="$nbEntry -$nbFind"/>
			<table border="1">
				<xsl:for-each select="xalan:distinct(.//actionResult[@to='proto']/@from)">
					<xsl:variable name="from" select="."/>
					<xsl:for-each select="//lexicon[@dialecte=$from]/entry">
						<xsl:if test="not(//actionResult[@to='proto'][@from=$from]//references/ref/@idref=@id)">
							<tr>
								<td><xsl:value-of select="@id"/></td>
								<td><xsl:apply-templates select="gl"/></td>
								<td><span><xsl:apply-templates select="hw"/></span></td>
							</tr>
						</xsl:if>
					</xsl:for-each>
				</xsl:for-each>
			</table>
		</body>
	</html>
</xsl:template>

</xsl:stylesheet>