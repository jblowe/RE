# -*- coding: utf-8 -*-

from nltk.corpus import wordnet as wn
import sys
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom

root = ET.Element('semantics')
runstats = ET.SubElement(root, 'totals')
glosses = set()
final_glosses = {}
count_found = 0
count_not_found = 0
raw_glosses = 0
lemmata_count = 0
not_found = []

for line in sys.stdin:
    raw_glosses += 1
    line = line.strip()
    line = line.split('/')
    if line == ['']: break
    for l in line:
        [glosses.add(g.strip()) for g in l.split(', ')]

for gloss in glosses:
    gloss = gloss.split(' (')[0]
    gloss = gloss.replace('*', '')
    gloss = gloss.replace('? ', '')
    gloss = re.sub(r'[\(\)]', '', gloss)
    gloss = re.sub(r'\(.*?to_\)', '', gloss)
    gloss = re.sub(r'^a kind of ', '', gloss)
    gloss = re.sub(r'^a ', '', gloss)
    gloss = re.sub(r'^to ', '', gloss)
    gloss = re.sub(r'^be ', '', gloss)
    gloss = re.sub(r'^become ', '', gloss)
    gloss = re.sub(r'^go ', '', gloss)
    gloss = re.sub(r'^être ', '', gloss)
    gloss = re.sub(r'\(.*?\) +', '', gloss)
    gloss = re.sub(r'\(.*?\)', '', gloss)
    gloss = re.sub(r' +', ' ', gloss)
    gloss = gloss.strip()
    gloss = gloss.replace(' ', '_')
    final_glosses[gloss] = True
    gloss2 = gloss.replace('-', '')
    if gloss2 != gloss:
        final_glosses[gloss2] = True

for gloss in sorted(final_glosses):
    if not final_glosses[gloss]: continue
    # mark this gloss as 'checked' (whether found or not)
    # final_glosses[gloss] = False
    # print('{0}\t{1}'.format(line, wn.synsets(gloss)))
    target = None
    synsets = [l.lemmas() for l in wn.synsets(gloss)]
    # if not found in English, look up gloss in French wordnet
    if len(synsets) != 0:
        target = 'english'
    else:
        synsets = [l.lemmas() for l in wn.synsets(gloss, lang='fra')]
        target = 'french'
    gloss = gloss.replace('_', ' ')
    if synsets == []:
        count_not_found += 1
        not_found.append(gloss)
        continue
    synonyms = set()
    synonyms.add(gloss)
    for lemmata in synsets:
        for l in lemmata:
            if l.name() in final_glosses:
                synonyms.add(l.name().replace('_', ' '))
            # if l.name() in final_glosses:
            #     if final_glosses[l.name()]:
            #         # if we add a gloss to the mel, make a mark so we don't add it again to another mel.
            #         final_glosses[l.name()] = False
            #         synonyms.add(l.name().replace('_', ' '))
    count_found += 1
    mel = ET.SubElement(root, 'mel', id="wn" + str(count_found))
    target = False
    lemmata_count += len(synonyms)
    for synonym in sorted(synonyms):
        sub = ET.SubElement(mel, 'gl')
        sub.text = synonym
        if gloss == synonym:
            sub.set('pivot', 'key')
            target = True
    if not target:
        sub = ET.SubElement(mel, 'gl')
        sub.text = gloss
        sub.set('pivot', 'otherlg')

ET.SubElement(runstats, 'found').set('value', str(count_found))
ET.SubElement(runstats, 'notfound').set('value', str(count_not_found))
ET.SubElement(runstats, 'total').set('value', str(len(final_glosses)))
ET.SubElement(runstats, 'rawglosses').set('value', str(raw_glosses))
ET.SubElement(runstats, 'lemmata').set('value', str(lemmata_count))

for gloss in sorted(not_found):
    if gloss == '' or gloss is None: continue
    count_found += 1
    mel = ET.SubElement(root, 'mel', id="nf" + str(count_found))
    sub = ET.SubElement(mel, 'gl')
    sub.text = gloss.replace('_', ' ')
    sub.set('pivot', 'notfound')

sys.stdout.write(minidom.parseString(ET.tostring(root)).toprettyxml(indent='   '))

# print('{0}\t{1}'.format(line, ','.join(synonyms)))
# 10 laugh [Synset('laugh.n.01'), Synset('laugh.n.02'), Synset('joke.n.01'), Synset('laugh.v.01')]
# >>> [str(lemma.name()) for lemma in wn.synsets(gloss)[2].lemmas()]
# ['joke', 'gag', 'laugh', 'jest', 'jape']

# wn.synsets('dog', pos=wn.VERB)
# wn.synset('dog.n.01')
