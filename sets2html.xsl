<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

    <xsl:param name="isolates" select="'null'"/>

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
                <p style="font-style: italic">created at: <xsl:value-of select=".//createdat"/></p>
                <h5>n = <xsl:value-of select="count(sets/set)" />
                </h5>
                <xsl:apply-templates select=".//sets"/>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="sets">
        <ul class="list-unstyled">
            <xsl:apply-templates select="set"/>
        </ul>
    </xsl:template>

    <xsl:template match="set">
        <li id="sf">
            <div class="wrapper etymonrow">
                <div id="id"><xsl:value-of select="id"/></div>
                <div id="plg"><xsl:value-of select="plg"/></div>
                <div id="pfm"><xsl:value-of select="pfm"/></div>
                <div id="pgl"><xsl:value-of select="pgl"/></div>
                <div id="rcn">[<xsl:value-of select="rcn"/>]</div>
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

    <xsl:template match="gl|hw">
        <xsl:apply-templates/>
    </xsl:template>

</xsl:stylesheet>
