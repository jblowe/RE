# -*- coding: utf-8 -*-

# example usage

from lingpy import *
from pyclics.api import Clics
from pyclics.models import Form
from tqdm import tqdm
import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom
from collections import defaultdict
import re

try:
    root_dir = sys.argv[1]
except:
    print("Please specify a root directory of clics repositories (concepticon-data, glottolog).")
    sys.exit(1)

clics = Clics(root_dir)
graph = clics.load_network('network', 3, 'families').graph
id_gloss = clics.db.fetchall("select distinct concepticon_id, concepticon_gloss from parametertable")
nodenames = {r[0]: r[1] for r in id_gloss}
nameids = {r[1]: r[0] for r in id_gloss}

edges = {}

root = ET.Element('semantics')
counter = 0

for edgeA, edgeB, data in graph.edges(data=True):
    edges[edgeA, edgeB] = (len(data['families']), len(data['languages']), len(data['words']))

# calculate depth 2 colexification sets
def calc(glosses):
    result = defaultdict(list)
    for (nodeA, nodeB), (fc, lc, wc) in sorted(edges.items(), key=lambda i: i[1], reverse=True):
        if nodenames[nodeA] in glosses and nodenames[nodeB] in glosses:
            result[nodenames[nodeA]].append(nodenames[nodeB])
    return result

def output_missing(glosses):
    with open('clics.not_found', 'w') as f:
        for gloss in glosses:
            if gloss not in nameids:
                f.write('{} \n'.format(gloss).lower())

def process_glosses():
    glosses = set()
    def process_gloss(gloss):
        split = re.split('/|,|;', gloss)
        if len(split) != 1:
            for x in split:
                process_gloss(x.strip().strip('*'))
        else:
            gloss = gloss.split(' (')[0]
            gloss = gloss.replace('be ','')
            gloss = gloss.replace('go ','')
            gloss = gloss.replace('être ','')
            glosses.add(gloss.upper())
    for line in sys.stdin:
        line = line.strip()
        gloss = line.split('\t')[0]
        starmatch = re.search(r'\*(\w+)', gloss)
        if starmatch:
            glosses.add(starmatch.group(0)[1:].upper())
        else:
            process_gloss(gloss)
    return glosses

processed = process_glosses()

# TODO make this output the original gloss not the processed one.
output_missing(processed)
# compute nodes restricted to our glosses.
syn_sets = calc(processed)

counter = 0
for (gloss, synonyms) in syn_sets.items():
    counter += 1
    mel = ET.SubElement(root, 'mel', id="clics" + str(counter))
    ET.SubElement(mel, 'gl').text = gloss.lower()
    for synonym in synonyms:
        ET.SubElement(mel, 'gl').text = synonym.lower()

sys.stdout.write(minidom.parseString(ET.tostring(root)).toprettyxml(indent='   '))
