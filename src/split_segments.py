# attempt to generate a ToC from tabular data based on
# a prior segmentation of forms based on segment classes

# this version segments into Onset + Rime

import csv, sys, re
from collections import defaultdict
from typing import Iterable, Sequence, Any, List, Set

# these are for for M. Jacque's Kiranti table, YMMV

# segment inventory
c = 'ŋŋɦɓbcdɗghjklmnpqrstwzʰʔʣʦ'
v = 'aeiouuʊɛːɨɔAôˀ'
f = 'st'
SYLLABLE_CANON = rf'^([{c}]*)([{v}]+)([{c}]*?)([{f}])?\b'
CONSTITUENT_TYPES = 'I V F S'.split(' ')
PROTO_LANGUAGE = 'PK'
DAUGHTER_LANGUAGES = 'wambule khaling bantawa limbu'
DATA_COLS = [3, 5, 8, 11]

correspondences = defaultdict(list)


# a desperate hack to decide what to use as a proto-constituent
def majority_rules(row):
    non_empty_constituents = set(row)
    if '' in non_empty_constituents: non_empty_constituents.remove('')
    majority = max(non_empty_constituents, key=row.count)
    return majority


def parsew(s):
    if s:
        m = re.match(SYLLABLE_CANON, s)
        if m:
            result = [x for x in m.groups()]
            if result[3] is None:
                result[3] = '0'
            return result
        else:
            print('no parse', s)
            return [''] * 4
    else:
        return [''] * 4


def merge_correspondences(rows: Iterable[Sequence[Any]], empties: Set[Any] = {"", None}) -> List[List[Any]]:
    """Merge equal-length rows; empties are wildcards. Drop subsets, keep maximal reps."""

    def is_empty(v):
        return v in empties

    groups: List[List[Any]] = []
    for row in rows:
        row = list(row)
        placed = False
        for g in groups:
            # incompatible if any position has two non-empty unequal values
            if any((not is_empty(a)) and (not is_empty(b)) and a != b for a, b in zip(g, row)):
                continue
            # merge: fill group's empties from row
            for i, (a, b) in enumerate(zip(g, row)):
                if is_empty(a) and not is_empty(b):
                    g[i] = b
            placed = True
            break
        if not placed:
            groups.append(row)
    return groups


with open(sys.argv[1], "r", newline="", encoding="utf-8") as src:
    with open(f'{sys.argv[2]}.data.parsed.csv', "w", newline="", encoding="utf-8") as dst:
        w = csv.writer(dst, delimiter="\t", lineterminator="\n")
        r = csv.reader(src, delimiter="\t")
        for i, row in enumerate(r):
            words = [row[i] for i in DATA_COLS]
            out = []
            correspondence = defaultdict(list)
            for word in words:
                out.append(word)
                parsed_form = parsew(word)
                # if the F was parsed as an S,  move it to the left
                if parsed_form[2] == '' and parsed_form[3] != '0' and parsed_form[3] != '':
                    parsed_form[2] = parsed_form[3]
                    parsed_form[3] = '0'
                    print(parsed_form)
                out = out + parsed_form
                [correspondence[CONSTITUENT_TYPES[c]].append(parsed_form[c]) for c in range(4)]
            [correspondences[c].append(correspondence[c]) for c in CONSTITUENT_TYPES]
            w.writerow([str(i)] + out)

toc_header = f'N Chron Type {PROTO_LANGUAGE} context {DAUGHTER_LANGUAGES}'.split(' ')
with open(f'{sys.argv[2]}.correspondences.csv', "w", newline="", encoding="utf-8") as dst:
    w = csv.writer(dst, delimiter="\t", lineterminator="\n")
    w.writerow(toc_header)
    n = 1
    for slot in CONSTITUENT_TYPES:
        merged_corrs = merge_correspondences(correspondences[slot])
        # merged_corrs = merge_correspondences(correspondences[slot])
        for i, segments in enumerate(merged_corrs):
            segments = [s if s else '?' for s in segments]
            pk = majority_rules(segments).upper()
            toc_left_side = [f'{str(n + i)}', '1', f'{slot}', f'{pk}', '?']
            w.writerow(toc_left_side + segments)
        n += i
