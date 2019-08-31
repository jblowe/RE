<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
      xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
      xmlns:exsl="http://xmlns.opentechnology.org/xslt-extensions/functions"
      xmlns:re="http://exslt.org/re"
>

    <xsl:output
            method="html"
            indent="yes"
            encoding="utf-8"/>

    <xsl:template match="/">
        <!-- p style="font-style: italic">created at: <xsl:value-of select=".//createdat"/></p -->
        <h5>Regular cognate sets</h5>
        <p>
            <b><div style="float: left; width:100px;">n = <xsl:value-of select="count(.//sets/set)" /></div>
            <div style="float: left; width:200px;"><a href="?paragraph">switch to paragraph display</a></div>
            <div style="float: left; width:100px;"><a href="#isolates">isolates</a></div>
            <div style="float: left; width:100px;"><a href="#failures">failures</a></div>
            </b>
        </p>
        <div class="should-be-responsive">
        <table class="table sets">
            <thead>
                <tr>
                    <th>num</th>
                    <th>plg</th>
                    <th>pfm</th>
                    <!-- th>pgl</th -->
                    <th>rcn</th>
                    <th>mel</th>
                    <xsl:apply-templates select=".//languages"/>
                </tr>
            </thead>
            <xsl:call-template name="sets">
               <xsl:with-param name="lgs" select=".//languages"/>
            </xsl:call-template>
        </table>
        </div>
        <xsl:apply-templates select=".//isolates"/>
        <xsl:apply-templates select=".//failures"/>
    </xsl:template>

    <xsl:template name="sets">
        <xsl:param name="lgs"/>
        <xsl:for-each select=".//sets/set">
            <tr>
            <td id="id"><xsl:value-of select="id"/></td>
            <td id="plg"><xsl:value-of select="plg"/></td>
            <td id="pfm"><xsl:value-of select="pfm"/></td>
            <!-- td id="pgl"><xsl:value-of select="pgl"/></td -->
            <td id="rcn"><xsl:value-of select="rcn"/></td>
            <td id="mel" title="{mel}"><xsl:value-of select="melid"/></td>
            <xsl:variable name="reflexes" select="sf"/>
            <xsl:for-each select="$lgs/*">
                <xsl:variable name="label" select="."/>
                <td>
                    <xsl:for-each select="$reflexes/*">
                        <xsl:if test="lg = $label">
                            <xsl:text> </xsl:text>
                            <span title='{gl}'><xsl:apply-templates select="lx"/></span>
                        </xsl:if>
                    </xsl:for-each>
                </td>
            </xsl:for-each>
            </tr>
        </xsl:for-each>
    </xsl:template>

    <xsl:template match="languages">
        <xsl:for-each select="*">
            <th><xsl:value-of select="."/></th>
        </xsl:for-each>
    </xsl:template>

    <xsl:template match="set">
        <li id="sf">
            <div class="wrapper etymonrow">
                <div id="id"><xsl:value-of select="id"/></div>
                <div id="plg"><xsl:value-of select="plg"/></div>
                <div id="pfm"><xsl:value-of select="pfm"/></div>
                <div id="pgl"><xsl:value-of select="pgl"/></div>
                <div id="rcn">[<xsl:value-of select="rcn"/>]</div>
                <div id="mel" title="{mel}"><xsl:value-of select="melid"/>:
                    <xsl:value-of select="substring-before(concat(mel, ',' ) , ',')"/>
                </div>
            </div>
            <xsl:apply-templates select="sf"/>
        </li>
    </xsl:template>

    <xsl:template match="sf">
        <xsl:apply-templates select="rfx2"/>
        <xsl:apply-templates select="subset"/>
    </xsl:template>

    <xsl:template match="subset">
        <div class="level{@level}">
        <li>
            <div class="wrapper subsetrow">
            <div id="id"><xsl:value-of select="id"/></div>
            <div id="plg"><xsl:value-of select="plg"/></div>
            <div id="pfm"><xsl:value-of select="pfm"/></div>
            <div id="pgl"><xsl:value-of select="pgl"/></div>
            <div id="rcn">[<xsl:value-of select="rcn"/>]</div>
            </div>
        </li>
        <ul class="list-unstyled">
            <xsl:apply-templates select="sf"/>
        </ul>
        </div>
    </xsl:template>

    <xsl:template match="rfx">
        <td><span title='{gl}'><xsl:apply-templates select="lx"/></span></td>
    </xsl:template>

    <xsl:template match="gl|hw">
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="rfx2">
        <li>
            <div class="wrapper">
            <div id="lg"><xsl:apply-templates select="lg"/></div>
            <div id="lx"><xsl:apply-templates select="lx"/></div>
            <div id="gl"><xsl:apply-templates select="gl"/></div>
            <xsl:choose>
                <xsl:when test="hn">
                    <div id="nn">[<xsl:apply-templates select="hn"/>]</div>
                </xsl:when>
                <xsl:when test="id">
                    <div id="nn">[<xsl:apply-templates select="id"/>]</div>
                </xsl:when>
                <xsl:otherwise/>
            </xsl:choose>
            </div>
        </li>
    </xsl:template>

    <xsl:template match="isolates">
        <a name="isolates"/>
        <h5>Isolates</h5>
        <h6>n = <xsl:value-of select="count(set)" /></h6>
        <ul class="list-unstyled">
            <xsl:apply-templates select="set"/>
        </ul>
    </xsl:template>

    <xsl:template match="failures">
        <a name="failures"/>
        <h5>Failures</h5>
        <h6>n = <xsl:value-of select="count(set)" /></h6>
        <ul class="list-unstyled">
            <xsl:apply-templates select="set"/>
        </ul>
    </xsl:template>

</xsl:stylesheet>
