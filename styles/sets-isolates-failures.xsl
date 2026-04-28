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
          <th class="col-plg">lg</th>
          <th class="col-pfm">lx</th>
          <th class="col-gloss">gl</th>
          <th class="col-pfm">pfm</th>
          <th class="col-rcn">rcn</th>
          <th class="col-plg">id</th>
          <th class="col-gloss">Reason</th>
        </tr>
      </thead>
      <tbody>
        <xsl:for-each select="rfx">
          <tr>
            <td class="col-plg"><xsl:value-of select="lg"/></td>
            <td class="col-pfm">
              <xsl:choose>
                <xsl:when test="lxf">
                  <xsl:value-of select="lxf"/>
                  <small style="color:#888;"> &lt;&lt; <xsl:value-of select="lx"/></small>
                </xsl:when>
                <xsl:otherwise><xsl:value-of select="lx"/></xsl:otherwise>
              </xsl:choose>
            </td>
            <td class="col-gloss"><xsl:value-of select="gl"/></td>
            <td class="col-pfm"><xsl:value-of select="pfm"/></td>
            <td class="col-rcn"><xsl:value-of select="rcn"/></td>
            <td class="col-plg"><xsl:value-of select="@id"/></td>
            <td class="col-gloss"><xsl:value-of select="reason"/></td>
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
          <th class="col-plg">lg</th>
          <th class="col-pfm">lx</th>
          <th class="col-gloss">gl</th>
          <th class="col-plg">id</th>
        </tr>
      </thead>
      <tbody>
        <xsl:for-each select="rfx">
          <tr>
            <td class="col-plg"><xsl:value-of select="lg"/></td>
            <td class="col-pfm">
              <xsl:choose>
                <xsl:when test="lxf">
                  <xsl:value-of select="lxf"/>
                  <small style="color:#888;"> &lt;&lt; <xsl:value-of select="lx"/></small>
                </xsl:when>
                <xsl:otherwise><xsl:value-of select="lx"/></xsl:otherwise>
              </xsl:choose>
            </td>
            <td class="col-gloss"><xsl:value-of select="gl"/></td>
            <td class="col-plg"><xsl:value-of select="@id"/></td>
          </tr>
        </xsl:for-each>
      </tbody>
    </table>
  </xsl:template>

</xsl:stylesheet>
