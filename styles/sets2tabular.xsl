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
            <a href="?paragraph">switch to paragraph display</a>
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
        <!-- TODO: figure out what class, if any makes table both sortable and header-sticky -->
        <div style="float: left;" class="table-responsive">
            <table class="table-sm table-bordered sets sortable">
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

        </body>
    </html>
    </xsl:template>

    <xsl:template name="sets">
        <xsl:param name="lgs"/>
        <xsl:for-each select=".//sets/set">
            <tr>
                <td class="id">
                    <xsl:value-of select="id"/>
                </td>

                <xsl:choose>
                    <xsl:when test="multi">
                        <td class="plg">
                            <span class="">
                                <xsl:value-of select=".//plg"/>
                            </span>
                        </td>
                        <!-- td class="pfm">
                            <span class="multiple" title='
                            </span>
                        </td -->
                        <td class="pfm">
                            <span class="multiple">
                                <xsl:attribute name="title">
                                    <xsl:for-each select=".//pfm">
                                        <xsl:if test="position() != 1" >
                                        <xsl:text>, </xsl:text>
                                        </xsl:if>
                                        <xsl:value-of select="."/>
                                    </xsl:for-each>
                                </xsl:attribute>
                                <xsl:value-of select="multi/pfm"/>
                            </span>
                        </td>
                       <td class="rcn">
                            <span>
                                <xsl:attribute name="title">
                                    <xsl:for-each select=".//rcn">
                                        <xsl:if test="position() != 1" >
                                        <xsl:text>, </xsl:text>
                                        </xsl:if>
                                        <xsl:value-of select="."/>
                                    </xsl:for-each>
                                </xsl:attribute>
                                <xsl:value-of select="multi/rcn"/>
                            </span>
                        </td>
                    </xsl:when>
                    <xsl:otherwise>
                        <td class="plg">
                            <xsl:value-of select="plg"/>
                        </td>
                        <td class="pfm">
                            <xsl:value-of select="pfm"/>
                        </td>
                        <td class="rcn">
                            <xsl:value-of select="rcn"/>
                        </td>
                    </xsl:otherwise>
                </xsl:choose>
                <td class="mel" title="{mel}">
                    <xsl:value-of select="melid"/>:
                    <xsl:value-of select="substring-before(concat(mel, ',' ) , ',')"/>
                </td>
                <xsl:variable name="reflexes" select="sf"/>
                <xsl:for-each select="$lgs/*">
                    <xsl:variable name="label" select="."/>
                    <td>
                        <xsl:for-each select="$reflexes/*">
                            <xsl:if test="lg = $label">
                                <xsl:text/>
                                <xsl:text> </xsl:text>
                                <span title='{gl} {id}'>
                                    <xsl:apply-templates select="lx"/>
                                </span>
                            </xsl:if>
                        </xsl:for-each>
                    </td>
                </xsl:for-each>
            </tr>
        </xsl:for-each>
    </xsl:template>


    <xsl:template match="multi">
        <td>
            <div class="plg">
                <xsl:value-of select="plg"/>
            </div>
            <div class="pfm">
                <xsl:value-of select="pfm"/>
            </div>
            <div class="pgl">
                <xsl:value-of select="pgl"/>
            </div>
            <div class="rcn">[<xsl:value-of select="rcn"/>]
            </div>
        </td>
    </xsl:template>


    <xsl:template match="languages">
        <xsl:for-each select="*">
            <th>
                <xsl:value-of select="."/>
            </th>
        </xsl:for-each>
    </xsl:template>

    <xsl:template match="isolates">
        <div style="float: left;">
            <a name="isolates"/>
            <h5>Isolates</h5>
            <h6>n =
                <xsl:value-of select="count(set)"/>
            </h6>
            <ul class="list-unstyled">
                <xsl:apply-templates select="set"/>
            </ul>
        </div>
    </xsl:template>

    <xsl:template match="failures">
        <div style="float: left;">
            <a name="failures"/>
            <h5>Failures</h5>
            <h6>n =
                <xsl:value-of select="count(set)"/>
            </h6>
            <ul class="list-unstyled">
                <xsl:apply-templates select="set"/>
            </ul>
        </div>
    </xsl:template>

    <xsl:template match="set" name="set">
        <li class="sf">
            <div class="wrapper etymonrow">
                <div class="id">
                    <xsl:value-of select="id"/>
                </div>
                <div class="plg">
                    <xsl:value-of select="plg"/>
                </div>
                <div class="pfm">
                    <xsl:value-of select="pfm"/>
                </div>
                <div class="pgl">
                    <xsl:value-of select="pgl"/>
                </div>
                <div class="rcn">[<xsl:value-of select="rcn"/>]
                </div>
                <div class="mel" title="{mel}"><xsl:value-of select="melid"/>:
                    <xsl:value-of select="substring-before(concat(mel, ',' ) , ',')"/>
                </div>
            </div>
            <xsl:apply-templates select="sf"/>
        </li>
    </xsl:template>

    <xsl:template match="sf">
        <xsl:apply-templates select="rfx"/>
        <xsl:apply-templates select="subset"/>
    </xsl:template>

    <xsl:template match="subset">
        <div class="level{@level}">
            <li>
                <div class="wrapper subsetrow">
                    <div class="id">
                        <xsl:value-of select="id"/>
                    </div>
                    <div class="plg">
                        <xsl:value-of select="plg"/>
                    </div>
                    <div class="pfm">
                        <xsl:value-of select="pfm"/>
                    </div>
                    <div class="pgl">
                        <xsl:value-of select="pgl"/>
                    </div>
                    <div class="rcn">[<xsl:value-of select="rcn"/>]
                    </div>
                </div>
            </li>
            <ul class="list-unstyled">
                <xsl:apply-templates select="sf2"/>
            </ul>
        </div>
    </xsl:template>

    <xsl:template match="rfx">
        <li>
            <div class="wrapper">
                <div class="lg">
                    <xsl:apply-templates select="lg"/>
                </div>
                <div class="lx">
                    <xsl:apply-templates select="lx"/>
                </div>
                <div class="gl">
                    <xsl:apply-templates select="gl"/>
                </div>
                <xsl:choose>
                    <xsl:when test="hn">
                        <div class="nn">[<xsl:apply-templates select="hn"/>]
                        </div>
                    </xsl:when>
                    <xsl:when test="id">
                        <div class="nn">[<xsl:apply-templates select="id"/>]
                        </div>
                    </xsl:when>
                    <xsl:otherwise/>
                </xsl:choose>
            </div>
        </li>
    </xsl:template>

    <xsl:template match="gl|hw|lx">
        <xsl:apply-templates/>
    </xsl:template>

</xsl:stylesheet>
