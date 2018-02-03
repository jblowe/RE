<?xml version="1.0" encoding="iso-8859-1"?> 
<xsl:stylesheet 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
	version="1.0"
    xmlns:redirect="org.apache.xalan.xslt.extensions.Redirect"
    extension-element-prefixes="redirect">

<xsl:param name="projectName"   select="'aaa'"/>

<xsl:output 
	method="html" 
	indent="yes" 
	encoding="iso-8859-1"/>

<xsl:template match="/">
	<redirect:write file="blank.htm">
		<HTML>
			<HEAD/>
			<BODY/>
		</HTML>
	</redirect:write>
	<redirect:write file="{$projectName}.index.htm">
		<HTML>
			<HEAD/>
			<frameset cols="250,*" Frameborder="Yes" FRAMESPACING="2">
				<frame SRC="{$projectName}.cmds.htm" name="cmds"/>
				<frame SRC="blank.htm" name="content"/>
			</frameset>
		</HTML>
	</redirect:write>
	<redirect:write file="{$projectName}.cmds.htm">
		<HTML>
			<HEAD/>
			<BODY>
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
			</BODY>
		</HTML>
	</redirect:write>
	<HTML>
		<HEAD>
		</HEAD>
		<BODY>
			<h3>Lexiques</h3>
			<ul>
				<xsl:for-each select=".//lexicon">
					<li><a href="#{@dialecte}"><xsl:value-of select="@dialecte"/></a></li>
				</xsl:for-each>
			</ul>
			<xsl:apply-templates select=".//lexicon"/>
		</BODY>
	</HTML>
</xsl:template>  


<xsl:template match="lexicon">
	<DIV>
		<a name="{@dialecte}"/>
		<h3><xsl:value-of select="@dialecte"/></h3>
		<table border="1" style="font-family:'Arial unicode MS'">
			<xsl:for-each select="entry">
				<tr>
					<td><xsl:apply-templates select="@id"/></td>
					<xsl:apply-templates select="gl"/>
					<xsl:apply-templates select="hw"/>
				</tr>
			</xsl:for-each>
		</table>
	</DIV>
</xsl:template>

<xsl:template match="gl|hw">
	<td>
		<xsl:apply-templates/>
	</td>
</xsl:template>

</xsl:stylesheet>
		