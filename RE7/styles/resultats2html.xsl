<?xml version="1.0" encoding="iso-8859-1"?> 
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
	xmlns:xalan="http://xml.apache.org/xalan"
	exclude-result-prefixes="xalan"
>

<xsl:output 
	method="html" 
	indent="yes" 
	encoding="iso-8859-1"/>

<xsl:template match="/">
	<HTML>
		<HEAD>
		</HEAD>
		<BODY style="font-family:'Arial unicode MS'">
			<xsl:apply-templates select=".//actionResult"/>
		</BODY>
	</HTML>
</xsl:template>  


<xsl:template match="actionResult">
	<DIV>
		<h3>
			<xsl:for-each select="@*">
				<xsl:value-of select="local-name()"/>="<xsl:value-of select="."/>"<xsl:text> </xsl:text>
			</xsl:for-each>
		</h3>
		<xsl:for-each select="solutions">
			<xsl:sort select="id(sol/rule/@idref)/proto"/>
			<xsl:apply-templates select="."/>
		</xsl:for-each>
		<hr/>
	</DIV>
</xsl:template>

<xsl:template match="solutions">
	<DIV>
		<xsl:apply-templates select="references"/>
		<xsl:text> </xsl:text>
		<font size="1">
			<xsl:value-of select="@tokens"/>
		</font>
		<BLOCKQUOTE>
			<xsl:apply-templates select="sol"/>
		</BLOCKQUOTE>
		
	</DIV>
</xsl:template>
<xsl:template match="references">
	<xsl:for-each select="ref">
		<xsl:value-of select="id(@idref)/hw"/>
		<xsl:if test="position()!=last()">.</xsl:if>
	</xsl:for-each>
</xsl:template>
<xsl:template match="sol">
	<div>
		<xsl:variable name="to" select="ancestor::actionResult/@to"/>
		<xsl:choose>
			<xsl:when test="not($to='proto')">
				<xsl:for-each select="rule">
					<xsl:variable name="moderne" select="id(@idref)/modern[@dialecte=$to]"/>
					<xsl:if test="count(xalan:nodeset($moderne)/seg) &gt; 1">(</xsl:if>
					<xsl:for-each select="xalan:nodeset($moderne)/seg">
						<xsl:value-of select="."/>
						<xsl:if test="position() != last()">|</xsl:if>
					</xsl:for-each>
					<xsl:if test="count(xalan:nodeset($moderne)/seg) &gt; 1">)</xsl:if>

					<xsl:if test="position()!=last()">.</xsl:if>
				</xsl:for-each>
			</xsl:when>
			<xsl:otherwise>
				*<xsl:for-each select="rule">
					<xsl:value-of select="id(@idref)/proto"/>
					<xsl:if test="position()!=last()">.</xsl:if>
				</xsl:for-each>
			</xsl:otherwise>
		</xsl:choose>
		<xsl:text> </xsl:text>
		<font size="1">
			[<xsl:for-each select="rule">
				<xsl:value-of select="@idref"/>
				<xsl:if test="position()!=last()">.</xsl:if>
			</xsl:for-each>]
		</font>
	</div>
</xsl:template>
</xsl:stylesheet>
		