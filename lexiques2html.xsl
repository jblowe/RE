<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	version="1.0"
    xmlns:redirect="org.apache.xalan.xslt.extensions.Redirect"
    extension-element-prefixes="redirect">

<xsl:param name="projectName"   select="'aaa'"/>

<xsl:output
	method="html"
	indent="yes"
	encoding="utf-8"/>

<xsl:template match="/">
	<redirect:write file="blank.htm">
		<html>
			<head/>
			<body/>
		</html>
	</redirect:write>
	<redirect:write file="{$projectName}.index.htm">
		<html>
			<head/>
			<frameset cols="250,*" Frameborder="Yes" FRAMESPACING="2">
				<frame SRC="{$projectName}.cmds.htm" name="cmds"/>
				<frame SRC="blank.htm" name="content"/>
			</frameset>
		</html>
	</redirect:write>
	<redirect:write file="{$projectName}.cmds.htm">
		<html>
			<head/>
			<body>
				<ul>
					<li><a href="{$projectName}.lexiques.htm"    target="content">Lexiques</a></li>
					<li><a href="{$projectName}.toc.htm"         target="content">Table des correspondances</a></li>
					<li><a href="{$projectName}.params.htm"      target="content">Parametres</a></li>
					<li><a href="{$projectName}.resultats.htm"   target="content">Résultats</a></li>
					<li><a href="{$projectName}.rejets.htm"      target="content">Rejets</a></li>
					<li><a href="{$projectName}.isolats.htm"     target="content">Isolats</a></li>
					<li><a href="{$projectName}.sets.htm"        target="content">Sets</a></li>
					<li><a href="{$projectName}.supersets.htm"   target="content">Super sets</a></li>
					<li><a href="{$projectName}.afterMel.htm"    target="content">Sets apres MEL</a></li>
					<li><a href="{$projectName}.isolatsMel.htm"  target="content">Isolats apres MEL</a></li>
					<li><a href="{$projectName}.afterExcl.htm"   target="content">Sets apres EXCL</a></li>
					<li><a href="{$projectName}.isolatsExcl.htm" target="content">Isolats apres EXCL</a></li>
				</ul>
			</body>
		</html>
	</redirect:write>
	<html>
		<head>
		</head>
		<body>
			<h4>Lexiques</h4>
			<ul>
				<xsl:for-each select=".//lexicon">
					<li><a href="#{@dialecte}"><xsl:value-of select="@dialecte"/></a></li>
				</xsl:for-each>
			</ul>
			<xsl:apply-templates select=".//lexicon"/>
		</body>
	</html>
</xsl:template>


<xsl:template match="lexicon">
	<div>
		<a name="{@dialecte}"/>
		<h4><xsl:value-of select="@dialecte"/></h4>
		<div class="table-responsive">
<table border="1">
			<xsl:for-each select="entry">
				<tr>
					<td><xsl:apply-templates select="@id"/></td>
					<xsl:apply-templates select="gl"/>
					<xsl:apply-templates select="hw"/>
				</tr>
			</xsl:for-each>
		</table>
</div>
	</div>
</xsl:template>

<xsl:template match="gl|hw">
	<td>
		<xsl:apply-templates/>
	</td>
</xsl:template>

</xsl:stylesheet>
		