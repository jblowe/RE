# -*- coding: utf-8 -*-
import collections

from nltk.corpus import wordnet as wn
import sys
import re
import lxml.etree as ET

root = ET.Element('semantics')
runstats = ET.SubElement(root, 'totals')
glosses = set()
final_glosses = {}
count_found = 0
count_not_found = 0
raw_glosses = 0
lemmata_count = 0
not_found = []

mels = ET.parse(sys.argv[1])
glosses = mels.findall('.//gl')
melids = mels.findall('.//mel')
for i, id in enumerate(melids):
    id.set('id', f'm{i+1:04d}')

for gloss_element in glosses:
    gloss = gloss_element.text
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

    languages = []
    lemmata = collections.defaultdict(list)
    for language in 'eng fra'.split(' '):
        l2 = [l.lemma_names(lang=language) for l in wn.synsets(gloss, lang=language)]
        lemmata[language] = [l for l in l2 if gloss in l][:5]
        if lemmata[language] != []:
            languages.append(language[:2])

    target = None
    if len(languages) > 1:
        target = 'xx'
        print(f'{gloss}')
        # print(f'{gloss} :: {gloss_element.text}')
        for l in lemmata:
            print(f'{l} = {lemmata[l]}')
        print()
    elif len(languages) == 1:
        target = languages[0]

    if target is not None:
        gloss_element.set('{http://www.w3.org/XML/1998/namespace}lang', target)

ET.SubElement(runstats, 'found').set('value', str(count_found))
ET.SubElement(runstats, 'notfound').set('value', str(count_not_found))
ET.SubElement(runstats, 'total').set('value', str(len(final_glosses)))
ET.SubElement(runstats, 'rawglosses').set('value', str(raw_glosses))
ET.SubElement(runstats, 'lemmata').set('value', str(lemmata_count))

output = open(sys.argv[2], 'w')
output.write(
    ET.tostring(mels,
                pretty_print=True,
                xml_declaration=True,
                encoding='utf-8').decode('utf-8')
)

# print('{0}\t{1}'.format(line, ','.join(synonyms)))
# 10 laugh [Synset('laugh.n.01'), Synset('laugh.n.02'), Synset('joke.n.01'), Synset('laugh.v.01')]
# >>> [str(lemma.name()) for lemma in wn.synsets(gloss)[2].lemmas()]
# ['joke', 'gag', 'laugh', 'jest', 'jape']

# wn.synsets('dog', pos=wn.VERB)
# wn.synset('dog.n.01')
