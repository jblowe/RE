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
        <html>
            <head>
                <link rel="stylesheet" type="text/css" href="/static/reconengine.css"/>
            </head>
            <body>
                <h5>Regular cognate sets</h5>
                <p>
                   <div style="float: left; width:60px;">
                        <b>n =
                            <xsl:value-of select="count(.//sets/set)"/>
                        </b>
                    </div>
                    <div style="float: left; width:220px;">
                        <i>created at:
                            <xsl:value-of select=".//createdat"/>
                        </i>
                    </div>
                    <div style="float: left; width:160px;">
                        <a href="?tabular">switch to tabular display</a>
                    </div>
                     <div style="float: left; width:80px;">
                        <a href="#isolates">
                            <xsl:value-of select="count(.//isolates/set)"/>
                            isolates
                        </a>
                    </div>
                    <div style="float: left; width:80px;">
                        <a href="#failures">
                            <xsl:value-of select="count(.//failures/set/sf/rfx)"/>
                            failures</a>
                    </div>
                </p>
                <xsl:apply-templates select=".//sets"/>
                <xsl:apply-templates select=".//isolates"/>
                <xsl:apply-templates select=".//failures"/>
            </body>
        </html>
    </xsl:template>

    <xsl:param name="isolates" select="'null'"/>

    <xsl:template match="sets" name="sets">
        <ul class="list-unstyled">
            <xsl:apply-templates select="set"/>
        </ul>
    </xsl:template>

    <xsl:template match="isolates">
        <div style="float: left;" >
        <a name="isolates"/>
        <h5>Isolates</h5>
        <h6>n = <xsl:value-of select="count(set)" /></h6>
        <ul class="list-unstyled">
            <xsl:apply-templates select="set"/>
        </ul>
        </div>
    </xsl:template>

    <xsl:template match="failures">
        <div style="float: left;" >
        <a name="failures"/>
        <h5>Failures</h5>
        <h6>n = <xsl:value-of select="count(set)" /></h6>
        <ul class="list-unstyled">
            <xsl:apply-templates select="set"/>
        </ul>
        </div>
    </xsl:template>

    <xsl:template match="set">
        <li class="sf">
            <div class="wrapper etymonrow">
                <div class="id"><xsl:value-of select="id"/></div>
                <xsl:choose>
                    <xsl:when test="multi">
                        <xsl:apply-templates select="multi"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <div class="plg"><xsl:value-of select="plg"/></div>
                        <div class="pfm"><xsl:value-of select="pfm"/></div>
                        <div class="pgl"><xsl:value-of select="pgl"/></div>
                        <div class="rcn">[<xsl:value-of select="rcn"/>]</div>
                    </xsl:otherwise>
                </xsl:choose>
                <div class="mel" title="{mel}"><xsl:value-of select="melid"/>:
                    <xsl:value-of select="substring-before(concat(mel, ',' ) , ',')"/>
                </div>
            </div>
            <xsl:apply-templates select="sf"/>
        </li>
    </xsl:template>

    <xsl:template match="sf">
        <ul class="list-unstyled">
            <xsl:apply-templates select="rfx"/>
            <xsl:apply-templates select="subset"/>
        </ul>
    </xsl:template>

    <xsl:template match="multi">
        <div>
        <div class="plg"><xsl:value-of select="plg"/></div>
        <div class="pfm"><xsl:value-of select="pfm"/></div>
        <div class="pgl"><xsl:value-of select="pgl"/></div>
        <div class="rcn">[<xsl:value-of select="rcn"/>]</div>
        </div>
    </xsl:template>

    <xsl:template match="subset">
        <div class="level{@level}">
        <li>
            <div class="wrapper subsetrow">
            <div class="id"><xsl:value-of select="id"/></div>
            <div class="plg"><xsl:value-of select="plg"/></div>
            <div class="pfm"><xsl:value-of select="pfm"/></div>
            <div class="pgl"><xsl:value-of select="pgl"/></div>
            <div class="rcn">[<xsl:value-of select="rcn"/>]</div>
            </div>
        </li>
        <ul class="list-unstyled">
            <xsl:apply-templates select="sf"/>
        </ul>
        </div>
    </xsl:template>

    <xsl:template match="rfx">
        <li>
            <div class="wrapper {membership}">
            <div class="lg"><xsl:apply-templates select="lg"/></div>
            <div class="lx"><xsl:apply-templates select="lx"/></div>
            <div class="gl"><xsl:apply-templates select="gl"/></div>
            <xsl:choose>
                <xsl:when test="hn">
                    <div class="nn">[<xsl:apply-templates select="hn"/>]</div>
                </xsl:when>
                <xsl:when test="id">
                    <div class="nn">[<xsl:apply-templates select="id"/>]</div>
                </xsl:when>
                <xsl:otherwise/>
            </xsl:choose>
            </div>
        </li>
    </xsl:template>

    <xsl:template match="gl|hw">
        <xsl:apply-templates/>
    </xsl:template>

</xsl:stylesheet>
