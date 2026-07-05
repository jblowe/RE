#!/usr/bin/env python3
"""Standalone evaluation script for mel.normalize_gloss.

Does nothing but this: read a list of glosses from an input file, run
normalize_gloss on each, and write gloss + results to an output file. Does
not touch any other part of the pipeline. See GLOSS_NORMALIZATION.md for
the write-up this supports.

Input format: one gloss per line. Optionally "gloss<TAB>lang" to pass an
xml:lang code (e.g. 'en', 'fr') for that line; without a tab, lang=None.
tgtm_reflex_glosses.txt and tgtm_mel_glosses.txt (this directory) are ready
to use as input.

A handful of real gloss strings contain a literal embedded tab (a data
artifact, e.g. "a\tfraction, to divide") -- indistinguishable from our own
separator unless we're picky about what a lang code looks like. Only the
*last* tab is considered, and only if what follows looks like a real code
(2-3 lowercase letters); otherwise the whole line, tab and all, is the
gloss and lang=None.

Usage:
    python3 eval_normalize_gloss.py <input_file> <output_file>
"""
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mel  # noqa: E402

_LANG_CODE_RE = re.compile(r'[a-z]{2,3}')


def main(in_path, out_path):
    with open(in_path, encoding='utf-8') as f_in, \
         open(out_path, 'w', encoding='utf-8') as f_out:
        for line in f_in:
            line = line.rstrip('\n')
            if not line:
                continue
            gloss, lang = line, None
            if '\t' in line:
                head, tail = line.rsplit('\t', 1)
                if _LANG_CODE_RE.fullmatch(tail):
                    gloss, lang = head, tail
            result = mel.normalize_gloss(gloss, lang)
            f_out.write(f'{gloss}\t{lang or ""}\t{result}\n')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
