<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<xsl:output
	method="html"
	indent="yes"
	encoding="utf-8"/>

<xsl:template match="/">
	<html>
		<head>
		</head>
		<body>
			<xsl:apply-templates select=".//tableOfCorr"/>
		</body>
	</html>
</xsl:template>

<xsl:template match="tableOfCorr">
	<div>
		<h5>Macro-classes</h5>
		<div class="table-responsive">
<table class="table-sm table-striped sortable">
			<thead>
				<tr>
					<th>Class</th>
					<th>Members</th>
				</tr>
			</thead>
		<xsl:for-each select="parameters/class">
			<tr>
				<td><xsl:value-of select="@name"/></td>
				<td><xsl:value-of select="@value"/></td>
			</tr>
		</xsl:for-each>
		</table>
</div>
		<xsl:if test="parameters/canon">
			<h5>Syllable canon</h5>
			<xsl:value-of select="parameters/canon/@value"/>
		</xsl:if>
		<h5>Table of correspondences</h5>
		<div class="table-responsive">
<table class="table-sm table-bordered sets sortable">
			<thead>
				<tr>
					<th>num</th>
					<th>*</th>
					<th>syll</th>
					<th>left</th>
					<th>right</th>
					<xsl:for-each select="corr[1]/modern">
						<th><xsl:value-of select="@dialecte"/></th>
					</xsl:for-each>
				</tr>
			</thead>
			<xsl:for-each select="corr">
				<tr>
					<td><xsl:value-of select="@num"/></td>
					<td><xsl:value-of select="proto"/></td>
					<td><xsl:value-of select="proto/@syll"/></td>
					<td><xsl:value-of select="proto/@contextL"/></td>
					<td><xsl:value-of select="proto/@contextR"/></td>
					
					<xsl:for-each select="modern">
						<!-- xsl:sort select="@dialecte"/ -->
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
</div>
	</div>
</xsl:template>

</xsl:stylesheet>