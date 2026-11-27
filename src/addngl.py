# -*- coding: utf-8
#
# usage: python3 addngl.py lexicon.xml gloss_band[,fallback_band...]
#
#   e.g. python3 addngl.py TEMP.ris.data.xml dfe,dfbot
#
# The gloss comes from the first of the listed bands that the entry has
# (with text); using a fallback band is reported on STDERR.
#
# Post-processes the output of Lex2XML.pl (in place) so that every <entry>
# has what RE needs:
#
#   <hw>   the headword, first element of the entry. If the entry has none,
#          it is made from the band Lex2XML marked headword="true" (the band
#          that started the entry). If it has one, its text is checked
#          against that band's text.
#   <gl>   the gloss. If missing, made from the gloss band.
#   <ngl>  the normalized gloss (compute_gloss), made from the gloss band
#          given on the command line (e.g. 'dff' for syang), or from <gl> if
#          the entry has no such band.
#
# A <gl> or <ngl> made here gets the xml:lang of the band it was made from
# (run addlang.py first).
#
# Only the element's own text is used -- text inside child elements such as
# <tbr> or <xcr> is not part of the headword or gloss. Bands are looked for
# in the entry itself and then in its <mode>s, never in <sub>s (a subentry
# has its own headword and gloss).
#
# Problems are reported on STDERR, one line per entry; 'placeholder' is used
# where a headword or gloss cannot be found.
import sys
import lxml.etree as ET
import re
from compute_gloss import compute_gloss

PLACEHOLDER = 'placeholder'
XML_LANG = '{http://www.w3.org/XML/1998/namespace}lang'


def own_text(element):
    """The element's text, not counting text inside its child elements."""
    return ' '.join(''.join(element.xpath('text()')).split())


def find_band(entry, tag):
    """First <tag> in the entry itself, else in one of its <mode>s."""
    band = entry.find(tag)
    if band is None:
        band = entry.find(f'mode/{tag}')
    return band


def report(filename, entry, message):
    print(f'{filename}: {entry.get("id")}: {message}', file=sys.stderr)


def check_hw(filename, entry):
    headword = entry.find('*[@headword="true"]')
    hw = entry.find('hw')
    if hw is not None:
        if headword is None:
            report(filename, entry, f'no headword band; using <hw> "{own_text(hw)}"')
        elif headword is not hw and own_text(hw) != own_text(headword):
            report(filename, entry,
                   f'<hw> "{own_text(hw)}" differs from headword band '
                   f'<{headword.tag}> "{own_text(headword)}"')
        if entry.index(hw) != 0:
            entry.remove(hw)
            entry.insert(0, hw)
        # the headword band may itself be an <hw> containing <xcr>/<tbr>:
        # keep those, but make sure .text (what RE reads) holds the headword
        hw.text = own_text(hw) or PLACEHOLDER
        for child in hw:
            child.tail = None
        if hw.text == PLACEHOLDER:
            report(filename, entry, '<hw> has no text of its own')
    else:
        hw = ET.Element('hw')
        if headword is not None and own_text(headword):
            hw.text = own_text(headword)
        else:
            hw.text = PLACEHOLDER
            report(filename, entry, 'no headword: no <hw> and no non-empty headword band')
        entry.insert(0, hw)
    adjust_hw(hw)


def find_gloss(entry, gloss_bands):
    """First band in gloss_bands (in order) that has text of its own."""
    for tag in gloss_bands:
        for band in entry.findall(tag) + entry.findall(f'mode/{tag}'):
            if own_text(band):
                return band
    return None


def add_glosses(filename, entry, gloss_bands):
    gl = entry.find('gl')
    gloss = find_gloss(entry, gloss_bands)
    if gloss is not None and gloss.tag != gloss_bands[0]:
        report(filename, entry, f'no <{gloss_bands[0]}>; gloss from <{gloss.tag}> "{own_text(gloss)}"')
    gloss_band = '>, <'.join(gloss_bands)
    source = gloss if gloss is not None else gl
    gl_text = own_text(source) if source is not None else ''
    # the language of the band the gloss came from (set by addlang.py)
    lang = source.get(XML_LANG) if source is not None else None

    if entry.find('ngl') is None:
        ngl = ET.Element('ngl')
        ngl.text = compute_gloss(gl_text) if gl_text else PLACEHOLDER
        if not gl_text:
            report(filename, entry, f'no gloss: no non-empty <{gloss_band}> or <gl>')
        elif lang:
            ngl.set(XML_LANG, lang)
        entry.insert(1, ngl)

    if gl is None:
        gl = ET.Element('gl')
        gl.text = gl_text or PLACEHOLDER
        if gl_text and lang:
            gl.set(XML_LANG, lang)
        entry.insert(1, gl)


def adjust_hw(element):
    # split morpheme boundaries off the headword: ²ham =pə -> ²ham <suffix>-pə</suffix>
    hw_text = element.text
    if hw_text == PLACEHOLDER:
        return
    if not re.search(r'[\-=]', hw_text):
        return
    parts = [h for h in re.split(r'[\-=]', hw_text) if h]
    if not parts:
        return
    element.text = parts[0]
    for h in parts[1:]:
        addnl_hw = ET.Element('suffix')
        addnl_hw.text = f'-{h}'
        element.append(addnl_hw)


def update_dom(xml_filename, gloss_bands):
    dom = ET.parse(xml_filename)
    for entry in dom.getroot().iter('entry'):
        check_hw(xml_filename, entry)
        add_glosses(xml_filename, entry, gloss_bands)
    return dom


if __name__ == '__main__':
    filename, gloss_bands = sys.argv[1], sys.argv[2].split(',')
    # write UTF-8 with a declaration, so later tools (xmllint) keep the
    # characters as they are instead of turning them into &#x...; references
    output = ET.tostring(update_dom(filename, gloss_bands), pretty_print=True,
                         xml_declaration=True, encoding='utf-8')
    with open(filename, 'wb') as output_file:
        output_file.write(output)
