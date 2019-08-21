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
    all_colexified_glosses = set()
    for (nodeA, nodeB), (fc, lc, wc) in sorted(edges.items(), key=lambda i: i[1], reverse=True):
        A = nodenames[nodeA]
        B = nodenames[nodeB]
        if A in glosses and B in glosses:
            result[A].append(B)
            all_colexified_glosses.add(A)
            all_colexified_glosses.add(B)
        elif A in glosses and A not in result:
            result[A] = []
        if B in glosses and B not in result:
            result[B] = []
    return result, all_colexified_glosses

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
            gloss2 = gloss.replace('-','')
            if gloss2 != gloss:
                glosses.add(gloss2.upper())

    # f = open(sys.argv[2], 'r')
    # for raw_gloss_count, line in enumerate(f):
    for raw_gloss_count, line in enumerate(sys.stdin):
        line = line.strip()
        gloss = line.split('\t')[0]
        starmatch = re.search(r'\*(\w+)', gloss)
        if starmatch:
            glosses.add(starmatch.group(0)[1:].upper())
        else:
            process_gloss(gloss)
    return glosses, raw_gloss_count

processed, raw_glosses = process_glosses()

# compute nodes restricted to our glosses.
syn_sets, all_colexified_glosses = calc(processed)

runstats = ET.SubElement(root, 'totals')
count_found = 0
seen = set()
for (gloss, synonyms) in sorted(syn_sets.items()):
    count_found += 1
    if len(synonyms) == 0 and gloss in all_colexified_glosses: continue
    mel = ET.SubElement(root, 'mel', id="clics" + str(count_found))
    sub = ET.SubElement(mel, 'gl')
    sub.text = gloss.lower()
    if len(synonyms) == 0 and gloss not in all_colexified_glosses:
        sub.set('singleton', 'yes')
    for synonym in sorted(synonyms):
        ET.SubElement(mel, 'gl').text = synonym.lower()

count_not_found = 0
for gloss in sorted(processed):
    # TODO make this output the original gloss not the processed one.
    if gloss not in nameids:
        count_not_found += 1
        mel = ET.SubElement(root, 'mel', id="nf" + str(count_found + count_not_found))
        sub = ET.SubElement(mel, 'gl')
        sub.text = gloss.lower()
        sub.set('pivot', 'notfound')

ET.SubElement(runstats, 'found').set('value', str(count_found))
ET.SubElement(runstats, 'notfound').set('value', str(count_not_found))
ET.SubElement(runstats, 'total').set('value', str(count_found + count_not_found))
ET.SubElement(runstats, 'rawglosses').set('value', str(raw_glosses))
ET.SubElement(runstats, 'lemmata').set('value', str(len(processed)))

sys.stdout.write(minidom.parseString(ET.tostring(root)).toprettyxml(indent='   '))
