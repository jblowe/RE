# -*- coding: utf-8 -*-

from nltk.corpus import wordnet as wn
import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom

root = ET.Element('semantics')
count_found = 0
count_not_found = 0
not_found = []

for line in sys.stdin:
    line = line.strip()
    gloss = line.split('\t')[0]
    orig = gloss
    gloss = gloss.split('/')[0]
    gloss = gloss.split(' (')[0]
    gloss = gloss.replace('be ','')
    gloss = gloss.replace('go ','')
    gloss = gloss.replace('être ','')
    gloss = gloss.replace(' ','_')
    #print('{0}\t{1}'.format(line, wn.synsets(gloss)))
    lemmas = [l.lemmas() for l in wn.synsets(gloss)]
    if len(lemmas) == 0:
        lemmas = [l.lemmas() for l in wn.synsets(gloss, lang='fra')]
    if lemmas == []:
        #not_found.write('{} \n'.format(orig))
        count_not_found += 1
        not_found.append(gloss)
        continue
    synonyms = {}
    for lemma in lemmas:
        for l in lemma:
            synonyms[l.name().replace('_',' ')] = 1
    count_found += 1
    mel = ET.SubElement(root, 'mel', id="wn" + str(count_found))
    pivot_set = False
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
for gloss in sorted(not_found):
    count_found += 1
    mel = ET.SubElement(root, 'mel', id="wn" + str(count_found))
    sub = ET.SubElement(mel, 'gl')
    sub.text = gloss.replace('_',' ')
    sub.set('pivot', 'notfound')

sys.stdout.write(minidom.parseString(ET.tostring(root)).toprettyxml(indent='   '))
        
    # print('{0}\t{1}'.format(line, ','.join(synonyms)))
    # 10 laugh [Synset('laugh.n.01'), Synset('laugh.n.02'), Synset('joke.n.01'), Synset('laugh.v.01')]
    #>>> [str(lemma.name()) for lemma in wn.synsets(gloss)[2].lemmas()]
    #['joke', 'gag', 'laugh', 'jest', 'jape']

#wn.synsets('dog', pos=wn.VERB)
#wn.synset('dog.n.01')
