<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<xsl:output
	method="html"
	indent="yes"
	encoding="utf-8"/>

<xsl:template match="/">
	<xsl:apply-templates select=".//tableOfCorr"/>
</xsl:template>

<xsl:template match="tableOfCorr">
	<div>
		<!-- Scoped styles for compact column widths in the correspondence table.
		     Must live in the body fragment (head is stripped by xml_to_html). -->
		<style>
			/* Tighter cell padding for the correspondence table */
			.toc-view-table td, .toc-view-table th { padding: .15rem .3rem !important; font-size: 0.8rem; }
			/* Column 1 = num, 3 = syll: very narrow */
			.toc-view-table th:nth-child(1), .toc-view-table td:nth-child(1) { width: 3ch; }
			.toc-view-table th:nth-child(3), .toc-view-table td:nth-child(3) { width: 4ch; }
			/* Columns 4-5 = left / right context */
			.toc-view-table th:nth-child(4), .toc-view-table td:nth-child(4),
			.toc-view-table th:nth-child(5), .toc-view-table td:nth-child(5) { width: 5ch; }
			/* Columns 6+ = dialect forms */
			.toc-view-table th:nth-child(n+6), .toc-view-table td:nth-child(n+6) { width: 5ch; }
		</style>
		<h6>Parameters</h6>
		<table class="table table-sm table-striped">
		<xsl:if test="parameters/canon">
			<tr>
				<td><b>Syllable canon</b></td>
				<td class="col-gloss">
					<xsl:value-of select="parameters/canon/@value"/>
				</td>
			</tr>
		</xsl:if>
		<xsl:if test="parameters/context_match_type">
			<tr>
				<td><b>Context match type</b></td>
				<td class="col-gloss">
					<xsl:value-of select="parameters/context_match_type/@value"/>
				</td>
			</tr>
		</xsl:if>
		</table>
		<p/>
		<h6>Macro-classes (used in Contexts)</h6>
		<div>
		<table class="table table-sm table-striped sortable">
			<thead>
				<tr>
					<th>Class</th>
					<th>Members</th>
				</tr>
			</thead>
		<xsl:for-each select="parameters/class">
			<tr>
				<td><xsl:value-of select="@name"/></td>
				<td class="col-gloss"><xsl:value-of select="@value"/></td>
			</tr>
		</xsl:for-each>
		</table>
		</div>
		<h6>Table of correspondences</h6>
		<div>
		<table class="table table-sm table-hover table-striped table-bordered sets sortable toc-view-table">
			<thead class="sticky-top top-0">
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
					
					<!-- Iterate over the CANONICAL column list so that missing
					 <modern> elements produce an empty cell in the correct
					 column rather than shifting subsequent cells left. -->
					<xsl:variable name="this-corr" select="."/>
					<xsl:for-each select="../corr[1]/modern">
						<xsl:variable name="d"    select="@dialecte"/>
						<xsl:variable name="cell" select="$this-corr/modern[@dialecte = $d]"/>
						<td>
							<xsl:for-each select="$cell/seg">
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
		    <h5>Rules</h5>
		<div>
		<table class="table table-sm table-hover table-bordered sets sortable">
			<thead class="sticky-top top-0">
				<tr>
					<th>num</th>
					<th>input</th>
					<th>output</th>
					<th>contextL</th>
					<th>contextR</th>
					<th>stage</th>
					<th>language</th>
				</tr>
			</thead>
			<xsl:for-each select="rule">
				<tr>
					<td><xsl:value-of select="@num"/></td>
					<td><xsl:value-of select="input"/></td>
					<td><xsl:value-of select="outcome"/></td>
					<td><xsl:value-of select="input/@contextL"/></td>
					<td><xsl:value-of select="input/@contextR"/></td>
					<td><xsl:value-of select="@stage"/></td>
					<td><xsl:value-of select="outcome/@languages"/></td>
				</tr>
			</xsl:for-each>
		</table>
		</div>
	</div>
</xsl:template>

</xsl:stylesheet>