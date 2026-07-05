#!/usr/bin/env python3
"""Compare normalize_gloss_legacy vs normalize_gloss (the active pipeline)
on real data.

Reads two static gloss lists (this directory, generated from TGTM -- see
GLOSS_NORMALIZATION.md for how and why):
  - tgtm_reflex_glosses.txt: distinct glosses from TGTM's ten attested
    lexicons, one per line, source='reflex'
  - tgtm_mel_glosses.txt:    distinct glosses from TGTM.hand-extended-v4.mel.xml
    (an external MEL file, not part of this repo, that tags some glosses
    with xml:lang), one per line, optionally "gloss<TAB>lang", source='mel'

For each gloss, runs both normalize_gloss_legacy(gloss) and
normalize_gloss(gloss) -- lang is read from the mel file where known, else
None (neither file is tagged consistently enough to always have one -- see
GLOSS_NORMALIZATION.md).

Writes a TSV: seq, source, gloss, score, legacy_count, legacy_result,
new_count, new_result.

legacy returns a plain, non-deduplicated list and normalize_gloss returns a
deduplicated tuple, in a different order (normalize_gloss groups phrases
first, then phrasal verbs, then words), so a direct `==` would call almost
everything different even when they agree on substance. Both are instead
treated as a *set* of candidate strings (a "bag of keyterms"), ignoring
container type, order, and duplicates:

  - `score` is the Jaccard similarity of the two sets --
    |intersection| / |union| -- 1.0 when they found exactly the same
    keyterms, 0.0 when they share none, and something in between when they
    partially overlap.
  - `legacy_count`/`new_count` are the number of *unique* keyterms each
    function produced for this gloss (not the raw list length -- legacy's
    list can contain duplicates).

Usage:
    python3 compare_normalize_gloss.py <output.tsv>
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mel  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REFLEX_GLOSSES_FILE = os.path.join(HERE, 'tgtm_reflex_glosses.txt')
MEL_GLOSSES_FILE = os.path.join(HERE, 'tgtm_mel_glosses.txt')


# A handful of real gloss strings contain a literal embedded tab (a data
# artifact, e.g. "a\tfraction, to divide") -- indistinguishable from our own
# "gloss<TAB>lang" separator unless we're picky about what a lang code looks
# like. Only split on the *last* tab, and only if what follows is actually
# a known code; otherwise treat the whole line, tab and all, as the gloss.
_KNOWN_LANG_CODES = {'en', 'fr', 'xx'}


def _read_gloss_file(path):
    """Yield (gloss, lang) pairs; lang is None when the line has no
    trailing <TAB><code> for a known code in _KNOWN_LANG_CODES."""
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line:
                continue
            if '\t' in line:
                gloss, lang = line.rsplit('\t', 1)
                if lang in _KNOWN_LANG_CODES:
                    yield gloss, lang
                    continue
            yield line, None


def _jaccard(legacy, new):
    """Jaccard similarity of the two results, treated as sets of keyterms:
    |intersection| / |union|. 1.0 if identical (including both empty --
    vacuously "the same"), 0.0 if they share nothing."""
    a, b = set(legacy), set(new)
    union = a | b
    if not union:
        return 1.0
    return len(a & b) / len(union)


def main(out_path):
    reflex_rows = [('reflex', g, lang) for g, lang in _read_gloss_file(REFLEX_GLOSSES_FILE)]
    mel_rows = [('mel', g, lang) for g, lang in _read_gloss_file(MEL_GLOSSES_FILE)]
    print(f'{len(reflex_rows)} reflex glosses, {len(mel_rows)} mel glosses')

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('seq\tsource\tgloss\tscore\tlegacy_count\tlegacy\t'
                 'new_count\tnew\n')
        for seq, (source, gloss, lang) in enumerate(reflex_rows + mel_rows, start=1):
            legacy = mel.normalize_gloss_legacy(gloss)
            new = mel.normalize_gloss(gloss, lang)
            score = _jaccard(legacy, new)
            f.write(f'{seq}\t{source}\t{gloss}\t{score:.3f}\t'
                     f'{len(set(legacy))}\t{legacy}\t'
                     f'{len(set(new))}\t{new}\n')

    print(f'{len(reflex_rows) + len(mel_rows)} rows written to {out_path}')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1])
