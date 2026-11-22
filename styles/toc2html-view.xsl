<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<xsl:output
	method="html"
	indent="yes"
	encoding="utf-8"/>

<xsl:include href="diff-common.xsl"/>

<xsl:template match="/">
	<xsl:apply-templates select=".//tableOfCorr"/>
</xsl:template>

<xsl:template match="tableOfCorr">
	<xsl:variable name="uid" select="generate-id(.)"/>
	<!-- diff mode: a section with a difference starts open; the table has a
	     column for every dialect in either version -->
	<xsl:variable name="open-controls" select="boolean(parameters/*[@diff][not(self::class)])"/>
	<xsl:variable name="open-classes"  select="boolean(parameters/class[@diff])"/>
	<xsl:variable name="open-toc"      select="boolean(corr[@diff])"/>
	<xsl:variable name="open-rules"    select="boolean(rule[@diff])"/>
	<xsl:variable name="open-quirks"   select="boolean(quirk[@diff])"/>
	<xsl:variable name="cols" select="diff_dialects/d | corr[not(../diff_dialects)][1]/modern"/>
	<div>

		<!-- ── Controls ─────────────────────────────────────────────────────── -->
		<button type="button" data-bs-toggle="collapse" data-bs-target="#{$uid}-controls">
			<xsl:attribute name="class">params-sec-hdr<xsl:if test="not($open-controls)"> collapsed</xsl:if></xsl:attribute>
			<xsl:attribute name="aria-expanded"><xsl:value-of select="$open-controls"/></xsl:attribute>Controls</button>
		<div id="{$uid}-controls">
			<xsl:attribute name="class">collapse<xsl:if test="$open-controls"> show</xsl:if></xsl:attribute>
			<table class="table table-sm table-striped">
				<xsl:for-each select="parameters/canon[1]">
					<tr>
						<xsl:call-template name="rowclass"/>
						<td><b>Syllable canon</b></td>
						<xsl:call-template name="dcell">
							<xsl:with-param name="row" select="."/>
							<xsl:with-param name="f" select="'value'"/>
							<xsl:with-param name="val" select="string(@value)"/>
						</xsl:call-template>
					</tr>
				</xsl:for-each>
				<xsl:for-each select="parameters/spec[1]">
					<tr>
						<xsl:call-template name="rowclass"/>
						<td><b>Supra-segmentals</b></td>
						<xsl:call-template name="dcell">
							<xsl:with-param name="row" select="."/>
							<xsl:with-param name="f" select="'value'"/>
							<xsl:with-param name="val" select="string(@value)"/>
						</xsl:call-template>
					</tr>
				</xsl:for-each>
				<xsl:for-each select="parameters/context_match_type[1]">
					<tr>
						<xsl:call-template name="rowclass"/>
						<td><b>Context match type</b></td>
						<xsl:call-template name="dcell">
							<xsl:with-param name="row" select="."/>
							<xsl:with-param name="f" select="'value'"/>
							<xsl:with-param name="val" select="string(@value)"/>
						</xsl:call-template>
					</tr>
				</xsl:for-each>
			</table>
		</div>

		<!-- ── Classes ──────────────────────────────────────────────────────── -->
		<button type="button" data-bs-toggle="collapse" data-bs-target="#{$uid}-classes">
			<xsl:attribute name="class">params-sec-hdr<xsl:if test="not($open-classes)"> collapsed</xsl:if></xsl:attribute>
			<xsl:attribute name="aria-expanded"><xsl:value-of select="$open-classes"/></xsl:attribute>Classes</button>
		<div id="{$uid}-classes">
			<xsl:attribute name="class">collapse<xsl:if test="$open-classes"> show</xsl:if></xsl:attribute>
			<table class="table table-sm table-striped sortable toc-classes-table">
				<thead>
					<tr>
						<th>Class</th>
						<th>Members</th>
					</tr>
				</thead>
				<xsl:for-each select="parameters/class">
					<tr>
						<xsl:call-template name="rowclass"/>
						<xsl:call-template name="dcell">
							<xsl:with-param name="row" select="."/>
							<xsl:with-param name="f" select="'name'"/>
							<xsl:with-param name="val" select="string(@name)"/>
							<xsl:with-param name="mark" select="true()"/>
						</xsl:call-template>
						<xsl:call-template name="dcell">
							<xsl:with-param name="row" select="."/>
							<xsl:with-param name="f" select="'value'"/>
							<xsl:with-param name="val" select="string(@value)"/>
						</xsl:call-template>
					</tr>
				</xsl:for-each>
			</table>
		</div>

		<!-- ── Table of correspondences ─────────────────────────────────────── -->
		<button type="button" data-bs-toggle="collapse" data-bs-target="#{$uid}-toc">
			<xsl:attribute name="class">params-sec-hdr<xsl:if test="not($open-toc)"> collapsed</xsl:if></xsl:attribute>
			<xsl:attribute name="aria-expanded"><xsl:value-of select="$open-toc"/></xsl:attribute>Table of correspondences</button>
		<div id="{$uid}-toc">
			<xsl:attribute name="class">collapse<xsl:if test="$open-toc"> show</xsl:if></xsl:attribute>
			<table class="table table-sm table-hover table-striped table-bordered sets sortable toc-view-table">
				<thead>
					<tr>
						<th>num</th>
						<th>*</th>
						<th>syll</th>
						<th>left</th>
						<th>right</th>
						<xsl:for-each select="$cols">
							<th><xsl:value-of select="@dialecte"/></th>
						</xsl:for-each>
					</tr>
				</thead>
				<xsl:for-each select="corr">
					<tr id="toc-corr-{@num}">
						<xsl:call-template name="rowclass"/>
						<xsl:call-template name="dcell">
							<xsl:with-param name="row" select="."/>
							<xsl:with-param name="f" select="'num'"/>
							<xsl:with-param name="val" select="string(@num)"/>
							<xsl:with-param name="mark" select="true()"/>
						</xsl:call-template>
						<xsl:call-template name="dcell">
							<xsl:with-param name="row" select="."/>
							<xsl:with-param name="f" select="'proto'"/>
							<xsl:with-param name="val" select="string(proto)"/>
						</xsl:call-template>
						<xsl:call-template name="dcell">
							<xsl:with-param name="row" select="."/>
							<xsl:with-param name="f" select="'syll'"/>
							<xsl:with-param name="val" select="string(proto/@syll)"/>
						</xsl:call-template>
						<xsl:call-template name="dcell">
							<xsl:with-param name="row" select="."/>
							<xsl:with-param name="f" select="'contextL'"/>
							<xsl:with-param name="val" select="string(proto/@contextL)"/>
						</xsl:call-template>
						<xsl:call-template name="dcell">
							<xsl:with-param name="row" select="."/>
							<xsl:with-param name="f" select="'contextR'"/>
							<xsl:with-param name="val" select="string(proto/@contextR)"/>
						</xsl:call-template>

						<!-- Iterate over the CANONICAL column list so that missing
						     <modern> elements produce an empty cell in the correct
						     column rather than shifting subsequent cells left. -->
						<xsl:variable name="this-corr" select="."/>
						<xsl:for-each select="$cols">
							<xsl:variable name="d"    select="@dialecte"/>
							<xsl:variable name="cell" select="$this-corr/modern[@dialecte = $d]"/>
							<td>
								<xsl:if test="$cell/@diff = 'added' or $cell/@diff = 'deleted'">
									<xsl:attribute name="class">diff-<xsl:value-of select="$cell/@diff"/></xsl:attribute>
								</xsl:if>
								<xsl:for-each select="$cell/seg">
									<xsl:call-template name="dspan"><xsl:with-param name="content">
										<xsl:if test="@statut='doute'">=</xsl:if>
										<xsl:value-of select="."/>
									</xsl:with-param></xsl:call-template>
									<xsl:if test="(position()!=last()) or (@statut!='doute')">,</xsl:if>
								</xsl:for-each>
							</td>
						</xsl:for-each>
					</tr>
				</xsl:for-each>
			</table>
		</div>

		<!-- ── Rules ────────────────────────────────────────────────────────── -->
		<button type="button" data-bs-toggle="collapse" data-bs-target="#{$uid}-rules">
			<xsl:attribute name="class">params-sec-hdr<xsl:if test="not($open-rules)"> collapsed</xsl:if></xsl:attribute>
			<xsl:attribute name="aria-expanded"><xsl:value-of select="$open-rules"/></xsl:attribute>Rules</button>
		<div id="{$uid}-rules">
			<xsl:attribute name="class">collapse<xsl:if test="$open-rules"> show</xsl:if></xsl:attribute>
			<table class="table table-sm table-hover table-bordered sets sortable">
				<thead>
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
						<xsl:call-template name="rowclass"/>
						<xsl:call-template name="dcell">
							<xsl:with-param name="row" select="."/>
							<xsl:with-param name="f" select="'num'"/>
							<xsl:with-param name="val" select="string(@num)"/>
							<xsl:with-param name="mark" select="true()"/>
						</xsl:call-template>
						<xsl:call-template name="dcell">
							<xsl:with-param name="row" select="."/>
							<xsl:with-param name="f" select="'input'"/>
							<xsl:with-param name="val" select="string(input)"/>
						</xsl:call-template>
						<xsl:call-template name="dcell">
							<xsl:with-param name="row" select="."/>
							<xsl:with-param name="f" select="'outcome'"/>
							<xsl:with-param name="val" select="string(outcome)"/>
						</xsl:call-template>
						<xsl:call-template name="dcell">
							<xsl:with-param name="row" select="."/>
							<xsl:with-param name="f" select="'contextL'"/>
							<xsl:with-param name="val" select="string(input/@contextL)"/>
						</xsl:call-template>
						<xsl:call-template name="dcell">
							<xsl:with-param name="row" select="."/>
							<xsl:with-param name="f" select="'contextR'"/>
							<xsl:with-param name="val" select="string(input/@contextR)"/>
						</xsl:call-template>
						<xsl:call-template name="dcell">
							<xsl:with-param name="row" select="."/>
							<xsl:with-param name="f" select="'stage'"/>
							<xsl:with-param name="val" select="string(@stage)"/>
						</xsl:call-template>
						<xsl:call-template name="dcell">
							<xsl:with-param name="row" select="."/>
							<xsl:with-param name="f" select="'languages'"/>
							<xsl:with-param name="val" select="string(outcome/@languages)"/>
						</xsl:call-template>
					</tr>
				</xsl:for-each>
			</table>
		</div>

		<!-- ── Exceptions (quirks) ──────────────────────────────────────────── -->
		<xsl:if test="quirk">
			<button type="button" data-bs-toggle="collapse" data-bs-target="#{$uid}-quirks">
				<xsl:attribute name="class">params-sec-hdr<xsl:if test="not($open-quirks)"> collapsed</xsl:if></xsl:attribute>
				<xsl:attribute name="aria-expanded"><xsl:value-of select="$open-quirks"/></xsl:attribute>Exceptions</button>
			<div id="{$uid}-quirks">
				<xsl:attribute name="class">collapse<xsl:if test="$open-quirks"> show</xsl:if></xsl:attribute>
				<table class="table table-sm table-hover table-bordered sets sortable">
					<thead>
						<tr>
							<th>id</th>
							<th>source id</th>
							<th>lang</th>
							<th>lexeme</th>
							<th>gloss</th>
							<th>alternative</th>
							<th>analysis</th>
							<th>notes</th>
						</tr>
					</thead>
					<xsl:for-each select="quirk">
						<xsl:variable name="analysis">
							<xsl:value-of select="analysis_slot"/>
							<xsl:if test="string(analysis_value)">=<xsl:value-of select="analysis_value"/></xsl:if>
						</xsl:variable>
						<xsl:variable name="notes">
							<xsl:for-each select="note">
								<xsl:value-of select="."/>
								<xsl:if test="position() != last()">; </xsl:if>
							</xsl:for-each>
						</xsl:variable>
						<tr>
							<xsl:call-template name="rowclass"/>
							<xsl:call-template name="dcell">
							<xsl:with-param name="row" select="."/>
							<xsl:with-param name="f" select="'id'"/>
							<xsl:with-param name="val" select="string(@id)"/>
							<xsl:with-param name="mark" select="true()"/>
						</xsl:call-template>
							<xsl:call-template name="dcell">
							<xsl:with-param name="row" select="."/>
							<xsl:with-param name="f" select="'source_id'"/>
							<xsl:with-param name="val" select="string(source_id)"/>
						</xsl:call-template>
							<xsl:call-template name="dcell">
							<xsl:with-param name="row" select="."/>
							<xsl:with-param name="f" select="'lg'"/>
							<xsl:with-param name="val" select="string(lg)"/>
						</xsl:call-template>
							<xsl:call-template name="dcell">
							<xsl:with-param name="row" select="."/>
							<xsl:with-param name="f" select="'lx'"/>
							<xsl:with-param name="val" select="string(lx)"/>
						</xsl:call-template>
							<xsl:call-template name="dcell">
							<xsl:with-param name="row" select="."/>
							<xsl:with-param name="f" select="'gl'"/>
							<xsl:with-param name="val" select="string(gl)"/>
						</xsl:call-template>
							<xsl:call-template name="dcell">
							<xsl:with-param name="row" select="."/>
							<xsl:with-param name="f" select="'alternative'"/>
							<xsl:with-param name="val" select="string(alternative)"/>
						</xsl:call-template>
							<xsl:call-template name="dcell">
							<xsl:with-param name="row" select="."/>
							<xsl:with-param name="f" select="'analysis'"/>
							<xsl:with-param name="val" select="string($analysis)"/>
						</xsl:call-template>
							<xsl:call-template name="dcell">
							<xsl:with-param name="row" select="."/>
							<xsl:with-param name="f" select="'notes'"/>
							<xsl:with-param name="val" select="string($notes)"/>
						</xsl:call-template>
						</tr>
					</xsl:for-each>
				</table>
			</div>
		</xsl:if>

	</div>
</xsl:template>

</xsl:stylesheet>
