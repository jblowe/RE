<?xml version="1.0" encoding="utf-8"?>
<!--
  diff-common.xsl – templates shared by the Browse pane's diff renderings
  (toc2html-view.xsl, fuzzy2html.xsl, mel2html.xsl, lexicon2table.xsl and
  sets-isolates-failures.xsl, which sets2tabular.xsl includes). Included with
  xsl:include; each rendering stays the one stylesheet for its type.

  The diff is computed in Python (REwww/diff_*.py), which annotates the XML:
    diff="added|deleted|changed" on an element;
    diff_<field>="changed" and old_<field>="<old value>" on a row, per field;
    old="<old value>" on a changed list item;
    norm_<field> / norm = "1" when only Unicode normalization differs.
  A file with no such attributes renders as it always did.
-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<!-- class="diff-..." on the current row element, if it is annotated -->
<xsl:template name="rowclass">
	<xsl:if test="@diff">
		<xsl:attribute name="class">diff-<xsl:value-of select="@diff"/></xsl:attribute>
	</xsl:if>
</xsl:template>

<!-- A <td> for field $f of row $row showing $val; marks the cell by the row's
     diff (added / deleted) or by a change to this field (with the old value). -->
<xsl:template name="dcell">
	<xsl:param name="row"/>
	<xsl:param name="f"/>
	<xsl:param name="val"/>
	<xsl:param name="mark" select="false()"/>
	<xsl:variable name="d"    select="string($row/@diff)"/>
	<xsl:variable name="chg"  select="$row/@*[name() = concat('diff_', $f)]"/>
	<xsl:variable name="old"  select="string($row/@*[name() = concat('old_', $f)])"/>
	<xsl:variable name="norm" select="$row/@*[name() = concat('norm_', $f)]"/>
	<td>
		<xsl:choose>
			<xsl:when test="$d = 'added' or $d = 'deleted'">
				<xsl:attribute name="class">diff-<xsl:value-of select="$d"/></xsl:attribute>
			</xsl:when>
			<xsl:when test="$chg">
				<xsl:attribute name="class">diff-changed</xsl:attribute>
				<xsl:attribute name="title">was: <xsl:value-of select="$old"/></xsl:attribute>
			</xsl:when>
		</xsl:choose>
		<xsl:if test="$mark and $d != ''">
			<span class="diff-mark">
				<xsl:choose>
					<xsl:when test="$d = 'added'">+</xsl:when>
					<xsl:when test="$d = 'deleted'">&#8722;</xsl:when>
					<xsl:otherwise>~</xsl:otherwise>
				</xsl:choose>
			</span>
		</xsl:if>
		<xsl:value-of select="$val"/>
		<xsl:if test="$chg and $old != ''">
			<xsl:text> </xsl:text><small class="diff-was"><del><xsl:value-of select="$old"/></del></small>
		</xsl:if>
		<xsl:if test="$norm">
			<xsl:text> </xsl:text><small class="diff-norm">Unicode normalization only</small>
		</xsl:if>
	</td>
</xsl:template>

<!-- ── Helpers for adding diff marks to an EXISTING rendering ────────────────
     Each does nothing when the element has no diff annotation, so the normal
     (non-diff) output is unchanged. Field f is a row field (diff_<f> / old_<f>);
     with f = '' they use the element's own diff / old attributes instead
     (list items such as a <from>, <gl> or a set member <rfx>). -->

<!-- Put on a <td>, <div>, ... after its literal attributes: sets class (base,
     plus the diff class) and, for a change, a "was:" tooltip. -->
<xsl:template name="dattrs">
	<xsl:param name="row" select="."/>
	<xsl:param name="f" select="''"/>
	<xsl:param name="base" select="''"/>
	<xsl:variable name="d" select="string($row/@diff)"/>
	<xsl:variable name="chg" select="$row/@*[name() = concat('diff_', $f)]"/>
	<xsl:variable name="cls">
		<xsl:choose>
			<xsl:when test="$f = '' and $d != ''">diff-<xsl:value-of select="$d"/></xsl:when>
			<xsl:when test="$f != '' and ($d = 'added' or $d = 'deleted')">diff-<xsl:value-of select="$d"/></xsl:when>
			<xsl:when test="$f != '' and $chg">diff-changed</xsl:when>
		</xsl:choose>
	</xsl:variable>
	<xsl:if test="$cls != ''">
		<xsl:attribute name="class"><xsl:value-of select="normalize-space(concat($base, ' ', $cls))"/></xsl:attribute>
		<xsl:variable name="old">
			<xsl:choose>
				<xsl:when test="$f = ''"><xsl:value-of select="$row/@old"/></xsl:when>
				<xsl:otherwise><xsl:value-of select="$row/@*[name() = concat('old_', $f)]"/></xsl:otherwise>
			</xsl:choose>
		</xsl:variable>
		<xsl:if test="($f = '' and $row/@old) or ($f != '' and $chg)">
			<xsl:attribute name="title">was: <xsl:value-of select="$old"/></xsl:attribute>
		</xsl:if>
	</xsl:if>
</xsl:template>

<!-- The old value of a changed field, struck through, to follow the new one. -->
<xsl:template name="dold">
	<xsl:param name="row" select="."/>
	<xsl:param name="f" select="''"/>
	<xsl:variable name="chg"  select="$row/@*[name() = concat('diff_', $f)]"/>
	<xsl:variable name="old">
		<xsl:choose>
			<xsl:when test="$f = ''"><xsl:value-of select="$row/@old"/></xsl:when>
			<xsl:otherwise><xsl:value-of select="$row/@*[name() = concat('old_', $f)]"/></xsl:otherwise>
		</xsl:choose>
	</xsl:variable>
	<xsl:variable name="norm">
		<xsl:choose>
			<xsl:when test="$f = ''"><xsl:value-of select="$row/@norm"/></xsl:when>
			<xsl:otherwise><xsl:value-of select="$row/@*[name() = concat('norm_', $f)]"/></xsl:otherwise>
		</xsl:choose>
	</xsl:variable>
	<xsl:if test="($f = '' and $row/@diff = 'changed' and $row/@old) or ($f != '' and $chg and not($row/@diff = 'added' or $row/@diff = 'deleted'))">
		<xsl:if test="string($old) != ''">
			<xsl:text> </xsl:text><small class="diff-was"><del><xsl:value-of select="$old"/></del></small>
		</xsl:if>
		<xsl:if test="string($norm) != ''">
			<xsl:text> </xsl:text><small class="diff-norm">Unicode normalization only</small>
		</xsl:if>
	</xsl:if>
</xsl:template>

<!-- + / - / ~ in front of a row's first cell. -->
<xsl:template name="dmark">
	<xsl:param name="row" select="."/>
	<xsl:if test="$row/@diff">
		<span class="diff-mark">
			<xsl:choose>
				<xsl:when test="$row/@diff = 'added'">+</xsl:when>
				<xsl:when test="$row/@diff = 'deleted'">&#8722;</xsl:when>
				<xsl:otherwise>~</xsl:otherwise>
			</xsl:choose>
		</span>
	</xsl:if>
</xsl:template>

<!-- Wraps $content (the rendering of the current list item) in a span marked by
     the item's diff, with its old value. Without a diff, just $content. -->
<xsl:template name="dspan">
	<xsl:param name="content"/>
	<xsl:choose>
		<xsl:when test="@diff">
			<span>
				<xsl:call-template name="dattrs"/>
				<xsl:copy-of select="$content"/>
				<xsl:call-template name="dold"/>
			</span>
		</xsl:when>
		<xsl:otherwise><xsl:copy-of select="$content"/></xsl:otherwise>
	</xsl:choose>
</xsl:template>

</xsl:stylesheet>
