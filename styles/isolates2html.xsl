<?xml version="1.0" encoding="utf-8"?>
<!--
  isolates2html.xsl
  Render only the <isolates> section from a cognate-sets XML document.
  Used by the lazy-load endpoint so the full table is fetched on demand
  rather than being included in the initial sets response.
-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:include href="sets-isolates-failures.xsl"/>
  <xsl:output method="html" indent="yes" encoding="utf-8"/>
  <xsl:template match="/">
    <xsl:apply-templates select=".//isolates"/>
  </xsl:template>
</xsl:stylesheet>
