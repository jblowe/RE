<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
	xmlns:xalan="http://xml.apache.org/xalan"
	exclude-result-prefixes="xalan"
>
<!--
     *** Liste tous les ensembles:
     ***    si tous les mots ont la meme glose: n'affiche que le ou les plus gros ensemble et sous ensembles
     ***    sinon affiche tous les sous ensembles
-->
	
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
	Nb sets: <xsl:value-of select="count(set[not(@isolat='true')])"/>
	<xsl:for-each select="set[not(@isolat='true')]">
		<xsl:variable name="countWord" select="count(word)"/>
		<hr>
			<xsl:for-each select="sol">
				<pre>
					<xsl:for-each select="rule">
						<xsl:variable name="corr" select="@idref"/>	
						<xsl:value-of select="/sets/tableOfCorr/corr[@num=$corr]/proto"/>
					</xsl:for-each>
					<xsl:text>/</xsl:text>
					<xsl:for-each select="rule"><xsl:value-of select="@idref"/><xsl:if test="position()!=last()">.</xsl:if></xsl:for-each>

					<xsl:text>[</xsl:text>
					<xsl:for-each select="../word">
						<xsl:value-of select="entry/@id"/><xsl:if test="position()!=last()">,</xsl:if>
					</xsl:for-each>
					<xsl:text>]</xsl:text>

					<!--
					***
					*** si tout les mots ont la meme glose
					*** ne lister que les ens de meme taille
					*** -->
					<xsl:choose>
						<!-- *** tout les mots n ont pas la meme glose *** -->
						<xsl:when test="count(xalan:distinct(../word//gl))&gt;1">
							<xsl:for-each select="..//set">
								<br/>
								<xsl:for-each select="sol/rule">
									<xsl:variable name="corr" select="@idref"/>	
									<xsl:value-of select="/sets/tableOfCorr/corr[@num=$corr]/proto"/>
								</xsl:for-each>
								<xsl:text>/</xsl:text>
								<xsl:for-each select="sol/rule"><xsl:value-of select="@idref"/><xsl:if test="position()!=last()">.</xsl:if></xsl:for-each>
								<xsl:text>[</xsl:text>
								<xsl:for-each select="word">
									<xsl:value-of select="entry/@id"/><xsl:if test="position()!=last()">,</xsl:if>
								</xsl:for-each>
								<xsl:text>]</xsl:text>
							</xsl:for-each>
						</xsl:when>
						<xsl:otherwise>
							<!-- *** que les ensemble qui comprennent tous les elements *** -->
							<xsl:for-each select="..//set">
								<xsl:variable name="countW" select="count(word)"/>
								<xsl:for-each select="sol">
									<xsl:if test="count(../word)=$countWord">
										<br/>
										<xsl:for-each select="rule">
											<xsl:variable name="corr" select="@idref"/>
											<xsl:value-of select="/sets/tableOfCorr/corr[@num=$corr]/proto"/>
										</xsl:for-each>
										<xsl:text>/</xsl:text>
										<xsl:for-each select="rule"><xsl:value-of select="@idref"/><xsl:if test="position()!=last()">.</xsl:if></xsl:for-each>
										<xsl:text>[</xsl:text>
										<xsl:for-each select="../word">
											<xsl:value-of select="entry/@id"/><xsl:if test="position()!=last()">,</xsl:if>
										</xsl:for-each>
										<xsl:text>]</xsl:text>
									</xsl:if>
								</xsl:for-each>
							</xsl:for-each>
						</xsl:otherwise>
					</xsl:choose>

					<table>
						<xsl:for-each select="../word">
							<tr><td><xsl:value-of select="entry/@id"/></td><td><xsl:value-of select="entry/hw"/></td><td><xsl:value-of select="entry/gl"/></td></tr>
						</xsl:for-each>
					</table>
</div>
				</pre>
			</xsl:for-each>
		</hr>
	</xsl:for-each>
</xsl:template>

</xsl:stylesheet>
		