# -*- coding: utf-8 -*-
"""list_multiword_hw.py -- list headwords made of 2+ words in a project's data XML files.

Annotations (<flags>, (notes), ?, $nepali, stray numbers) are NOT counted as
words; cleanhw.clean() strips them first, so "ɲaŋ <m>" is one word but
"ɖʰaː ɖʰaː" is two.  The 'form' column is the cleaned multiword form; 'note'
holds any stripped annotations (<flags> in angle brackets, (notes), ?, $words).

usage: list_multiword_hw.py out.csv data1.xml data2.xml ...
"""
import csv, sys, unicodedata
import lxml.etree as ET
from cleanhw import clean

def rows(path):
    root = ET.parse(path).getroot()
    lang = root.attrib.get('dialecte')
    for e in root.iterfind('entry'):
        hw = e.find('hw')
        if hw is None:
            continue
        raw = (hw.text or '').strip()
        words, srcs, notes = clean(raw)
        if len(words) < 2:
            continue
        ngl, gl = e.find('ngl'), e.find('gl')
        gloss = ngl.text if ngl is not None else (gl.text if gl is not None else '')
        yield [lang, ' '.join(words), (gloss or '').strip(), e.attrib.get('id'),
               '; '.join(['<%s>' % x for x in srcs] + notes), len(words)]

if __name__ == '__main__':
    out, files = sys.argv[1], sys.argv[2:]
    n = {}
    with open(out, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['language', 'form', 'gloss', 'id', 'note', 'n_words'])
        for p in files:
            for r in rows(p):
                w.writerow([unicodedata.normalize('NFC', str(x)) for x in r])
                n[r[0]] = n.get(r[0], 0) + 1
    print(n, sum(n.values()))
