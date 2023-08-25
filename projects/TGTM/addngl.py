# -*- coding: utf-8
import sys
import lxml.etree as ET
import re


def update_dom(xml_filename, gloss_band):
    dom = ET.parse(xml_filename)
    dom = select_gloss(dom, gloss_band)
    dom = select_hw(dom)
    return dom

def select_gloss(dom, gloss_band):
    entries = dom.findall('entry')
    for e in entries:
        gloss_to_use = ET.Element('ngl')
        gloss = e.find(f'.//{gloss_band}')
        if gloss is not None:
            gloss_value = gloss.text
        else:
            gloss = e.find(f'.//gl')
            if gloss is not None:
                gloss_value = gloss.text
            else:
                gloss_value = 'placeholder'
        gloss_to_use.text = gloss_value
        e.append(gloss_to_use)
    return dom

def select_hw(dom):
    entries = dom.findall('entry')
    for e in entries:
        hw = e.find(f'.//hw')
        if hw is None:
            hw = e.find(f'.//var')
        # add a headword element if there isn't one already
        if hw is None:
            hw_to_use = ET.Element('hw')
            found = False
            for tag in 'mar tag sya'.split(' '):
                hw = e.find(f'.//{tag}')
                if hw is not None:
                    hw_to_use.text = hw.text
                    found = True
                    break
            if not found:
                # there was no headword. use a placeholder
                hw_to_use.text = 'placeholder'
            adjust_hw(hw_to_use)
            e.append(hw_to_use)
        else:
            adjust_hw(hw)
    return dom

def adjust_hw(element):
    hw_text = element.text
    if hw_text == 'placeholder': return
    hw_text = re.split(r'[\-=]', hw_text)
    # nothing to see here
    if len(hw_text) == 1: return
    hw_text = [h for h in hw_text if h != '']
    element.text = hw_text[0]
    del hw_text[0]
    for h in hw_text:
        addnl_hw = ET.Element('suffix')
        addnl_hw.text = h
        element.append(addnl_hw)
    # <hw>( *[=\-])#<prefix>\1</prefix><hw>#;
    # <hw>(.*?)( *[=\-].*?)</hw>#<hw>\1</hw><suffix>\2</suffix>#;
    return


output_string = ET.tostring(update_dom(sys.argv[1], sys.argv[2]), pretty_print=True, encoding='ascii').decode('ascii')
output_file = open(sys.argv[1], 'w')
output_file.write(output_string)
