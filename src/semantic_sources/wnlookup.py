# -*- coding: utf-8 -*-

from nltk.corpus import wordnet as wn
import sys
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom

root = ET.Element('semantics')
runstats = ET.SubElement(root, 'totals')
glosses = set()
final_glosses = set()
count_found = 0
count_not_found = 0
raw_glosses = 0
lemmata = 0
not_found = []

for line in sys.stdin:
    raw_glosses += 1
    line = line.strip()
    line = line.split('/')
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
    final_glosses.add(gloss)

for gloss in final_glosses:
    # print('{0}\t{1}'.format(line, wn.synsets(gloss)))
    lemmas = [l.lemmas() for l in wn.synsets(gloss)]
    if len(lemmas) == 0:
        lemmas = [l.lemmas() for l in wn.synsets(gloss, lang='fra')]
    gloss = gloss.replace('_', ' ')
    if lemmas == []:
        # not_found.write('{} \n'.format(orig))
        count_not_found += 1
        not_found.append(gloss)
        continue
    synonyms = set()
    for lemma in lemmas:
        for l in lemma:
            synonyms.add(l.name().replace('_', ' '))
    count_found += 1
    mel = ET.SubElement(root, 'mel', id="wn" + str(count_found))
    pivot_set = False
    lemmata += len(synonyms)
    for synonym in sorted(synonyms):
        sub = ET.SubElement(mel, 'gl')
        sub.text = synonym
        if gloss == synonym:
            sub.set('pivot', 'samelg')
            pivot_set = True
    if not pivot_set:
        sub = ET.SubElement(mel, 'gl')
        sub.text = gloss
        sub.set('pivot', 'otherlg')

ET.SubElement(runstats, 'found').set('value', str(count_found))
ET.SubElement(runstats, 'notfound').set('value', str(count_not_found))
ET.SubElement(runstats, 'total').set('value', str(len(final_glosses)))
ET.SubElement(runstats, 'rawglosses').set('value', str(raw_glosses))
ET.SubElement(runstats, 'lemmata').set('value', str(lemmata))

for gloss in sorted(not_found):
    if gloss == '' or gloss is None: continue
    count_found += 1
    mel = ET.SubElement(root, 'mel', id="wn" + str(count_found))
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
