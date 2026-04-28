<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:import href="sets2html.xsl" />
  <xsl:import href="sets2venn.xsl" />

    <xsl:output
            method="html"
            indent="yes"
            encoding="utf-8"/>

    <xsl:strip-space elements="*"/>

    <xsl:template match="/">
        <div>
            <p style="font-style: italic">created at: <xsl:value-of select=".//createdat"/></p>
            <h5>Summary statistics</h5>
            <xsl:apply-templates select=".//venn"/>
            <xsl:apply-templates select=".//sankey"/>
            <xsl:apply-templates select=".//settings"/>
            <xsl:apply-templates select=".//totals" mode="summary"/>
            <xsl:apply-templates select=".//stats"/>
            <xsl:apply-templates select="stats/sets_in_common"/>
            <xsl:apply-templates select="stats/sets_only_in_lexicon1"/>
            <xsl:apply-templates select="stats/sets_only_in_lexicon2"/>
            <!-- xsl:apply-templates select="stats/matrix"/ -->
        </div>
    </xsl:template>

    <xsl:template match="sets_in_common">
        <h6><span class="fas fa-angle-double-down"/>Sets in common</h6>
        <div style="display: none;">
            <xsl:call-template name="sets"/>
        </div>
    </xsl:template>
    <xsl:template match="sets_only_in_lexicon1">
        <h6><span class="fas fa-angle-double-down"/>Sets only in "Sets 1"</h6>
        <div style="display: none;">
            <xsl:call-template name="sets"/>
        </div>
    </xsl:template>
    <xsl:template match="sets_only_in_lexicon2">
        <h6><span class="fas fa-angle-double-down"/>Sets only in "Sets 2"</h6>
        <div style="display: none;">
            <xsl:call-template name="sets"/>
        </div>
    </xsl:template>
    <xsl:template match="sets_diff">
        <h6><span class="fas fa-angle-double-down"/>Sets Diff</h6>
        <div style="display: inline;">
            <div class="p-2">
                <button class="w-25 p-1 rounded l1">in sets 1</button>
                <button class="w-25 p-1 rounded l2">in sets 2</button>
                <button class="w-25 p-1 rounded both">in both</button>
            </div>
            <xsl:call-template name="threeway"/>
        </div>
    </xsl:template>
    <xsl:template match="matrix">
        <h6><span class="fas fa-angle-double-down"/>Table of Overlaps</h6>
        <div style="display: inline;">
            <div class="p-2">
                <table class="table table-sm table-striped sortable">
                    <thead>
                        <xsl:copy-of select="header/*"/>
                    </thead>
                    <tbody>
                        <xsl:copy-of select="table/*"/>
                    </tbody>
                </table>

            </div>
        </div>
    </xsl:template>

    <xsl:template match="venn">
        <img height="200px;" src="/plot/venn/{@value}"/>
    </xsl:template>

    <xsl:template match="sankey">
        <img height="300px;" src="/plot/sankey/{@value}"/>
    </xsl:template>

    <xsl:template match="settings">
        <h5>Experiment settings</h5>
        <xsl:apply-templates select=".//settings"/>
    </xsl:template>

    <xsl:template match="totals" mode="summary">
        <div class="table-responsive">
        <table class="table table-sm table-striped sortable">
            <thead>
                <tr>
                    <th>Stat</th>
                    <th class="col-gloss">Value</th>
                </tr>
            </thead>
            <xsl:for-each select="./*">
                <tr>
                    <td><xsl:value-of select ="name(.)"/></td>
                    <td class="col-gloss"><xsl:value-of select ="@value"/></td>
                </tr>
            </xsl:for-each>
            <!-- Append key run settings so they appear alongside the numeric stats -->
            <xsl:for-each select="../settings/parm[@key='context_match_type'
                                                 or @key='spec'
                                                 or @key='strict']">
                <tr>
                    <td><xsl:value-of select="@key"/></td>
                    <td class="col-gloss"><xsl:value-of select="@value"/></td>
                </tr>
            </xsl:for-each>
        </table>
    </div>
    </xsl:template>

  <xsl:key name="elements" match="lexicons/lexicon/*" use="name()"/>
  <xsl:key name="subtotals" match="totals/*" use="name()"/>

    <xsl:template match="stats">
        <xsl:apply-templates select="lexicons"/>
        <xsl:apply-templates select="correspondences"/>
    </xsl:template>

    <xsl:template match="lexicons">
        <h5>Lexicon statistics</h5>
        <div class="table-responsive">
        <table class="table table-sm table-striped sortable">
            <thead>
              <tr>
                  <th>language</th>
                <xsl:for-each select="//*[generate-id(.)=generate-id(key('elements',name())[1])]">
                  <xsl:for-each select="key('elements', name())">
                    <xsl:if test="position()=1">
                      <th>
                        <xsl:call-template name="col-display-name">
                          <xsl:with-param name="n" select="name()"/>
                        </xsl:call-template>
                      </th>
                    </xsl:if>
                  </xsl:for-each>
                </xsl:for-each>
              </tr>
            </thead>
            <xsl:apply-templates select="lexicon"/>
            <tr>
              <th>totals</th>
                <xsl:for-each select="//*[generate-id(.)=generate-id(key('elements',name())[1])]">
                  <xsl:for-each select="key('subtotals', name())">
                    <xsl:if test="position()=1">
                      <th><xsl:value-of select ="@value"/></th>
                    </xsl:if>
                  </xsl:for-each>
                </xsl:for-each>
            </tr>
        </table>
        </div>
    </xsl:template>

    <!-- Map internal stat names to user-friendly column labels -->
    <xsl:template name="col-display-name">
      <xsl:param name="n"/>
      <xsl:choose>
        <xsl:when test="$n = 'no_parses'">failures</xsl:when>
        <xsl:when test="$n = 'in_sets'">in sets</xsl:when>
        <xsl:otherwise><xsl:value-of select="$n"/></xsl:otherwise>
      </xsl:choose>
    </xsl:template>

    <xsl:template match="correspondences">
        <div class="table-responsive">
        <table class="table table-sm table-striped sortable">
            <thead>
              <tr>
                  <th>correspondence</th>
                  <th>in reconstructions</th>
                  <th>in sets</th>
              </tr>
            </thead>
            <tbody>
                <xsl:apply-templates select="correspondence"/>
            </tbody>
        </table>
        </div>
        <p>correspondences_used: <xsl:value-of select=".//correspondences_used[@value]"/></p>
    </xsl:template>


    <xsl:template match="settings">
        <div class="table-responsive">
        <table class="table table-sm table-striped sortable">
            <thead>
              <tr>
                  <th>Setting</th>
                  <th>Value</th>
              </tr>
            </thead>
            <tbody>
                <xsl:apply-templates select="parm"/>
            </tbody>
        </table>
        </div>
    </xsl:template>


    <xsl:template match="correspondence">
        <tr>
            <td><xsl:value-of select="@value"/></td>
            <xsl:for-each select="./*">
                <td><xsl:value-of select ="@value"/></td>
            </xsl:for-each>
        </tr>
    </xsl:template>

    <xsl:template match="parm">
        <tr>
            <td><xsl:value-of select="@key"/></td>
            <td><xsl:value-of select="@value"/></td>
        </tr>
    </xsl:template>

    <xsl:template match="lexicon">
        <tr>
            <td>
                <xsl:value-of select="@language"/>
            </td>
            <xsl:for-each select="./*">
                <td><xsl:value-of select ="@value"/></td>
            </xsl:for-each>
        </tr>
    </xsl:template>


    <xsl:template match="totals" mode="bottom">
        <tr>
            <td>
                Totals
            </td>
            <xsl:for-each select="./*">
                <td><xsl:value-of select ="@value"/></td>
            </xsl:for-each>
        </tr>
    </xsl:template>

    <xsl:template match="*[@type = 'string']">
        <xsl:value-of select='@value'/>
    </xsl:template>
    <xsl:template match="*[@type = 'float']">
        <xsl:value-of select='format-number(@value, "##.###")'/>
    </xsl:template>
    <xsl:template match="*[@type = 'integer']">
        <xsl:value-of select='format-number(@value, "###,###")'/>
    </xsl:template>

</xsl:stylesheet>
