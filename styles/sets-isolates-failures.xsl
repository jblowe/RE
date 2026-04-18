<?xml version="1.0" encoding="utf-8"?>
<!--
  sets-isolates-failures.xsl
  Shared templates for the Isolates and Failures sections of a cognate-sets
  XML document.  Included (xsl:include) by sets2html.xsl and sets2tabular.xsl
  so both panes render these sections identically.
-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:template match="isolates">
    <a name="isolates"/>
    <h5>Isolates
      <small class="text-muted" style="font-size:0.8em; font-weight:normal;">
        n = <xsl:value-of select="count(rfx)"/>
      </small>
    </h5>
    <table class="table table-sm table-striped table-hover table-bordered sortable">
      <thead>
        <tr>
          <th>lg</th>
          <th>lx</th>
          <th>gl</th>
          <th>pfm</th>
          <th>rcn</th>
          <th>id</th>
        </tr>
      </thead>
      <tbody>
        <xsl:for-each select="rfx">
          <tr>
            <td><xsl:value-of select="lg"/></td>
            <td><xsl:value-of select="lx"/></td>
            <td><xsl:value-of select="gl"/></td>
            <td><xsl:value-of select="pfm"/></td>
            <td><xsl:value-of select="rcn"/></td>
            <td><xsl:value-of select="@id"/></td>
          </tr>
        </xsl:for-each>
      </tbody>
    </table>
  </xsl:template>

  <xsl:template match="failures">
    <a name="failures"/>
    <h5>Failures
      <small class="text-muted" style="font-size:0.8em; font-weight:normal;">
        n = <xsl:value-of select="count(rfx)"/>
      </small>
    </h5>
    <table class="table table-sm table-striped table-hover table-bordered sortable">
      <thead>
        <tr>
          <th>lg</th>
          <th>lx</th>
          <th>gl</th>
          <th>id</th>
        </tr>
      </thead>
      <tbody>
        <xsl:for-each select="rfx">
          <tr>
            <td><xsl:value-of select="lg"/></td>
            <td><xsl:value-of select="lx"/></td>
            <td><xsl:value-of select="gl"/></td>
            <td><xsl:value-of select="@id"/></td>
          </tr>
        </xsl:for-each>
      </tbody>
    </table>
  </xsl:template>

</xsl:stylesheet>
