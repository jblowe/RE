# -*- coding: utf-8
import sys
import lxml.etree as ET


def select_gloss(xml_filename, gloss_band):
    dom = ET.parse(xml_filename)
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


output_string = ET.tostring(select_gloss(sys.argv[1], sys.argv[2]), pretty_print=True, encoding='ascii').decode('ascii')
output_file = open(sys.argv[1], 'w')
output_file.write(output_string)
