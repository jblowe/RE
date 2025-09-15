<?xml version="1.0" encoding="iso-8859-1"?> 
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
		xmlns="http://www.w3.org/1999/xhtml"
		xmlns:java="http://xml.apache.org/xslt/java"
 		exclude-result-prefixes="java"
		version="1.0">

<xsl:output method="xml" indent="no" encoding="utf-8" omit-xml-declaration="yes"/>
<xsl:strip-space elements="*"/> 

<xsl:template match="/">
	<html>
		<head>
			<style>
			/* Pour Mozilla: ne pas utiliser text-align: justify */
			body { 
				margin-left: 15px;
				margin-right: 15px;
				text-align:left; 
				font-family: 'Lucida sans Unicode'; 
				font-size: 12px; 
				line-height: 1.4;
			}
			.entry               { margin-left:  15px; margin-top: 15px;}
			.entry:first-letter  { margin-left: -30px;}
			.sub                 { margin-left:  15px;}
			.sub:first-letter    { margin-left: -30px;}
			.level      {font-weight:bold;}
			.hdr {
				font-size:18pt;
				text-align: center;
				font-weight:bold;
				margin-top: 24pt;
				margin-bottom: 24pt;
			}
			.hw         {font-weight:bold; font-size:13px;}
			.small      {font-size:10px;}
			.il         {font-weight:bold;}
			.nag        {font-size:12px;}
			.remark        {font-size:10px;}
			
			.ps,
			.pourcentage,
			.dollar,
			.binom,
			.langue,
			.dfn        {font-style:italic;}
			</style>
			<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
		</head>
		<body>
			<h2>Tamang-French-English-Nepali Dictionary</h2>
			<dl>
				<xsl:for-each select=".//entry">
					<div class="entry">
						<xsl:apply-templates/>
					</div>
				</xsl:for-each>
			</dl>
		</body>
	</html>
</xsl:template>

<!-- sous-entree -->
<xsl:template match="sub">
	<xsl:apply-templates select="@*"/>
	<div class="sub"><xsl:apply-templates/></div>
</xsl:template>

<!-- vedette -->
<xsl:template match="hw">
	<xsl:apply-templates select="@*"/>
	<span class="hw"><xsl:apply-templates/></span>
</xsl:template>
<xsl:template match="hwX">
	<xsl:apply-templates select="@*"/>
	<span><xsl:text>[X] </xsl:text></span>
	<span class="hw"><xsl:apply-templates/></span>
</xsl:template>
<xsl:template match="hwdialX">
	<xsl:apply-templates select="@*"/>
	<span><xsl:text>[dialX] </xsl:text></span>
	<span class="hw"><xsl:apply-templates/></span>
</xsl:template>
<xsl:template match="hwdial">
	<xsl:apply-templates select="@*"/>
	<span class="small"><xsl:text>[dial] </xsl:text></span>
	<span class="hw"><xsl:apply-templates/></span>
</xsl:template>
<xsl:template match="hdr">
	<div class="hdr"><xsl:apply-templates/></div>
</xsl:template>

<!-- partie du discours -->
<xsl:template match="ps">
	<xsl:apply-templates select="@*"/>
	<span class="ps">
		<xsl:text> , </xsl:text><xsl:apply-templates/>
		<xsl:text>, </xsl:text>
	</span>
</xsl:template>

<!-- définitions (francais, anglais, nepali) -->
<xsl:template match="dff|dfe|nag|dfn">
	<xsl:apply-templates select="@*"/>
	<xsl:choose>
		<xsl:when test="local-name(.) = 'dff'"><span class="small"><xsl:text> FR&#160;</xsl:text></span></xsl:when>
		<xsl:when test="local-name(.) = 'dfe'"><span class="small"><xsl:text> ENG </xsl:text></span></xsl:when>
		<xsl:when test="local-name(.) = 'nag'"><span class="small"><xsl:text> NEP </xsl:text></span></xsl:when>
		<xsl:otherwise><xsl:text> </xsl:text></xsl:otherwise>
	</xsl:choose>
	<span class="{local-name()}"><xsl:apply-templates/></span>
</xsl:template>

<!-- illustrations -->
<xsl:template match="il|phr">
	<xsl:apply-templates select="@*"/>
	<xsl:text> &#x2022;&#xa0;</xsl:text><xsl:apply-templates/>
</xsl:template>
<xsl:template match="il/item[1]|phr/item[1]">
	<xsl:apply-templates select="@*"/>
	<span class="il"><xsl:apply-templates/></span><xsl:text>,</xsl:text>
</xsl:template>
<xsl:template match="span">
	<xsl:text> </xsl:text>
	<xsl:apply-templates/>
	<xsl:text> </xsl:text>
</xsl:template>
<xsl:template match="item">
	<xsl:text> </xsl:text>
	<xsl:apply-templates select="@*"/>
	<span><xsl:apply-templates/></span>
</xsl:template>

<xsl:template match="*">
	<xsl:apply-templates select="@*"/>
	<xsl:variable name="localname" select="local-name()"/>
	<xsl:if test="local-name(preceding-sibling::*[1]) != $localname">
		<xsl:text> [</xsl:text>
		<span class="small"><xsl:value-of select="$localname"/>: </span>
	</xsl:if>
	<span><xsl:apply-templates/></span>
	<xsl:choose>
		<xsl:when test="local-name(following-sibling::*[1]) = $localname">
			<xsl:text>; </xsl:text>
		</xsl:when>
		<xsl:otherwise>
			<xsl:text>]</xsl:text>
		</xsl:otherwise>
	</xsl:choose>
</xsl:template>

<!-- divers -->
<xsl:template match="cf">
	<xsl:choose>
		<xsl:when test="local-name(preceding-sibling::*[1]) = 'cf'"><xsl:text>; </xsl:text></xsl:when>
		<xsl:otherwise><xsl:text> &#x2192; </xsl:text></xsl:otherwise>
	</xsl:choose>
	<span class="hw"><xsl:apply-templates/></span>
</xsl:template>
<xsl:template match="xr">
	<xsl:choose>
		<xsl:when test="local-name(preceding-sibling::*[1]) = 'xr'"><xsl:text>; </xsl:text></xsl:when>
		<xsl:otherwise><i><xsl:text> cf </xsl:text></i></xsl:otherwise>
	</xsl:choose>
	<span class="hw"><xsl:apply-templates/></span>
</xsl:template>
<xsl:template match="emp">
	<xsl:apply-templates select="@*"/>
	<xsl:text> &lt;</xsl:text>
	<span class="{local-name()}"><xsl:apply-templates/></span>
</xsl:template>

<xsl:template match="dfbot">
	<span class="small"><xsl:text> BOT </xsl:text></span>
	<xsl:apply-templates/>
</xsl:template>

<xsl:template match="dfzoo">
	<xsl:text> </xsl:text>
	<xsl:apply-templates select="@*"/>
	<span class="{local-name()}"><xsl:apply-templates/></span>
</xsl:template>
<xsl:template match="binom">
	<xsl:apply-templates select="@*"/>
	<span class="{local-name()}"><xsl:apply-templates/></span>
	<xsl:text> </xsl:text>
</xsl:template>
<xsl:template match="langue">
	<xsl:apply-templates select="@*"/>
	<span class="{local-name()}"><xsl:apply-templates/></span>
	<xsl:text> </xsl:text>
</xsl:template>
<xsl:template match="span">
	<span class="{@class}">
		<xsl:apply-templates/>
	</span>
</xsl:template>


<!-- pour mettre un numero lors de la premiere aparition d un nouveau numero -->
<xsl:template match="@level">
	<xsl:if test="not(../preceding-sibling::*[1]/@level = .)">
		<span class="level"><xsl:text> </xsl:text><xsl:value-of select="substring(., string-length(.))"/><xsl:text>.&#160;</xsl:text></span>
	</xsl:if>
</xsl:template>

<xsl:template match="text()">
	<xsl:value-of select="."/>
</xsl:template>
 
<xsl:template match="remark">
	<span class="remark"><xsl:text>&lt;</xsl:text><xsl:value-of select="."/><xsl:text>&gt;</xsl:text></span>
</xsl:template>
<xsl:template match="myref">
	<span class="remark"><xsl:text>{</xsl:text><xsl:value-of select="."/><xsl:text>}</xsl:text></span>
</xsl:template>
<!--
<xsl:template match="remark"/>
-->


</xsl:stylesheet>