# -*- coding: utf-8 -*-

from nltk.corpus import wordnet as wn
import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom

root = ET.Element('semantics')
counter = 0

with open('wn.not_found', 'w') as not_found:
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
            not_found.write('{} \n'.format(orig))
        synonyms = {}
        for lemma in lemmas:
            for l in lemma:
                synonyms[l.name()] = 1
        for synonym in synonyms:
            counter += 1
            mel = ET.SubElement(root, 'mel', id="wn" + str(counter))
            ET.SubElement(mel, 'gl').text = gloss
            ET.SubElement(mel, 'gl').text = synonym

sys.stdout.write(minidom.parseString(ET.tostring(root)).toprettyxml(indent='   '))
        
    # print('{0}\t{1}'.format(line, ','.join(synonyms)))
    # 10 laugh [Synset('laugh.n.01'), Synset('laugh.n.02'), Synset('joke.n.01'), Synset('laugh.v.01')]
    #>>> [str(lemma.name()) for lemma in wn.synsets(gloss)[2].lemmas()]
    #['joke', 'gag', 'laugh', 'jest', 'jape']

#wn.synsets('dog', pos=wn.VERB)
#wn.synset('dog.n.01')
