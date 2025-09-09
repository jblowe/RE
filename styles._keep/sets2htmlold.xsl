<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
	xmlns:xalan="http://xml.apache.org/xalan"
	exclude-result-prefixes="xalan"
>

<xsl:param name="isolats"   select="'null'"/>

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
	Nb sets: <xsl:value-of select="count(xalan:distinct(set[@isolat=$isolats]))"/>
	<div class="table-responsive">
<table border="1">
		<xsl:for-each select="set[@isolat=$isolats]">
			<tr>
				<td><xsl:value-of select="@analysis"/></td>
				<xsl:for-each select=".//word">
					<xsl:sort select="../@dialecte"/>
					<xsl:for-each select="entry">
						<td>
							<nobr>
								<span><xsl:apply-templates select="hw"/></span>
								(<xsl:apply-templates select="gl"/>)
								<i><xsl:apply-templates select="../@dialecte"/></i>
							</nobr>
						</td>
					</xsl:for-each>
				</xsl:for-each>
			</tr>
		</xsl:for-each>
	</table>
</div>
</xsl:template>

<xsl:template match="gl|hw">
	<xsl:apply-templates/>
</xsl:template>

</xsl:stylesheet>
		