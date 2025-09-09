# -*- coding: utf-8
import sys
import lxml.etree as ET
import re


def update_dom(xml_filename):
    dom = ET.parse(xml_filename)
    dom = change_tags(dom)
    return dom

def change_tags(dom):
    entries = dom.findall('entry')
    root = dom.getroot()
    language = root.get('dialecte')
    root = ET.Element('add')
    for e in entries:
        doc = ET.SubElement(root, 'doc')
        id = e.get('id')
        ET.SubElement(doc, 'field', attrib={'name': 'id'}).text = id
        ET.SubElement(doc, 'field', attrib={'name': 'language_s'}).text = language
        for t in e.findall('*'):
            if t.tag == 'sub':
                ET.SubElement(doc, 'field', attrib={'name': f'{t.tag}_ss'}).text = t.text
                continue
            ET.SubElement(doc, 'field', attrib={'name': f'{t.tag}_ss'}).text = t.text
    return root

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


output_string = ET.tostring(update_dom(sys.argv[1]), pretty_print=True, encoding='utf-8').decode('utf-8')
output_file = open(sys.argv[2], 'w')
output_file.write(output_string)
