# -*- coding: utf-8 -*-

import sys
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
import csv
from collections import defaultdict
from compute_gloss import compute_gloss

root = ET.Element('semantics')
runstats = ET.SubElement(root, 'totals')
tag_dico = defaultdict(set)



# make a dictionary of stedt sets and the glosses of supporting forms
with open(sys.argv[1], "r", newline="", encoding="utf-8") as src:
    r = csv.reader(src, delimiter="\t")
    for row in r:
        analysis = row[6]
        gloss = row[3]
        for a in analysis.split(','):
            try:
                tag = int(a)
                [tag_dico[tag].add(compute_gloss(g)) for g in gloss.split('/')]
            except Exception:
                pass

gloss_count = 0
# write out mels
for n, tag in enumerate(sorted(tag_dico)):
    mel = ET.SubElement(root, 'mel', id=f"stedt{tag}")
    glosses = tag_dico[tag]
    gloss_count += len(glosses)
    for synonym in sorted(glosses):
        sub = ET.SubElement(mel, 'gl')
        sub.text = synonym

ET.SubElement(runstats, 'found').set('value', str(n))
ET.SubElement(runstats, 'total').set('value', str(len(tag_dico)))
ET.SubElement(runstats, 'glosses').set('value', str(gloss_count))

sys.stdout.write(minidom.parseString(ET.tostring(root)).toprettyxml(indent='  '))
