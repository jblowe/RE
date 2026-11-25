# TGTM: why 3,284 forms fail, and where the isolates could go

*2026-11-21. Baseline = run `TGTM.20261117-103819` (ToC `C794-rev1`, fuzzy, hand MEL, strict):
858 sets / 2,030 isolates / 3,284 failures, 7,863 forms; 2,528 forms (32%) in sets.
All experiments were done on a **sandbox copy** of the TGTM project (nothing in
`RE-Tamangish-Files/TGTM` was touched); the baseline reproduced exactly (858 / 2030 / 3284).
Each run takes ~6 s, so every number below is measured, not estimated.*

## 1. Waterfall (strict, hand MEL, cumulative)

| step | sets | isolates | failures | forms in sets |
|---|---|---|---|---|
| Nov-17 run as is | 858 | 2,030 | 3,284 | 2,528 |
| + strip whitespace from headwords (**engine bug**, `read.py`, applied) | 942 | 2,177 | 2,854 | |
| + your Nov-20 `fuzzy` file (mar/syang tones → `˥`/`˩`) | 983 | 2,200 | 2,557 | |
| + canon allows 2–3 syllables (tone on 1st only) | 999 | 3,610 | 1,120 | |
| + drop `<tag>` and `(…)` annotations from headwords | 1,003 | 3,666 | 1,035 | |
| + tag `kʰ` (c102/c103), fill c138 `ʈʰ` | 1,004 | 3,679 | 1,017 | 3,141 (40%) |

Failures fall 3,284 → 1,017 (−69%); forms in sets 32% → 40%. The big caveat is the isolate column:
rescued polysyllables mostly become **isolates**, not set members (see §3).

## 2. What is wrong, ranked by forms affected

1. **Trailing space in headwords (engine bug): 475 forms (473 tuk).** `<hw>¹hə <suffix>-nə</suffix></hw>`;
   `entry.find('hw').text` stops at the child element and returns `'¹hə '`. Fixed in
   [read.py](../src/read.py) (`.strip()`); committed 2026-11-23. Zero padded forms ever reconstructed, so this was
   pure loss. Rescues ~430 forms and gives +84 sets by itself.
2. **The ToC is a monosyllable model: ~1,670 failures.** Canon `T?(OG?|IL?G?)?(R|VF)` admits one
   syllable. Of 7,863 forms, monosyllables are in sets 54% of the time; 2-syllable forms 4 of 1,557
   times (1%). Initial consonants carry `contextL` A/B (the tone), so a second-syllable consonant can
   never satisfy it. One-line canon change (sandbox): `T?(OG?|IL?G?)?(R|VF)((OG?|IL?G?)?(R|VF)){0,2}`
   rescues 1,437 forms. It is a research decision, not a bug fix: it asserts that later syllables are
   just toneless copies of the same inventory. **ris (815), tuk (331), syang (413) are the languages affected.**
3. **Mar/syang fuzzy output vs ToC tone cells.** The Nov-17 fuzz mapped mar/syang tones to `ᴴ`/`ᴸ`,
   but ToC c1/c2 have `˥` only for those languages (`ᴴ` only in c4), so every voiceless-initial form
   died on its tone. Your Nov-20 fuzz file already fixes this (−297 failures). Mar's low-tone group goes to `³`, but
   **both** high groups (`⁵⁴ ⁵¹ ⁵³ ⁵²…` and `⁴³ ⁴⁴ ⁴⁵ ⁵⁵…`) go to `˥`; check that is intended.
4. **Multiword / phrase headwords: 364 forms**, never reconstructable (`¹cĩ ¹tʰẽ`, `¹krup ¹krup`).
   Needs a policy (split into words, or exclude), not a ToC edit.
5. **Annotation noise in headwords: ~85 forms**: `<m>`, `<FTB>`, `<sM / mM>`, `(…)`, dangling `(`.
   Stripping rescues them (sandbox hook `_clean_hw`). The `<…>` codes look like source/loan flags; if
   so, route them to a loan filter rather than discarding.
6. **Unmatched tone-sandhi strings, ~100 forms** (mar/syang `⁵⁵'⁴⁴'³³po`): the fuzz lists exact
   2-tone combinations; 3-tone strings and unlisted pairs leave a literal `'`. Needs more fuzz rows.
   Taking only the first tone is **wrong**: `⁵⁵'³³` is ᴴ but `⁵⁵` alone is ᴸ for mar.
7. **Inventory gaps (small each)**:
   - **c138 `*ʈʰ` has `?` for every language**: any `ʈʰ` form is dead.
   - tag has no `kʰ` (c102/c103 give `h`): 42 forms.
   - nasal vowels (`õ` etc. are base + U+0303): few ToC rows carry them. ~100 forms (gha, ris, syang, pra).
   - gha final `-r/-n/-m/-l/-ŋ` rimes (`kʰin`, `lom`, `aːr`): ~50 forms fail with *Syllable structure
     not satisfied*; there are F rows only for k, t, p, l, s.
   - gha `ᴴ` tone (17 forms) has no ToC cell; others: tag `ɛ`, `ɕ`, `c`, mar `ɛ`, `ʱ`, syang `ᴜ`, `ɔ`, `æ̃`, ris `⁰`, `,`.
8. **Context failures (left/right) on monosyllables: ~120**, mostly gha (`²bi`: `b` requires left context B,
   gets `²`→B but then right context `U` fails). Needs a phonologist's eye, not a mechanical fix.

## 3. Isolates (best configuration: 3,679)

| group | n | what it means |
|---|---|---|
| no sound-only partner at all | 1,492 | 1,295 are 2+ syllable (ris 832, tuk 284, syang 223). The ToC has no medial-syllable correspondences, so a disyllable rarely lines up with another language's reconstruction. |
| sound-only partner(s) exist, none semantically linked | ~1,890 | median 7 candidate partners each, so mostly chance matches |
| of which: strong semantic partner (tier A) | **296** | see below, `docs/tgtm-proposals/isolate-placements-tierA.tsv` |

Strict vs no-MEL on the same ToC: 3,141 forms in sets vs 5,329. About two thirds of the sound-only
candidate sets are gated out by the 673-MEL hand file; most of that is correct (chance matches), some is not.

**Placement scorer** (prototype, `docs/tgtm-proposals/score_isolate_placements.py`; this is approach A in
`SEMANTIC_MATCHING_ALTERNATIVES.md`). For each isolate and each sound-only partner it pools unmerged MELs
(hand-extended-v4, clics, wordnet, stedt-reduced) with `1/log2(1+size)` specificity plus WordNet
shared-synset (English + French via OMW). Tier A = two independent sources including a small MEL,
or a MEL plus a shared synset.

Validation without using the hand MEL as a voter: tier A accepts **59% of pairs your hand MEL links but
only 1.3% of other sound-only pairs** (tiers B/C: no useful discrimination; C was *more* common among
non-hand pairs, so it is discarded). Adding the big `stedtsemkey` MEL as a voter raised recall to 64%
but also false positives to 2.4%, and visibly admitted junk (`of ~ even`), so it is excluded.
Rough pair-level precision for tier A is ~85–90%, a lower bound since some "other" pairs are true.

Result: **296 isolates** (ris 76, syang 55, tuk 47, mar 35, gha 26, tag 20, pra 20, sahu 17) get a
strong partner, taking forms in sets from 3,141 to ~3,437 (44%). Examples that look right: tuk `ᴴkʰa`
neck ~ syang `⁵⁴kʰa` cou; mar `Xmun` nuit ~ tag `³mun` night; syang `²¹nʌː` oreille ~ tuk `³nə` ear;
tuk `ᴴpəj` wool ~ mar `⁵⁴⁵pʌɛ` laine; pra `³ceː` tea ~ mar `³tɕʌʱ` thé. A few are still wrong
(`gha ¹e` "turn back" ~ `tuk ᴴŋi` "day after tomorrow"): review the TSV before accepting any. The TSV
lists pairs only; they are **not** merged into sets (no set-forming code was changed).

## 4. Things I tried that did not help

- **Stripping a leading minor syllable** (a-, Cə-, …) to match roots: sets 1,004 → 1,005, failures up
  (stripped forms now fail). In strict mode the polysyllables' problem is the *MEL*: it was built for
  TGTM roots and has no entries for dictionary-style ris glosses ("kapok tree"). Not a prefix problem.
- **Larger MELs in strict mode** (same ToC): hand 999; hand-extended-v4 1,150; wordnet 1,295; both 1,474;
  merged2 1,663; stedtsemkey 3,354. Set count alone says nothing about precision: see the 296 vs
  `stedtsemkey` junk above.

## 5. Recommended order

1. Keep the `read.py` strip fix (done, uncommitted). Re-run, expect ≈ +430 forms.
2. Decide the polysyllable policy (canon change above, or prefix rows). Biggest single lever, but it
   will move ~1,400 forms into *isolates*, not sets, until the MEL covers their glosses.
3. Decide multiword and `<tag>` policy (hook or reader); 364 + 85 forms.
4. ToC edits: c138 `ʈʰ`, tag `kʰ`, gha `ᴴ`, nasal vowel rows, gha coda rimes, more fuzz rows for tone sandhi.
5. For isolates: review the tier-A TSV; consider pooled scoring in `create_sets` rather than a MEL bucket.

*Not verified:* the repo `read.py` edit was syntax-checked but the full run used the equivalent edit in the
sandbox copy of `src/`; no ToC, fuzz, or data file in `RE-Tamangish-Files` was changed.

## 6. Follow-up experiments (2026-11-23; sandbox only, strict hand MEL unless noted)

Cumulative, each row adds one change. (Denominator grew from 7,863 to 8,255 forms at the "split" step.)

| step | sets | isolates | failures | forms in sets |
|---|---|---|---|---|
| Nov-20 fuzz + committed `read.py` strip fix | 983 | 2,200 | 2,557 | 3,083 |
| + canon allows 2–3 syllables | 999 | 3,610 | 1,120 | 3,107 |
| + headword annotations moved out of `<hw>` (`cleanhw.py`) | 1,003 | 3,667 | 1,034 | 3,136 |
| + multiword headwords: every word becomes a form | 1,031 | 4,158 | 799 | 3,247 |
| + c138 `ʈʰ` fill, tag `kʰ` | 1,032 | 4,171 | 781 | 3,252 |
| + 62 tone-sandhi fuzz rows (mar, syang) | 1,035 | 4,247 | 693 | 3,264 |
| + 57 proposed MEL entries | 1,097 | 4,121 | 693 | 3,388 |
| + 17 more (borderline) | 1,119 | 4,081 | 693 | 3,428 |

**Polysyllable canon.** Strict: only +16 sets and 3,083 → 3,107 forms (9 brand-new sets, 8 monosyllables joining 7 existing sets).
Without a MEL: +59 sets, +98 forms, 88 polysyllabic set members (syang 32, tuk 26, ris 20, mar 8), 35 sets made only of
polysyllables (reduplications and compounds: `tsatsa`, `kʰuku`, `tsʰaːpo`, `tini`). About 1,300 2–3-syllable forms become isolates
because a ris/tuk/syang polysyllable almost never has a same-shape partner. The "2+ syllable forms that reconstructed" in the
Nov-17 run were 2 forms (syang `kʰuju`): `c19` proto rime `uiu` has the cell `uju`, which is one syllable, not two.
Eight monosyllables joined sets only because the looser canon lets a final `j` be read as a second syllable (`pʰəj`, `kʰəj`);
check those. After splitting these into morphemes the 2-syllable isolates should be re-run.

**Multiword headwords** (767 after cleaning; syang 244, ris 54, pra 53; tang's 410 are not in this reconstruction).
First word only 1,020 sets, last word only 1,014, all words 1,031. The new sets are mostly right (`hai` how, `ti` begin,
`tʰiŋ` palm) but each word inherits the whole phrase gloss, so some are noise (syang `koi` "pain fait avec pâte" ~ tag `ho` burn).

**Headword annotations (pipeline).** Only ~85 forms; they look like source or loan flags. Suggested home: a small post-processor
after `addngl.py` in `pipeline_manual.sh` (`tgtm-proposals/cleanhw.py`), so `Lex2XML.pl` stays generic. It moves `<m>`, `<S>`, `(…)`, `?`,
`$word` into `<hwsrc>` / `<hwnote>` and puts words 2+ in `<part>` children of `<hw>` (the same trick as `<suffix>`).
Run on the data XML with the committed engine it gives 1,020 / 3,905 / 737 (first word); with a 10-line opt-in change to read the
`<part>`s (`tgtm-proposals/read_parts.patch`) it gives 1,031 / 4,158 / 799, identical to the in-engine hook. Separate small bug:
`check_hw` in `addngl.py` prefers `<var>` over `<sya>`/`<mar>`/`<tag>`, so ~42 entries (syang 11, mar 15, tag 16) get a toneless headword
although the primary field has a tone.

**ToC.** 169 `?` cells in 71 of 209 correspondences (syang 44, pra 29, mar 28, tag 26, gha 14, sahu 13, tuk 12, ris 3); 165 are the
only segment in their cell. c138 has 6. Filling c138 with `ʈʰ`: −10 failures, all become isolates (no new set); tag `kʰ`: +1 set, −8
failures. The other 163 look like genuine "unattested" gaps. The bigger ToC gap is rimes: 241 failing forms have a final rime that
no cell offers for that language (syang `am oŋ om ol ʌl an ap`, gha `aːr aːn`, mar `im om ɛm`, sahu `aːr aːl`):
`tgtm-proposals/toc-rime-gaps.tsv`. Also nasal vowels (58 forms, ris and syang polysyllables mostly) and gha `ᴴ` (33 forms).

**Tone-sandhi fuzz.** 62 rows (`tgtm-proposals/fuzzy-tone-proposal.tsv`) rule-derived from the existing rows: mar low first tone `³`, else `˥`;
syang first tone 4–5 `˥`, 1–2 `˩`, `³⁴` `˥`, `³¹ ³²` `˩`, `³³` and `⁵¹` `X` (as in the current single-tone rows). The 3x/5x cases are guesses.

**MEL additions.** The hand MEL has no entry for e.g. salt, shadow, pillar, yesterday, meadow, today, tea. Of 2,535 sound-only
member pairs the hand MEL does not link, 102 have strong evidence (identical gloss, or WordNet synset plus a small MEL elsewhere) and
25 are borderline. They merge into 57 + 17 entries (`tgtm-proposals/TGTM.mel-additions*.xml`, evidence in `mel-additions-pairs.tsv`).
Spot check of 22 new sets: 19 look right; 3 are questionable (tea set with the `vautour` homophone, slave with `thumb`, particle `not`).
The other ~2,400 unlinked pairs have no evidence of any kind and are probably chance matches.
