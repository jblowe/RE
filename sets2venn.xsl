<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">


    <xsl:output
            method="html"
            indent="yes"
            encoding="utf-8"/>

    <xsl:template match="threeway" name="threeway">
        <ul class="list-unstyled">
            <xsl:apply-templates select="sxt"/>
        </ul>
    </xsl:template>

    <xsl:template match="sxt">
        <xsl:for-each select="*">
            <h6><xsl:value-of select="name(.)"/></h6>
            <xsl:apply-templates/>
        </xsl:for-each>
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
