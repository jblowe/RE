<?xml version="1.0" encoding="iso-8859-1"?> 
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<xsl:output 
	method="html" 
	indent="yes" 
	encoding="iso-8859-1"/>

<xsl:template match="/">
	<HTML>
		<HEAD>
		</HEAD>
		<BODY>
			<xsl:apply-templates select=".//tableOfCorr"/>
		</BODY>
	</HTML>
</xsl:template>  

<xsl:template match="tableOfCorr">
	<DIV>
		<h3>Macro-classes</h3>
		<xsl:for-each select="parameters/class">
			<div style="font-family:'Arial unicode MS'">
				<xsl:value-of select="@name"/>: <xsl:value-of select="@value"/>
			</div>
		</xsl:for-each>
		<h3>Table des correspondances</h3>
		<table border="1" style="font-family:'Arial unicode MS'">
			<tr>
				<th>num</th>
				<th>*</th>
				<th>syll</th>
				<th>left</th>
				<th>right</th>

				<xsl:for-each select="corr[1]/modern">
					<xsl:sort select="@dialecte"/>
					<th><xsl:value-of select="@dialecte"/></th>
				</xsl:for-each>
			</tr>
			<xsl:for-each select="corr">
				<tr>
					<td><xsl:value-of select="@num"/></td>
					<td><xsl:value-of select="proto"/></td>
					<td><xsl:value-of select="proto/@syll"/></td>
					<td><xsl:value-of select="proto/@contextL"/></td>
					<td><xsl:value-of select="proto/@contextR"/></td>
					
					<xsl:for-each select="modern">
						<xsl:sort select="@dialecte"/>
						<td>
							<xsl:for-each select="seg">
								<xsl:if test="@statut='doute'">=</xsl:if>
								<xsl:value-of select="."/>
								<xsl:if test="(position()!=last()) or (@statut!='doute')">,</xsl:if>
							</xsl:for-each>
						</td>
					</xsl:for-each>
				</tr>
			</xsl:for-each>
		</table>
	</DIV>
</xsl:template>

</xsl:stylesheet>