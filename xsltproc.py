import sys
import lxml.etree as ET

def xml2html(xsl_filename, xml_filename):

    dom = ET.parse(xml_filename)
    xslt = ET.parse(xsl_filename)
    transform = ET.XSLT(xslt)
    newdom = transform(dom)
    return newdom


sys.stdout.write(ET.tostring(xml2html(sys.argv[1], sys.argv[2]), pretty_print=True))
