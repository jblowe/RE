#!/usr/bin/env python3
"""Generate the two static input gloss lists used by eval_normalize_gloss.py
and compare_normalize_gloss.py: tgtm_reflex_glosses.txt and
tgtm_mel_glosses.txt (both written to this directory). See
GLOSS_NORMALIZATION.md for why these exist.

This is the one script in this group that *does* depend on the external
TGTM project directory (~/GitHub/RE-Tamangish-Files/TGTM, not part of this
repo) -- it's the one-time (or rerun-when-the-source-data-changes) step that
turns that external, personal-machine-only data into the two plain-text
files checked into src/, so the eval/compare scripts themselves don't need
that directory at all.

Usage:
    python3 generate_tgtm_gloss_lists.py
"""
import sys
import os
import glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import read   # noqa: E402
import utils  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TGTM_DIR = os.path.expanduser('~/GitHub/RE-Tamangish-Files/TGTM')
MEL_FILE = os.path.join(TGTM_DIR, 'TGTM.hand-extended-v4.mel.xml')

REFLEX_GLOSSES_FILE = os.path.join(HERE, 'tgtm_reflex_glosses.txt')
MEL_GLOSSES_FILE = os.path.join(HERE, 'tgtm_mel_glosses.txt')


def generate_reflex_glosses():
    """Distinct glosses from TGTM's attested lexicons, one per line."""
    paths = sorted(glob.glob(os.path.join(TGTM_DIR, 'TGTM.*.data.xml')))
    lexicons = {}
    for p in paths:
        lex = read.read_lexicon(p)
        lexicons[lex.language] = lex
    reflex_glosses = sorted(utils.all_glosses(lexicons))
    with open(REFLEX_GLOSSES_FILE, 'w', encoding='utf-8') as f:
        for g in reflex_glosses:
            f.write(g + '\n')
    print(f'{len(reflex_glosses)} reflex glosses -> {REFLEX_GLOSSES_FILE}')


def generate_mel_glosses():
    """Distinct glosses from TGTM.hand-extended-v4.mel.xml, one per line,
    with xml:lang preserved as a second tab-separated column where known
    (see mel.Mel.gloss_langs)."""
    mels = read.read_mel_file(MEL_FILE)
    gloss_lang = {}
    for m in mels:
        for g in m.glosses:
            gloss_lang.setdefault(g, m.gloss_langs.get(g))
    with open(MEL_GLOSSES_FILE, 'w', encoding='utf-8') as f:
        for g in sorted(gloss_lang):
            lang = gloss_lang[g]
            f.write(f'{g}\t{lang}\n' if lang else f'{g}\n')
    tagged = sum(1 for lang in gloss_lang.values() if lang)
    print(f'{len(gloss_lang)} mel glosses ({tagged} with xml:lang) -> {MEL_GLOSSES_FILE}')


if __name__ == '__main__':
    generate_reflex_glosses()
    generate_mel_glosses()
