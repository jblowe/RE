# -*- coding: utf-8 -*-
"""cleanhw.py -- post-process a RE "data" XML file made by Lex2XML.pl (+ addngl.py)

Why a separate step: Lex2XML.pl is a general-purpose converter and should not
know about one project's headword conventions.  This runs after addngl.py (the
same slot in pipeline_manual.sh) and only rewrites each entry's <hw>.

For every <hw>:
  <flag>        e.g. <m> <S> <p> <fa> <ML> <1972:63>  -> <hwsrc>flag</hwsrc>
  (note)        optional segment / alternate word      -> <hwnote>note</hwnote>
  leading ?     uncertain                              -> <hwnote>?</hwnote>
  $word         Nepali/other-language word             -> <hwnote>$word</hwnote>
  stray number                                         -> dropped
  2nd+ words    "w1 w2 w3"                             -> <hw>w1<part>w2</part><part>w3</part></hw>

so hw.text is always the single head word RE already reads (the same trick as
<suffix>); nothing is thrown away, and an engine that wants the other words can
read the <part> children.

usage: cleanhw.py in.xml out.xml [--prefer-primary]
"""
import re, sys, unicodedata
import lxml.etree as ET

VOWEL = re.compile(r"[aeiouəʌɤɔɛɯɨɐæɪʊɑɒœøyɵ]")
PRIMARY = ('sya', 'mar', 'tag')          # the language's own transcription field
TONE = re.compile(r"[⁰¹²³⁴⁵ᴴᴸX]")

def clean(text):
    notes, srcs = [], []
    s = text
    for m in re.findall(r'<([^>]*)>?', s):
        srcs.append(m.strip())
    s = re.sub(r'\s*<[^>]*>?', '', s)
    for m in re.findall(r'\(([^)]*)\)?', s):
        notes.append(m.strip())
    s = re.sub(r'\s*\([^)]*\)?', '', s)
    if re.search(r'(^|\s)\?', s):
        notes.append('?')
        s = re.sub(r'(^|\s)\?\S*', r'\1', s)
    for m in re.findall(r'(?:^|\s)(\$\S*)', s):
        notes.append(m)
    s = re.sub(r'(^|\s)\$\S*', r'\1', s)
    s = re.sub(r'(^|\s)\d+(?=\s|$)', r'\1', s)
    # NFD so accented vowels (tang: á í ō ã ...) still count as vowels
    words = [w for w in s.split() if VOWEL.search(unicodedata.normalize('NFD', w))] or s.split()
    return words, srcs, notes

def process(inp, outp, prefer_primary=False):
    tree = ET.parse(inp)
    n = changed = 0
    for e in tree.getroot().iterfind('entry'):
        hw = e.find('hw')
        if hw is None:
            continue
        n += 1
        text = (hw.text or '').strip()
        if prefer_primary and not TONE.search(text):
            for tag in PRIMARY:
                p = e.find(tag)
                if p is not None and p.text and TONE.search(p.text):
                    text = p.text.strip(); break
        words, srcs, notes = clean(text)
        if not words:
            continue
        if words == [text] and not srcs and not notes and hw.text == text:
            continue
        changed += 1
        suffixes = list(hw)                      # keep existing <suffix> children
        for c in suffixes: hw.remove(c)
        hw.text = words[0]
        for w in words[1:]:
            part = ET.SubElement(hw, 'part'); part.text = w
        for c in suffixes: hw.append(c)
        pos = list(e).index(hw) + 1
        for kind, vals in (('hwsrc', srcs), ('hwnote', notes)):
            for v in vals:
                el = ET.Element(kind); el.text = v
                e.insert(pos, el); pos += 1
    tree.write(outp, encoding='utf-8', xml_declaration=True, pretty_print=True)
    return n, changed

if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    n, c = process(a[0], a[1], '--prefer-primary' in sys.argv)
    print('%s: %d headwords, %d rewritten' % (a[0], n, c))
