# -*- coding: utf-8
import sys
import lxml.etree as ET
import re
from compute_gloss import compute_gloss
from copy import deepcopy


def update_dom(xml_filename, gloss_band):
    dom = ET.parse(xml_filename)
    dom = add_alternate_gloss(dom, gloss_band)
    dom = check_hw(dom)
    return dom


def add_alternate_gloss(dom, gloss_band):
    entries = dom.findall('entry')
    for e in entries:
        ngl = ET.Element('ngl')
        gloss = e.find(f'.//{gloss_band}')
        gl = e.find(f'.//gl')
        has_ngl = e.find(f'.//ngl')
        if has_ngl is not None:
            continue
        if gloss is not None:
            ngl.text = compute_gloss(gloss.text)
        elif gl is not None:
            ngl.text = compute_gloss(gl.text)
        else:
            ngl.text = 'placeholder'
        e.insert(1, ngl)

        if gl is None and gloss is not None:
            gl = ET.Element('gl')
            # print(gloss.text)
            gl.text = gloss.text
            e.insert(1, gl)
    return dom


def check_hw(dom):
    entries = dom.findall('entry')
    # nb: this function rebuilds the dom from <entry>s
    language = dom.getroot().attrib.get('dialecte')
    new_dom = ET.Element('lexicon', attrib={'dialecte': language})
    for e in entries:
        # the following tags can all be headwords. replicate article if they are found.
        for tag in 'hw var mar tag sya'.split(' '):
            hw = e.find(f'.//{tag}')
            # add a headword element if there isn't one already
            if hw is not None:
                break
        hw_to_use = ET.Element('hw')
        if hw is not None:
            hw_to_use.text = hw.text
        else:
            # there was no headword. use a placeholder
            hw_to_use.text = 'placeholder'
        # if we found a headword, use it. otherwise insert the other element as hw
        if tag == 'hw':
            adjust_hw(hw)
        else:
            adjust_hw(hw_to_use)
            e.insert(0, hw_to_use)
        new_dom.append(deepcopy(e))
    return new_dom


def adjust_hw(element):
    hw_text = element.text
    if hw_text == 'placeholder': return
    hw_text = re.split(r'[\-=]', hw_text)
    # nothing to see here
    if len(hw_text) == 1: return
    hw_text = [h for h in hw_text if h]
    element.text = hw_text[0]
    del hw_text[0]
    for h in hw_text:
        addnl_hw = ET.Element('suffix')
        addnl_hw.text = f'-{h}'
        element.append(addnl_hw)
    # <hw>( *[=\-])#<prefix>\1</prefix><hw>#;
    # <hw>(.*?)( *[=\-].*?)</hw>#<hw>\1</hw><suffix>\2</suffix>#;
    return


output_string = ET.tostring(update_dom(sys.argv[1], sys.argv[2]), pretty_print=True, encoding='unicode')
output_file = open(sys.argv[1], 'w', encoding='utf-8')
output_file.write(output_string)
