# TGTM, TGTM94SETS and DEMO93: comparing the MEL files (2026-11-24, revised 2026-11-25)

All experiments ran in a scratchpad sandbox. Nothing in `RE-Tamangish-Files` or `src/` was changed.
The full per-file table is [tgtm-proposals/mel-stats.csv](tgtm-proposals/mel-stats.csv).

## Summary

- There are **45 MEL files** (41 distinct): 17 in `TGTM`, 20 in `TGTM94SETS` and 8 in `DEMO93`. They form three families: the
  **hand** family (hand, enriched, extended), the **STEDT** family (stedt6–9, merged) and the **external-resource** family
  (CLICS, WordNet, EvoSem).
- **Two different "hand" MELs exist.** `TGTM/TGTM.hand.mel.xml` has de-accented French glosses (`abces`, `derriere`, `mur`:
  57 glosses in 50 MELs; 85 of the 673 MELs differ in some way). `TGTM94SETS/TGTM.hand.mel.xml` is accented. The engine does not fold accents, so the TGTM version
  silently misses accented data glosses.
- **The hand MEL covers only 69.5% of the glosses of the TGTM forms.** In strict mode the rest can never be in a set.
  `hand-extended-v4` covers 98.8%.
- **Decisions (2026-11-24, after review):** no accent folding, ever (the MEL holds the real French and English words); the
  `TGTM/TGTM.hand.mel.xml` file is left alone for now; empty `<gl/>` are skipped by the reader; every gloss gets a `source`
  attribute; both a `broad` and a `conservative` merged MEL are produced, with noise removed; the earlier pair-derived additions
  are merged in (section 4). The accent-fold experiment (section 3) is kept as a result only: its patch was withdrawn.
- **Revision 2026-11-25:** a **variant layer** was added (section 4.3a): a stray gloss such as `brèdes` now joins the one MEL that has
  its singular `brède`, and plural/singular, hyphen and spacing variants are treated the same way (accent differences between two
  real French words are not). The engine is unchanged.
- **Revision 2026-11-25 (later): `hand-extended-v4` is the base.** The first build treated the two hand MELs as the base and v4 as a layer on top; it is now the other way round (section 6.1): every MEL of v4 is kept with its own id (`m0001` …), and the hand glosses inside it are tagged `source="core"`. Without the WordNet layer the sets are identical to the first design (1,214 and 1,088) and no hand94 pair is lost; the MEL counts, ids and some statistics changed. `python make_merged_mels.py broad-hand conservative-hand` rebuilds the first design for comparison.
- **Revision 2026-11-25 (subset merge):** the last step of the build now merges every MEL whose normalized glosses (`mel.normalize_gloss`) are all in one other MEL into that MEL (`fly (v.)` and `to fly` now sit in the MEL of `fly`, `voler`); broad 4,133 → 3,295 MELs, conservative 4,539 → 3,795, with exactly the same sets (section 4.8, 6.5b); hand MELs may be merged into larger MELs.
- **Revision 2026-11-25 (WordNet layer):** a `wordnet` layer translates glosses between French and English through WordNet and adds each to the MELs that hold its translation (`voler` now also sits in the `steal` and `fly` MELs; section 4.7 and 6.5a). Both files have it, tagged `source="wordnet"`. It adds 88 (broad) and 114 (conservative) sets and about 110 / 170 fewer isolates; the numbers in sections 4 and 6 are those of the final build.
- **Result:** the two new files (`TGTM.broad.mel.xml`, `TGTM.conservative.mel.xml`, section 4) give 1,302 and 1,202 sets on TGTM
  (1,214 and 1,088 before the WordNet layer; the TGTM hand MEL: 983), with no folding. More sets is not by itself better and a lower score against the 1994 sets is not
  by itself worse: that reference was built with the hand MEL. Section 4 therefore reports what each layer adds, and lists every
  new or enlarged set for review.

## 1. Statistics

"Glosses" counts every `<gl>`, so a gloss that occurs in several MELs is counted several times.

### TGTM (`RE-Tamangish-Files/TGTM`)

| File | MELs | Glosses | Avg gl/MEL | Notes |
|---|---:|---:|---:|---|
| hand | 673 | 2,489 | 3.70 | de-accented French |
| hand-v2 | 673 | 2,488 | 3.70 | `xml:lang` on 1,973 glosses |
| hand.mel.orig | 673 | 2,487 | 3.70 | before the 16 edits that made `hand` |
| enriched / enriched2 / enriched3 | 673 / 673 / 674 | 3,467 / 3,764 / 4,332 | 5.15 / 5.59 / 6.43 | hand + data-gloss variants |
| hand-extended | 5,688 | 12,118 | 2.13 | hand + one MEL per unmatched data gloss; no `xml:lang` |
| hand-extended-v2 / v3 | 5,688 | 12,118 / 12,102 | 2.13 | adds `xml:lang` (8,313 glosses) |
| hand-extended-v4 | 5,585 | 11,743 | 2.10 | removes `*` duplicates, merges subset MELs; 7,956 tagged |
| hand-extra | 2,012 | 2,012 | 1.00 | singleton MELs only |
| clics | 3,269 | 4,728 | 1.45 | 2,747 singletons |
| wordnet | 3,737 | 9,737 | 2.61 | |
| wordnet2 | 1,945 | 25,321 | 13.02 | merges senses (`sang`, `sing`, `ginseng`) |
| wn-pairs | 43,438 | 86,876 | 2.00 | every WordNet pair, size 2 |
| es-reduced | 8,478 | 57,262 | 6.75 | EvoSem reduced; identical copy in TGTM94SETS |
| both | 2,618 | 27,808 | 10.62 | 4 identical copies (3 in DEMO93) |

### TGTM94SETS

| File | MELs | Glosses | Avg gl/MEL | Notes |
|---|---:|---:|---:|---|
| hand | 673 | 2,502 | 3.72 | accented; the reference for the 1994 sets |
| clics | 2,132 | 2,631 | 1.23 | one empty `<gl pivot="notfound"/>` crashes the engine |
| wordnet | 2,081 | 5,018 | 2.41 | |
| stedt-reduced | 812 | 4,198 | 5.17 | |
| stedt6 / 7 / 8 / 9 | 2,329 / 2,572 / 2,726 / 2,845 | 7,484 / 9,185 / 10,417 / 11,488 | 3.21 / 3.57 / 3.82 / 4.04 | STEDT etyma, capped at N glosses |
| stedt6id / 7id / 8id / 9id | 3,266 / 3,468 / 3,604 / 3,716 | 8,421 / 10,081 / 11,295 / 12,359 | 2.58 / 2.91 / 3.13 / 3.33 | plus one `idNNN` MEL per unmatched data gloss |
| stedt9idmerged | 2,602 | 10,654 | 4.09 | `merge_mels.py` over stedt9id |
| stedt9idmerged-hand | 2,772 | 12,441 | 4.49 | + hand |
| merged1 | 1,725 | 6,661 | 3.86 | clics + stedt-reduced + hand |
| merged2 | 1,982 | 8,614 | 4.35 | + wordnet |
| stedtsemkey | 631 | 73,887 | 117.10 | one MEL per STEDT semantic key; max 6,539 glosses |
| evosem | 24,916 | 178,503 | 7.16 | EvoSem cogsets (`DIS.evosem`) |
| DIS.es-reduced | 55 | 112 | 2.04 | a DIS file; does not belong here |

### DEMO93

| File | MELs | Glosses | Avg gl/MEL |
|---|---:|---:|---:|
| hand | 69 | 72 | 1.04 |
| clics | 61 | 66 | 1.08 |
| wordnet | 74 | 80 | 1.08 |
| both (copy of TGTM's) | 2,618 | 27,808 | 10.62 |
| hand-extra, wn | 0 | 0 | — |

## 2. How the families differ

- **Hand family.** The curated 673-MEL core. `enriched*` adds data-gloss spellings (`abandon/cast away`, `se laver`).
  `hand-extended*` adds one MEL per gloss that otherwise matches nothing, and from v2 on carries `xml:lang`
  (`en`, `fr`, `xx` for ambiguous, or none). All `hand-extended*` files use zero-padded IDs (`m0001…`), so their IDs do not line up with `hand` (`m1`).
- **`hand-extended-v3` → `v4`** (`TGTM/mel_maintenance_v3_to_v4.py`, run against the coverage report of run `TGTM.20260608-165613`). Three steps:
  (1) remove a `*`-prefixed gloss when the same gloss without `*` is in the same MEL (882 `*` glosses in v3, 440 in v4);
  (2) add the glosses the run reported as unmatched, mostly French headwords (`ail`, `arriver`, `vautour`, `corbeau`, `sourd`, `éboulement`), to a MEL chosen by a hand-written French→English keyword table and word overlap;
  (3) merge MELs that became identical to, or a subset of, another one. v3 has 5,688 MELs / 12,102 glosses, v4 has 5,585 / 11,743:
  103 MELs are gone, none is new, 5,032 are unchanged and 553 changed (392 glosses removed, 186 added; 122 gloss strings are new to the file).
  The step-2 placements were not checked one by one. Both files carry the older, partial `xml:lang` tags (a third of the glosses have none).
  `enriched3` (May 2026) is newer than `enriched2` (April) and larger (4,332 against 3,764 glosses); the merged MELs use `enriched2`; `enriched3` was tried on 2026-11-25 and not adopted (4.5a).
- **What the hand MELs have that `hand-extended-v3` / `-v4` lack** (checked 2026-11-25, same result for both). `TGTM94SETS/TGTM.hand.mel.xml` (2,502 glosses): 11 absent even ignoring case, accents and punctuation (`baratter`, `become ripe`, `become tired`, `take rest`, `genre d'épinards`, `s'effondrer`, `faire des petites dépenses`, `s'empêtrer`, `employer`, `lieu de pélerinage`, `moucharder`) and 56 (v3: 58) present only in another spelling (`abcès`, `décorer`, `derrière`, `piège`, `brède` …). `TGTM/TGTM.hand.mel.xml` (2,489): `sarong` and `break clods` absent, `grand-mere` differs. 19 of the 673 94SETS hand MELs are spread over several v4 MELs, because v4 splits multiword glosses (`be born` → `be`, `born`): 113 of the 4,810 gloss pairs inside a hand MEL (2.3%) are never together in any v4 MEL; for the TGTM hand MEL, 22 of 4,753 (0.5%). The merged files write the hand glosses into their MEL as `core`, so none of this is lost.
- **STEDT family.** The MELs are cognate-set-based: each STEDT etymon's glosses form a MEL. They have
  high form coverage only in the `id` variants, which add a singleton per unmatched data gloss. Without that they cover 58–64% of forms.
- **External resources.** CLICS, WordNet, EvoSem and `wn-pairs` are not tailored to these glosses. Alone, they
  recover only about 35–70% of the 1994 pairs (table in §3).
- **`merged1`, `merged2` and `stedt9idmerged-hand`** are `merge_mels.py` outputs. All three contain the hand MEL.
- **DEMO93.** It has a different gloss universe (497 forms, six languages). Its hand MEL is almost all singletons, and `wordnet` gives
  identical results. `both` is TGTM's, not DEMO93's. A merge adds nothing here.

## 3. Results

Strict mode, `C794-rev1`, current `TGTM.fuzzy.fuz.xml`, engine as committed.
**TGTM94SETS** (3,074 forms) is scored against the 1994 sets (`SETS0111-SRT.sets.xml`, 5,755 cross-language form pairs).
**TGTM** (7,863 forms) is scored the same way for pairs between forms that the 1994 sets also contain ("P"). "R" is the share of 1994 pairs found.
`evosem` scores P 0.618 / R 0.408 on TGTM94SETS. Rows use TGTM's copy of a file where both projects have one, except `hand`.
This reference was built with the hand MEL, so it favours hand-like MELs: it guards against regressions, and does not prove that new links are wrong.

| MEL | TGTM sets | TGTM isolates | TGTM P / R | 94SETS sets | 94SETS P / R |
|---|---:|---:|---|---:|---|
| TGTM hand (de-accented) | 983 | 2,200 | 0.981 / 0.827 | 994 | 0.986 / 0.956 |
| 94SETS hand (accented) | 990 | 2,187 | 0.980 / 0.831 | 1,016 | 0.988 / 0.972 |
| hand-extended-v4 | 1,120 | 2,149 | 0.970 / 0.831 | 1,021 | 0.981 / 0.957 |
| enriched2 | 1,180 | 1,951 | 0.960 / 0.846 | 1,035 | 0.974 / 0.967 |
| both | 1,445 | 1,963 | 0.927 / 0.834 | 1,135 | 0.939 / 0.956 |
| wordnet | 1,257 | 2,327 | 0.927 / 0.644 | 878 | 0.926 / 0.612 |
| clics (TGTM's file) | 929 | 2,846 | 0.963 / 0.450 | 750 | 0.942 / 0.346 |
| stedt9idmerged-hand | n/a | n/a | n/a | 1,076 | 0.971 / 0.973 |
| merged2 | n/a | n/a | n/a | 1,313 | 0.886 / 0.974 |
| es-reduced | 2,737 | 1,871 | 0.742 / 0.578 | 1,178 | 0.642 / 0.401 |
| stedtsemkey | n/a | n/a | n/a | 1,565 | 0.322 / 0.430 |


Accent folding in the engine was tried (a symmetric `mel._candidates_lower` change) and gave +4 sets / −9 isolates on TGTM94SETS with
the accented hand MEL, and +24 sets / −65 isolates with the de-accented one. **It was rejected:** the MEL must keep the real French
words, and the loss came from the de-accented TGTM `hand` MEL, not from the data (the French lexicons are accented). The patch has been withdrawn.

Adding the abbreviations `sthg`, `smn`, `become` and similar to the stopwords changed nothing measurable (±2 sets). The two false
links I spotted (`hide sthg` ~ `like sthg`) are not common enough to matter.


## 4. The merged MELs (revised 2026-11-24)

`make_merged_mels.py` writes **`TGTM.broad.mel.xml`** and **`TGTM.conservative.mel.xml`** (the `<project>.<token>.mel.xml`
convention, so `--mel broad` / `--mel conservative` work). Neither is a default; both are proposals. **The base is `TGTM.hand-extended-v4.mel.xml`** (5,585 MELs, ids `m0001` …; it already contains the 673 hand MELs, 94% of them unchanged): every one of its MELs is in both files, and the layers below are added to it.

### 4.1 What is in them

| Layer | `source` | `layer` | In broad | In conservative |
|---|---|---|---:|---:|
| the hand glosses (union of the two hand MELs: 94SETS spellings win; the TGTM-only glosses are added, including your `sarong`), written into the v4 MEL that holds them | core | | 2,504 | 2,496 |
| the other glosses of the v4 MELs (the base: data-driven, one MEL per gloss variant) | extra | `extended` | 5,701 | 6,394 |
| `enriched2` glosses for a hand MEL (only when the two share a gloss) | extra | `enriched` | 1,071 | |
| the 57 pair-derived MELs (`TGTM.mel-additions.xml`) | extra | `pairs` | 36 | 38 |
| the 17 loose pair-derived MELs (`...-loose.xml`) | extra | `pairs-loose` | 32 | |
| a gloss the lexicons use, added to the MELs that hold its WordNet translation (4.7) | **wordnet** | `wordnet` | 2,030 | 2,138 |
| real, accented spelling of a de-accented French gloss | extra | `accent` | 21 | 21 |
| plural / singular / hyphen / spelling variant attached to the MEL that has its partner (4.3a) | extra | `variant` | 24 | 30 |
| **total** | | | **11,419 in 3,295 MELs (avg 3.47)** | **11,117 in 3,795 MELs (avg 2.93)** |

(The core count is below the 2,510 of the hand MELs because merging a hand MEL into another (4.8) collapses gloss strings the two share; every one of the 2,029 distinct hand gloss strings is still there as `core`. The counts are glosses; fewer than in the sources because duplicates, junk and dead glosses were removed, below, and MELs that add nothing (their glosses are all in another MEL) were dropped: 1,248 in broad, 807 in conservative. 663 (conservative) or 667 (broad) of the MELs hold hand glosses.)
The pair-derived additions were already in the first merged files; they are now tagged, and the loose ones are kept but marked `pairs-loose`.

### 4.2 Attributes on every `<gl>`

- `xml:lang` = `en`, `fr` or `und`. **`und`** is the BCP 47 code for *undetermined*; it is used where the string is a word in both
  languages (`sari`, `pot`, `pain`, `attention`, `chair`) or nothing says which. The repo's older placeholder `xx` is no longer written
  (`compare_normalize_gloss.py` accepts both). Every gloss is tagged: 118 core and 100 (broad) or 98 (conservative) other glosses are `und`.
  How the tag is chosen (`gloss_lang.py`): (1) which lexicons use the string as a gloss. The French lexicons are mar, syang and tang, the
  English ones gha, pra, ris, sahu, tag and tuk; each data gloss is first classified by its own words, because the French lexicons contain some English glosses;
  a string used by both languages is `und`. (2) French/English stopwords and accents. (3) WordNet, asking which language is *predominant*, since WordNet-fra lists many English words.
  (4) the tag already in the source file counts as one more vote; a tie is `und`.
  This is a heuristic: expect some wrong tags, mostly on short words.
- `source` = `core` (curated by hand), `extra` (added by the script from the other MEL files) or `wordnet` (added by the WordNet layer, 4.7). It can take more values later (`concepticon` …).
- `confidence` (WordNet glosses only) = `high` or `low` (4.7). **The engine does not read it** (`read.read_mel_file` reads only `xml:lang` and `source`, and `source` is stored but not used), so every gloss, low confidence included, takes part in matching and in making sets.
- `layer` (extras only) = why the gloss is there (table above). This is extra to what you asked for; drop it if you prefer.

The engine reads `source` (`read.read_mel_file` → `Mel.gloss_sources`) but does not use it yet; nothing is shown in the panes.

**Output order and ids.** The two files list the glosses of each MEL in alphabetical order and the MELs in alphabetical order of their first gloss (case, accents and a leading `*` or `(` are ignored for the order only; no gloss is changed). Ids have at least four digits (`m0001`, `p0002`, `q0007`); the ids that were not padded (the hand MEL `m675`, the pair MELs `p…`, `q…`) are in `mel-id-changes-*.tsv`.

### 4.3 Accents

Nothing is folded anywhere in the output. 31 French glosses in the hand MELs (and 1 extra) are de-accented (`jete`, `eviter`, `appetit`,
`naitre`, `abces` …) and have exactly one known accented spelling (from the French WordNet or the French lexicons). Where the MEL did not
already hold it, the real spelling is added next to the hand gloss as `layer="accent"` (21 glosses; the full list is
`mel-accent-restorations-broad.tsv`); the de-accented hand glosses stay, since the hand MEL is not rewritten. Extras are corrected in place.
Words with two possible accented spellings (`eleve`: `élevé`, `élève`) are left alone.
(`fold()` in the script is used only to decide whether two *candidate* MELs duplicate each other.)

### 4.3a Plurals and other variants (`layer="variant"`, added 2026-11-25)

**The problem.** The engine compares exact strings, so `brèdes` (the plural, in the mar and syang data) did not meet `brède` (in the hand MEL m188, with
`spinach`, `green vegetable`, `légume`). The data-driven `extended` layer made `brèdes` a one-gloss MEL of its own, and so did every other
plural that the hand MEL lacks (`étoiles` against `étoile` in m426, `cheveux`, `gencives`, `testicules`, `seins` …).
`brèdes` is *not* a candidate for m187 (`broth, soup, side-dish, cooked vegetable, légumes`): m187 and m188 share only `légumes`, and m188 is the vegetable MEL (`brède`, `spinach`, `green vegetable`, `mustard`).

**What it does** (`variants.py`, `variant_layer()` in `make_merged_mels.py`; runs after the layers and the dead-gloss pruning). Two kinds of variant are recognised, never combined
(a plural *and* an accent change at once is too loose: `près` → `pres` → `press`):

| kind | example | rule |
|---|---|---|
| spelling | `rice-field` ~ `*rice field`, `earthquake` ~ `earth*quake`, `lend/borrow` ~ `lend, borrow`, `grand-mère` ~ `grand- mere`, `cowshed` ~ `cow shed`, `ail` ~ `aïl` | same letters up to case, accents, punctuation, spacing |
| number | `brèdes` ~ `brède`, `chevaux` ~ `cheval`, `chèvres` ~ `chèvre`, `lungs` ~ `lung`, `étoiles` ~ `étoile`, `siblings` ~ `sibling` | plural ↔ singular, accents kept; English (`-s -es -ies -ves`, `man/men`, `child/children`) and French (`-s -x -aux/-al -eux/-eu`) |

What happens to a gloss that has such a partner **in exactly one other MEL**:
(a) a non-core MEL with a single gloss is merged into that MEL (broad 12, conservative 17: `brèdes` → m0188, `étoiles` → m0426, `seins` → m0184, `earthquake`, `ashes`);
(b) a data gloss that **no** MEL matches at all (211 distinct glosses of the TGTM data, mostly grammatical notes and numbers; a few are plurals or spellings of a gloss the MELs have) is added to the partner's MEL (broad 12, conservative 13: `chevaux` → m0251 `cheval`, `ail` → m0036 `aïl`; see the TSV).
The added gloss is the data's own spelling, written as `<gl layer="variant">`; the existing glosses are never rewritten.

Safeguards, all visible in `mel-variant-merges-broad.tsv` and `mel-variant-merges-conservative.tsv` (one row per decision, with the target MEL's glosses):
- **Ambiguous cases are not merged, only listed** (`ambiguous-singleton`, `ambiguous-data-gloss`: broad 7 + 6, conservative 10 + 8): when the partner is in several MELs (`brothers`, `sisters`, `tears`, `rides`, `roots`, `côtes`, `dents`, `invité`) I do not guess which sense is meant.
- **Two real French words that differ only by an accent are not linked** (`fatigue` / `fatigué`; "real" = in the French WordNet). `ail` / `aïl` is linked because `aïl` is not a word, only a spelling in the mar lexicon.
- A few rows still deserve a look: `reins` → the `kidney / rein` MEL (French *reins* can also mean the lower back), `ashes` ↔ `ash`, `cando s.th.` (spacing rule).

Also done in the same step: **duplicate one-gloss MELs are dropped** (`subsumed-singleton`: 34 in broad, 46 in conservative; some of these are one-gloss MELs made redundant by the WordNet layer). With v4 as the base, the bulk of this clean-up happens earlier: a v4 MEL with no hand gloss whose glosses are all in another MEL (for instance a hand MEL that `enriched2` has since grown) is dropped, as step 3 of the v3 → v4 maintenance does (1,248 in broad, 807 in conservative, mostly one-gloss MELs such as `[greasy]` beside `[too *greasy (side-dish), greasy]`). Nothing changes for the engine: the same forms match the larger MEL.

**Effect on TGTM** (strict, same ToC; measured on the first, hand-based build, against the build without the layer): broad 1,213 → 1,214 sets, conservative 1,084 → 1,088. Isolates: 1,972 → 1,970 and 2,161 → 2,152. The v4-base build gives the same sets.
All 5,195 cross-language hand94 pairs are still found. The changed sets are, in conservative, the intended ones: `brèdes` (mar, syang) joins the `vegetable / spinach / green vegetable` set, `étoiles` the `star` set,
`seins` the `milk / breasts` set, `cheveux` ~ `hair` (and a weaker `cheveux` ~ `pin hair up`); in both: `grand-mère` ~ `grandmother`, `rice field` ~ `rice-field`.
They are marked `~` in the two set-review TSVs. One bad link is visible and not new: `brèdes` ~ `sow one seed at a time, as maize or green beans …` (a long gloss whose sub-word `green beans` matched).

**Plurals in the engine itself** (matching `brèdes` to `brède` at run time, so that no variant needs to be written into a MEL) was not done: it would be a second matching rule next to the exact one, and
you ruled out the same kind of change for accents. The variant layer gets the same result for the glosses in the TGTM, TGTM94SETS and DEMO93 data, but a new lexicon with new plural glosses would need a rebuild.

### 4.4 Noise removed (extras only; the core is never touched)

- function-word and stopword-only glosses (`of`, `even`, `if`, `also`, `etc.`, `dat` …), generic verbs (`be`, `make`, `faire`, `auxiliaire`), numbers and markup
  (`%`, `|`, `$`), `cf.` notes and phrases of more than five words. This now applies to **every** extra layer; before it skipped the pair-derived ones;
- about 110 extras (114 in broad, 109 in conservative) that **no lexicon of TGTM, TGTM94SETS or DEMO93 can ever match** (computed with the engine's own `_candidates_lower`). This does not change any result, which I checked.
  (Computed over TGTM alone it did: TGTM94SETS has glosses TGTM lacks.)
- duplicates inside a MEL; an extra that only differs from a core gloss by accents or punctuation is dropped; MELs that add nothing because another MEL has all their glosses (4.3a).

No size cap was applied. `broad` has 292 MELs of 8 or more glosses (134 of 12 or more, largest 33); `conservative` 154 (57, largest 29). Before the WordNet layer it was 130 (33, 20) and 48 (7, 17): the growth is the WordNet layer. I did not cap them
because I could not show that the long MELs are the wrong ones.

### 4.5 What the layers add (TGTM, strict, no folding, against the `hand94` run)

| | TGTM sets | isolates | 94SETS sets / isolates |
|---|---:|---:|---|
| 94SETS hand (the baseline) | 990 | 2,187 | 1,016 / 38 |
| TGTM hand (de-accented, untouched) | 983 | 2,200 | 994 / 98 |
| **conservative, before the WordNet layer** | 1,088 | 2,152 | 1,029 / 31 |
| **broad, before the WordNet layer** | 1,214 | 1,969 | 1,044 / 30 |
| **conservative** | 1,202 | 1,983 | 1,047 / 29 |
| **broad** | 1,302 | 1,861 | 1,063 / 29 |

Sets that are **new** (no form was in a hand94 set) or **enlarged** (a hand94 set plus new forms), by the origin of the MEL that made them:

| MEL origin | broad new | broad enlarged | conservative new | conservative enlarged |
|---|---:|---:|---:|---:|
| MELs with hand glosses (core, plus the extras and WordNet glosses they gained) | 83 | 169 | 30 | 82 |
| v4-only MELs (no hand gloss) | 32 | 36 | 55 | 59 |
| `pairs` | 2 | 1 | 3 | 1 |
| `pairs-loose` | 3 | 4 | | |

("Enlarged" = exactly one hand94 set plus new forms; the totals are 330 rows for broad and 230 for conservative (before the WordNet layer: 239 and 100). The origin is now decided by whether the MEL holds a hand gloss, because v4 contains the hand MELs; the first build split by id prefix, so these rows are not comparable with it: 55/104 and 32/30 for broad, 3/7 and 42/41 for conservative. The WordNet layer's own contribution is in 4.7.) A third category, sets that merge two or more hand94 sets (384 in broad, 345 in conservative), is not counted as a gain:
the engine groups a MEL's forms into sets by correspondence, so the grouping shifts when the glosses change.
So the MELs with hand glosses give most of the new and enlarged sets (`enriched2` and the WordNet layer both add to them), and in conservative the v4-only MELs give about half.

**What I did not do:** judge these sets. The 1994 reference cannot (it favours the hand MEL: against it broad scores P 0.953 on TGTM, conservative 0.967, the hand MEL 0.980; on
TGTM94SETS 0.960 / 0.973 / 0.988; before the WordNet layer 0.965 / 0.976 and 0.977 / 0.985), so it is used only to catch breakage. Nothing was lost: **all 5,195 cross-language form pairs (language, form) of the hand94 run are still in both files**, and 804 (broad) or 531 (conservative) are added (530 and 169 before the WordNet layer).
(Counted by form *id* 13% of hand94 pairs differ, but all of those involve homophones that now sit in a different set: for example sahu `¹ur` "stunted and fruitless" is no longer linked to `yellow`.)
The earlier spot check of 25 random broad sets found about 17 right, 3 borderline and 5 wrong, by eye. For a proper look, every new and enlarged set is listed with its MEL
(extras marked `+`), in `broad-new-and-enlarged-sets.tsv` (330 rows) and `conservative-new-and-enlarged-sets.tsv` (230 rows); `~` marks a variant-layer gloss.
The loose pairs are mixed, as expected: `night`/`nuit`, `hoof`/`sabot`, `near` and `contagious` look right; `top ~ big ~ beautiful` (q7), `obey ~ subside` (q54) and `cloth ~ loom` (q16) do not.
Typical weaknesses of the `extended` MELs are fragments from hyphenated glosses (`+grand`, `+mother` from `*grand-*mother`).

### 4.5a `enriched3` instead of `enriched2` (tried 2026-11-25, not adopted)

`python make_merged_mels.py broad-e3` builds `TGTM.broad-e3.mel.xml`: broad with the `enriched` layer taken from `enriched3` (4,184 MELs, 10,532 glosses; the variant layer is on in both).
(This trial was run on the first, hand-based build; the v4 base gives the same sets, so the result stands.) `enriched3` adds 864 glosses to the hand MELs that `enriched2` lacks and drops 697 of its glosses, many of them long French phrases (`tapis fait à la maison`, `rester bon`, `natte de bambou`).

| TGTM, strict | sets | isolates | forms in sets |
|---|---:|---:|---:|
| broad (`enriched2`) | 1,214 | 1,970 | 3,294 |
| broad-e3 (`enriched3`) | 1,210 | 1,969 | 3,294 |

1,112 sets are identical; 102 exist only with `enriched2` and 98 only with `enriched3`. Only 13 of the `enriched3`-only sets (and 11 of the others) share no form with a set of the other build, so the two are close. The new ones are not better:
the long phrases bring sub-word matches (the engine also matches the words of a phrase): `mar bon marché` ~ `tuk sit cross-legged` (through `rester bon` and `sit`), `mar cour de maison` ~ `tuk sit cross-legged` (through `tapis fait à la maison`).
A few of the new sets look right (`ris shelf, platform` ~ `sahu bench`, `syang dormir` ~ `tuk lie down`), and some of the sets lost are right too (`mar déplacer, remuer` ~ `tuk move to other place`, `mar chang` ~ `syang bière`).
Against the 1994 pairs (regression guard only) it is the same: TGTM P 0.962 / R 0.848 against 0.965 / 0.846; TGTM94SETS 1,049 sets against 1,044. Verdict: no reason to switch, and some to stay; the file is left as an experiment.

### 4.6 Statistics and how the MELs match the data

Measured with the engine's own matcher (`mel.compile_associated_mels`) against the 7,863 forms of the eight TGTM lexicons (the glosses the engine uses:
`ngl`, else `gl`). No precision or recall here: these numbers describe *what matches what*. The two existing hand MELs are shown for comparison and were not changed.
Full table: `tgtm-proposals/new-mel-stats.csv`.

**Size**

| | TGTM hand | 94SETS hand | conservative | broad |
|---|---:|---:|---:|---:|
| MELs | 673 | 673 | 3,795 | 3,295 |
| glosses | 2,489 | 2,502 | 11,117 | 11,419 |
| glosses per MEL: mean / median / max | 3.70 / 3 / 16 | 3.72 / 3 / 16 | 2.93 / 2 / 29 | 3.47 / 2 / 33 |
| MELs with 1 / 2 / 3–4 / 5–7 / 8+ glosses | 12 / 215 / 287 / 116 / 43 | 13 / 212 / 288 / 116 / 44 | 856 / 1,244 / 1,188 / 353 / 154 | 689 / 1,056 / 953 / 305 / 292 |
| `source`: core / extra or wordnet | n/a | n/a | 2,496 / 8,621 | 2,504 / 8,915 |
| `xml:lang`: en / fr / und | none | none | 7,755 / 3,150 / 212 | 7,970 / 3,241 / 208 |

The new MELs are many small MELs, not a few big ones: 673 hand MELs of about 3.7 glosses, against about 4,000 new ones of about 2.2, because
`hand-extended-v4` has one MEL per data-gloss variant. Only the hand MELs are broad semantic fields.

**How much of the data they reach** (strict mode: a form whose gloss matches no MEL can never be in a set)

| | TGTM hand | 94SETS hand | conservative | broad |
|---|---:|---:|---:|---:|
| forms with a matching MEL | 5,467 (69.5%) | 5,498 (69.9%) | 7,736 (98.4%) | 7,746 (98.5%) |
| forms with a MEL that also matches another language | 5,456 (69.4%) | 5,487 (69.8%) | 7,185 (91.4%) | 7,259 (92.3%) |
| MELs that match at least one form | 672 | 671 | 3,791 | 3,291 |
| MELs reaching ≥ 2 / ≥ 3 languages | 656 / 622 | 655 / 624 | 3,107 / 2,555 | 2,678 / 2,227 |
| forms per matching MEL: mean / median / max | 17.0 / 12 / 113 | 17.0 / 12 / 108 | 12.6 / 8 / 138 | 14.0 / 8 / 144 |
| MEL glosses that match at least one form | 81.4% | 81.8% | 92.7% | 92.8% |

Per-language coverage (forms with a matching MEL) in the hand MELs runs from 53% (syang) and 64% (ris, tuk) to 94% (tag); in both new MELs it is 93–99.7%
(lowest: mar, 93.3% conservative and 96.0% broad). So the new MELs mostly close the **French and Syang gap**: syang 53% → 99%, mar 69–71% → 93–96%.

**Where the matches come from**

| forms matched through… | conservative | broad |
|---|---:|---:|
| core glosses only | 659 | 617 |
| core and extra glosses | 4,841 | 4,883 |
| extra glosses only | 2,236 | 2,246 |
| … of which, by layer | extended 2,011; wordnet 639; pairs 82; variant 26 | extended 1,882; wordnet 573; enriched 600; pairs-loose 64; pairs 79; variant 19 |

(a form can be matched through extras of more than one layer, so the layers can add up to more than the row.) About 2,200 forms, 28% of the data, have a MEL
*only* because of an extra gloss, nearly all of them from `extended`. The variant layer is what links 26 (conservative) or 19 (broad) forms to a MEL that they could not reach before:
their gloss was a plural or spelling variant that only had a one-gloss MEL. 95.8% (conservative) and 95.9% (broad) of the extra glosses match at least one form, against
81.8% of the core glosses (the core is a general vocabulary list; 18% of its glosses never occur in these lexicons).

**Ambiguity** (the cost of more matches: each form is matched to several candidate MELs)

| MELs matched per matching form | TGTM hand | 94SETS hand | conservative | broad |
|---|---:|---:|---:|---:|
| mean / median / max | 2.09 / 1 / 18 | 2.08 / 1 / 18 | 6.2 / 3 / 60 | 6.0 / 3 / 60 |
| 1 MEL | 2,898 | 2,897 | 2,447 | 2,527 |
| 2–3 | 1,761 | 1,806 | 1,428 | 1,489 |
| 4–9 | 775 | 762 | 2,220 | 2,187 |
| 10 or more | 33 | 33 | 1,641 | 1,543 |

This is the main behavioural difference. Roughly one form in five now matches 10 or more MELs (1,641 and 1,543 forms, against 33; the WordNet layer had raised it to 1,853 and 1,839, and the subset merge of 4.8 brought it back down). I expect that to come from
glosses of several words, each word matching a different small MEL, but I did not check it. Forms whose only MEL is a singleton MEL: 461 (conservative), 398 (broad);
such a form can only join forms whose gloss is the same word.

**What the sets look like** (TGTM, strict; counted from the run files)

| | 94SETS hand | conservative | broad |
|---|---:|---:|---:|
| sets | 990 | 1,202 | 1,302 |
| distinct forms in sets | 3,096 | 3,297 | 3,419 |
| reflexes per set: mean / median / max | 3.85 / 3 / 14 | 3.54 / 3 / 13 | 3.50 / 3 / 13 |
| sets with 2 / 3 / 4+ languages | 416 / 219 / 355 | 552 / 261 / 389 | 626 / 278 / 398 |
| sets with 2 / 3–4 / 5+ reflexes | 323 / 370 / 297 | 472 / 435 / 295 | 531 / 466 / 305 |
| MELs that produced at least one set | 503 | 615 | 592 |

The extra sets are mostly small: against the 94SETS hand MEL the new MELs add 2-language sets (+136 conservative, +210 broad) much more than sets with 4 or more languages (+34, +43),
and the sets come from more MELs (503 → 615 and 592; the first build counted 717 and 718, because the hand MEL and a separate extended MEL could both be credited for one set; with v4 as the base they are one MEL; I did not check this further). Only 3,300–3,400 of the 7,700 forms that match a MEL end up in a set; the rest fail on sound correspondences, not on meaning.

### 4.7 The WordNet layer (`source="wordnet"`, added 2026-11-25)

**What it is for.** The MELs link French and English glosses only where a hand, v4 or pair MEL happens to hold both. `voler` was in one MEL (`fly`, `voler`, `s'envoler`) and in none of the `steal` MELs, so a French "steal" and an English `steal` could not meet.
The layer translates the glosses the lexicons use through WordNet (English) and the French WordNet (Open Multilingual WordNet, via NLTK), and adds each gloss to the MELs that hold its translation. Both files have it. Every added gloss is `source="wordnet"`, `layer="wordnet"`, with the usual `xml:lang`.
How it works is in 6.5a; every decision (added, rejected, skipped) is in `mel-wordnet-additions-broad.tsv` and `mel-wordnet-additions-conservative.tsv`, with the synset that justified it.

**What it adds.** Broad: 2,515 glosses (1,697 French → English, 818 English → French; 1,090 distinct glosses placed in 1,545 MELs). Conservative: 2,599 (1,765 / 834; 1,145 glosses, 1,672 MELs).
`voler` is now in the `steal` MEL m0660 (`steal`, `theft`, `thief`, `voleur`, …, `steal (to_)`) and in the `fly` MEL m0472 (`fly`, `voler`, `s'envoler`, …, `fly (v.)`, `to fly`), and also in the `flee` MELs (m0469 in both files; m0310 and m4653 in broad), but not in the `fly (n.)` insect MEL. (The layer first put it into the one-translation MELs `steal (to_)`, `fly (v.)` and `to fly`; the subset merge of 4.8 then folded those into m0660 and m0472.)
`falcon` (a DEMO93 gloss no MEL had) is now in m0209 with `faucon`, `buzzard`, `vulture`.

**Effect on TGTM** (strict, same ToC; before = the same files without the layer):

| | sets | isolates | P / R against the 1994 pairs (TGTM) | 94SETS sets / isolates |
|---|---:|---:|---|---|
| broad, before | 1,214 | 1,969 | 0.965 / 0.846 | 1,044 / 30 |
| **broad** | **1,302** | **1,861** | 0.953 / 0.849 | 1,063 / 29 |
| conservative, before | 1,088 | 2,152 | 0.976 / 0.835 | 1,029 / 31 |
| **conservative** | **1,202** | **1,983** | 0.967 / 0.842 | 1,047 / 29 |

No hand94 pair is lost in either file (5,195 kept; 804 and 531 added). Of the sets, 161 (broad) and 205 (conservative) differ from the sets without the layer: broad 20 new, 62 enlarged, 79 merge two or more earlier sets; conservative 41 new, 90 enlarged, 73 merged.
All are listed with their MEL (WordNet glosses marked `^`) in `broad-wordnet-changed-sets.tsv` and `conservative-wordnet-changed-sets.tsv`. The 1994 reference is only a regression guard (see 4.5): its precision drops by 0.009–0.012, which fits more links than the 1994 analysis had, and I have not
shown that they are right. Reading a sample of conservative sets, many are good (`mar ³³'³³to` `plier` ~ `tuk ²təp` `fold over` (m0744); `syang ²²'²²sum` `dormir` ~ `tuk ³sum` `lie down` (m0566); `mar ³pjaʱ` `sabot` ~ `tuk ³pja` `hoof` (m0927); `mar` `tasse` ~ `ris` `wooden drinking-cup` (m2086); `gha ¹tsʰer` `disgust` ~ `ris ¹tsʰer` `irritated` (m0060))
and some are not (`mar ⁵⁵'⁴⁴kʰʌr` `faire tomber de l'arbre` ~ `tag` `dry` through the mixed MEL m5477; the `ear` MEL m0386 also gains `épi`, "ear of grain"). The noise is mostly the French WordNet's odd sense assignments (`introduire` ~ `imprison`, `father` ~ `mère`) and MELs that already mix senses. Generic translations (`be`, `être`, `venir`, `faire` …) are excluded, which removed junk such as `father`, `exist` and `equal` in the `être` MEL.

**Confidence.** Each added gloss has `confidence="high"` or `"low"` (also in the `confidence` column of the TSVs). `high` = (a) the English sense is a main sense of the English word (at least 0.3 of its SemCor sense counts, over all parts of speech), and for French → English also (b) a strong translation of the French word (its SemCor count is at least half of the strongest translation's: `voler` → `steal` 0.62, `fly` 0.89, `flee` 1.0) and (c) not contradicted by the MEL, i.e. the MEL's other English glosses are near the sense (WordNet path similarity ≥ 0.25 or derivationally related) or there are none. Everything else is `low`.
Broad: 1,023 high, 1,007 low; conservative: 1,069 high, 1,069 low (after the subset merge). `voler` is `high` in the `steal` MEL (m0660) and the `fly` MEL (m0472) and `low` in the `flee` MELs; `falcon` in m0209 is `high`.
**Nothing reads the attribute, so low-confidence glosses are used as much as the others.** To see what the high ones alone do, build with `python make_merged_mels.py broad-wnhigh conservative-wnhigh` (the low ones are then not added at all): conservative 1,159 sets (1,202 with all), broad 1,258 (1,302). Against the 1994 pairs, the share of the new links between forms the 1994 sets know that are in them is 0.447 (high only) against 0.434 (all) for conservative and 0.433 against 0.375 for broad: slightly better, from 38–176 judged pairs only, so a hint at best.

**Why it is tagged.** `source="wordnet"` lets you drop, count or display these glosses (and the sets that depend on them) separately; building with `broad-nown` / `conservative-nown` gives the files without the layer.

### 4.8 Merging subset MELs (last step, added 2026-11-25)

**Why.** `fly (v.)` and `to fly` were separate MELs next to `m0472` (`fly`, `voler`, `s'envoler`): the earlier duplicate test compared glosses with accents, case and punctuation ignored, but not through the engine's gloss normalization, so `fly (v.)` and `to fly` never counted as `fly`.
**What.** The last step of the build (`subset_merge()`, 6.5b) compares the candidate glosses that `mel.normalize_gloss()` makes of each MEL's glosses. A MEL whose candidates are all among the candidates of one other MEL is merged into it: its glosses are appended (so the written forms `fly (v.)`, `to fly` appear) and it is removed. It is the engine's own test for "this MEL matches nothing the other does not".

| | MELs before | merged away | ambiguous (left alone, listed) | MELs after |
|---|---:|---:|---:|---:|
| conservative | 4,539 | 744 (25 of them hand MELs) | 925 | 3,795 |
| broad | 4,133 | 838 (10 hand MELs) | 850 | 3,295 |

**It changes nothing for the engine.** Anything the merged MEL matched, its target matches, and the written glosses are kept in the target. Checked by re-running both files: the sets are identical (1,202 and 1,302 on TGTM, no set only before or only after), and so are isolates, the gold figures and the hand94 pairs.
Hand MELs can be merged away too, as long as they go into a larger MEL (25 in conservative, 10 in broad, logged as `merged-hand`): their glosses keep `source="core"` in the target, and none is lost (all 2,029 distinct hand gloss strings are still `core`), but the hand id disappears.

**Rules that keep it from joining different senses.** (1) The target must be the single largest MEL that contains the candidate set; with two or more unrelated containing MELs (`to comb`, `return`, `turn over` …) it is left alone and listed (`ambiguous` in `mel-subset-merges-*.tsv`). (2) A MEL that says it is about nouns (`fly (n.)`, `(n.)`) is not merged into one that does not say so, so the insect MEL `m5642` (`fly (n.)`, `fly`, `mouche`) stays separate from `m0472`; a verb-marked one (`fly (v.)`, `to fly`) never goes into a noun-marked one.
(3) It repeats until nothing more merges. The comparison includes the sub-words of phrases, as the engine's matching does, so a one-word MEL can be a subset of a MEL with a phrase (`fly` ⊆ `fly ball`); the single-target rule is what keeps that in check. Verified result for the example: `m2154` (`fly (v.)`) and `m3630` (`to fly`) are merged into `m0472`.

## 5. Status of the suggestions

| # | Suggestion | Status |
|---|---|---|
| 1 | fold accents in `mel._candidates_lower` | **rejected**; patch withdrawn. The MEL keeps real French; accented spellings are added instead (4.3) |
| 2 | retire `TGTM/TGTM.hand.mel.xml` | **left alone for now**. The two hand MELs have drifted apart (4 ids only in TGTM, 4 only in 94SETS; 59 accent variants; 18 TGTM-only and 36 94-only glosses), so a decision on one core is still needed |
| 3 | one MEL as the default | **neither** for now; both produced |
| 4 | tag the glosses by source | **done** in the files (`source`, `layer`); the engine carries it (`Mel.gloss_sources`) but nothing displays it yet |
| 5 | skip empty `<gl/>` | **done** in `src/read.py` (also skips a MEL with no glosses). `TGTM94SETS.clics.mel.xml` (1,852 empty glosses) now runs |
| 6 | get rid of the noise | **done in the merged files** (4.4). Cleaning the data directories (duplicate copies, empty DEMO93 files, the stray `DIS.es-reduced`; archiving `stedtsemkey`, `evosem`, `wn-pairs`, `wordnet2`) is **not done**: I did not touch the data repository. Commands are below |
| 8 | plurals and other variants (2026-11-25) | **done in the MEL files** as the `variant` layer (4.3a); the engine still matches exact strings; ambiguous cases are listed in `mel-variant-merges-*.tsv`, not merged |
| 9 | translate French ↔ English glosses with WordNet (2026-11-25) | **done** as the `wordnet` layer (4.7, 6.5a) in both files, tagged `source="wordnet"`; each decision is logged. Broad +88 sets, conservative +114 |
| 10 | merge MELs whose normalized glosses are a subset of another's (2026-11-25) | **done** as the last step of the build, using `mel.normalize_gloss`; hand MELs excluded; ambiguous cases listed (4.8, 6.5b) |
| 7 | fill in `xml:lang` | **done** for every gloss of the merged files; the original files are unchanged |

Suggested next steps, in order: (a) review the two set TSVs and the two `mel-variant-merges-*.tsv`; (b) decide which hand MEL is the core; (c) decide whether the `loose` layer stays in broad;
(d) use `source` in the Sets pane (show which sets depend on an extra link).

### Data-directory clean-up (not run)

```bash
cd /Users/johnlowe/GitHub/RE-Tamangish-Files
mkdir -p archive/mel
git mv TGTM94SETS/TGTM94SETS.stedtsemkey.mel.xml TGTM94SETS/TGTM94SETS.evosem.mel.xml archive/mel/   # only if tracked; check with git status
```
Check `git status` first: several of these files are not tracked, and the exact list of duplicates is in `mel-stats.csv` (`identical_to`).

## Engine changes made for this (not committed)

- `src/read.py`: `read_mel_file` skips empty `<gl/>` and MELs left with no glosses, and reads an optional `source` attribute.
- `src/mel.py`: `Mel` takes an optional `gloss_sources` (like `gloss_langs`).
- `src/compare_normalize_gloss.py`: `und` is a known language code, next to `en`, `fr` and `xx`.

## Files (all in `docs/tgtm-proposals/`)

- `TGTM.broad.mel.xml`, `TGTM.conservative.mel.xml`: the two merged MELs.
- `make_merged_mels.py` (builds them on `hand-extended-v4` as the base; `broad-e3` is the enriched3 experiment, `broad-hand` / `conservative-hand` the first design with the hand MELs as base, `broad-wnhigh` / `conservative-wnhigh` with only the high-confidence WordNet glosses, `broad-nown` / `conservative-nown` the build without the WordNet layer and the subset merge, `broad-nosub` / `conservative-nosub` without the subset merge only; run it with the miniconda `main` interpreter), `gloss_lang.py` (language tags and accent spellings) and `variants.py` (plural / spelling variants).
- `mel-id-changes-broad.tsv`, `mel-id-changes-conservative.tsv`: the ids that were padded to four digits.
- `mel-subset-merges-broad.tsv`, `mel-subset-merges-conservative.tsv`: every merge and every ambiguous subset of the last step, with both MELs' glosses.
- `mel-wordnet-additions-broad.tsv`, `mel-wordnet-additions-conservative.tsv`: every decision of the WordNet layer (added, rejected-other-sense, too-many-targets, skipped-und) with the synset and the target MEL's glosses; `broad-wordnet-changed-sets.tsv`, `conservative-wordnet-changed-sets.tsv`: the sets that differ from the build without it (WordNet glosses marked `^`).
- `mel-variant-merges-broad.tsv`, `mel-variant-merges-conservative.tsv`: every variant decision (merged, attached, subsumed duplicate, ambiguous) with the target MEL's glosses.
- `broad-new-and-enlarged-sets.tsv`, `conservative-new-and-enlarged-sets.tsv`: sets for review.
- `new-mel-stats.csv`: the statistics of 4.6.
- `mel-accent-restorations-broad.tsv`, `mel-accent-restorations-conservative.tsv`.
- `TGTM.mel-additions.xml`, `TGTM.mel-additions-loose.xml`, `build_mel_additions.py`: the earlier pair-derived additions (now merged in).
- `mel-stats.csv`: statistics and run results for the 45 original files (the merged files are not in it).

## 6. How the broad and conservative MEL files are made (process description, 2026-11-25)

Everything is done by one script, `tgtm-proposals/make_merged_mels.py` (helpers: `gloss_lang.py`, `variants.py`). The **base is `TGTM.hand-extended-v4.mel.xml`**; the script keeps all of its MELs,
tags the glosses that came from the hand MELs, adds and removes glosses by fixed rules, and writes `TGTM.broad.mel.xml` and `TGTM.conservative.mel.xml`. No source file is changed, no gloss is ever rewritten or de-accented, and the engine is not involved
in the build except as a matcher (6.2). The two files differ only in which layers they include. Run it with `python make_merged_mels.py` (a few seconds to a minute, miniconda `main` interpreter).
The worked examples are numbered **Example 1 … 24** and are real rows of the output files.

*(An earlier version of the script took the two hand MELs as the base and `hand-extended-v4` as a layer. That was a misreading of the plan: v4 already contains the hand MELs. The two designs give the same sets and the same 5,195 hand94 pairs; the v4-base one is the default now and the old one stays available as `broad-hand` / `conservative-hand`.)*

```
hand-extended-v4 (all MELs, own ids)  ─►  mark the hand glosses core  ─►  + enriched2 (broad only)  ─►  + pairs  ─►  + pairs-loose (broad only)
      ─►  drop MELs that add nothing  ─►  remove noise  ─►  tag xml:lang  ─►  restore accents  ─►  drop dead extras  ─►  WordNet layer  ─►  variant layer  ─►  merge subset MELs  ─►  sort, pad ids, write
```

| layer | `source` | `layer` | broad | conservative |
|---|---|---|:-:|:-:|
| 1 base: `hand-extended-v4`; the glosses of its MELs that are hand glosses are `core`, the rest are `extended` | core / extra | `extended` | yes | yes |
| 2 `enriched2`: extra glosses for hand MELs | extra | `enriched` | yes | no |
| 3 pair-derived MELs | extra | `pairs` | yes | yes |
| 4 loose pair-derived MELs | extra | `pairs-loose` | yes | no |
| 5 accent restoration | extra | `accent` | yes | yes |
| 6 WordNet translation layer | wordnet | `wordnet` | yes | yes |
| 7 variant layer | extra | `variant` | yes | yes |
| 8 merge of subset MELs (last step; adds no glosses; hand MELs included) | | | yes | yes |
| 9 write: glosses and MELs in alphabetical order, ids padded to four digits | | | yes | yes |

### 6.1 The base, the core, and the optional layers

**Base.** Every MEL of `TGTM.hand-extended-v4.mel.xml` (5,585 MELs, ids `m0001` …) is a MEL of the output, with its own id. v4 already contains the hand MELs: of the 673 hand MELs, 638 are identical there and the rest differ by a gloss or two
(v4 splits `be born` into `be` and `born`, for instance). v4 is the v3 → v4 maintenance result described in section 2, one MEL per gloss variant in the data.

**Core.** To say which glosses are hand glosses (`source="core"`), the two hand MELs are first unioned: `TGTM94SETS/TGTM.hand.mel.xml` (accented French) as it is, plus the glosses that only `TGTM/TGTM.hand.mel.xml` has (de-accented French, and your `sarong`),
added to the MEL with the same id or to the MEL it shares at least two glosses with. Each hand MEL is then claimed by the v4 MEL that shares the most glosses with it (ties go to the same number); 672 are claimed and one is not (it is kept under its own hand id).
Inside the claimed v4 MEL the hand glosses are written first, as `core`, so **no hand gloss is lost even where v4 reworded or split one** (v4 lacks 11 glosses of the 94SETS hand MEL altogether, such as `baratter`, `become tired`, `employer`, and has 56 only in another spelling, such as `abces` for `abcès`);
the other glosses of the v4 MEL are `extra`, `layer="extended"`, and the junk filter of 6.2 is applied to them. Core glosses are never removed or edited later. `key()` (case-, accent-, punctuation-insensitive) is used only to recognise duplicates.

**Example 1: the base with its core.** `m0209` starts as `buse`, `buzzard`, `faucon`, `milan`, `vulture` (core, from the hand MEL) plus whatever v4 adds. (`falcon` is not in it: neither hand MEL nor v4 has it, see 6.6.)

**Enriched** (broad only). `TGTM.enriched2.mel.xml` has the same ids as the hand MEL. For a MEL that exists in both and shares at least one gloss with its enriched2 counterpart, the enriched2 glosses that are new, not junk (6.2)
and not duplicates are added as `layer="enriched"`.

**Example 2: enriched glosses.** m0209 in `broad` gains `aigle`, `bird of prey`, `eagle`, `hawk`, `vautour` (all `extra`, `enriched`), so `faucon` and `eagle` now meet. (`enriched3`, a later file, was tried instead and rejected: 4.5a.)

**Example 3: a v4-only MEL.** `m0002` = `abandon`, `abandonner`, `cast away`, `cesser` … is in v4 and has no hand counterpart; its glosses are all `extra`, `extended`. These MELs, one per gloss variant of the data, are what take form coverage from about 70% (hand) to 98%.

**Subset MELs, first pass.** A v4 MEL with no hand gloss whose glosses (compared with case, accents and punctuation ignored) are all in another MEL is dropped, as step 3 of the v3 → v4 maintenance does; the engine-based, merging version is the last step (6.5b). It happens here because the enriched and pair layers grow other MELs after v4 was made (1,248 MELs in broad, 807 in conservative, mostly one-gloss MELs). The sets do not change.

**Pairs.** `TGTM.mel-additions.xml` (57 MELs, `p…`) and `TGTM.mel-additions-loose.xml` (17 MELs, `q…`) come from `propose_mel_additions.py`, which looks at forms that the engine put in *sound-only* sets
(no MEL needed) and asks whether their glosses are semantically linked. A pair of glosses is accepted when there is independent evidence: **E** the two share a candidate produced by the engine's own normalizer; **W** they share a **WordNet** synset
(English, and French through the Open Multilingual WordNet; top three senses only); **M** they co-occur in a small MEL (15 glosses or fewer) of another source file. Accepted = E, or W+M, or M in two different source files. Borderline pairs are the loose layer.
A pair MEL is added unless an existing MEL already has all its glosses.

**Example 4: an accepted pair.** `p0002` = `aujourd'hui` (fr) + `today` (en), from syang `⁵⁵'⁵⁴tini` "aujourd'hui" ~ tuk `¹tiŋi` "today".
**Example 5: a loose pair that is wrong.** `q0007` = `beautiful`, `big`, `distant`, `far`, `the top`, `top` (tagged `pairs-loose`; `top ~ big ~ beautiful` is one of the bad ones listed in 4.5). Loose pairs are kept in broad but tagged so that they can be filtered.

### 6.2 Noise removal (extras only)

`junk(g)` rejects a gloss that is a stopword or only stopwords (**NLTK**'s English and French stopword lists, plus `avoir`, `être`), a generic verb or filler (`be`, `make`, `faire`, `auxiliaire`, `etc.`, `dat`), one-character strings,
anything with `%`, `|`, `$`, a parenthesis start or `cf.`, and phrases of more than five words. It is applied to every extra layer; core glosses are exempt.

**Example 6.** `of`, `even`, `etc.`, `be`, `faire`, `50%` and `cf. foo` are all rejected; `ail` is kept.

Later, *dead* extras are removed: `support(g)` asks the engine's own normalizer (`mel._candidates_lower`) whether any lexicon of TGTM, TGTM94SETS or DEMO93 has a gloss that could match `g`. An extra with support 0
can never fire for any of these projects, so it is dropped (114 in broad, 109 in conservative; no result changes).

**Example 7: dead extras.** `molar`, `evil` and `topic` (from `hand-extended-v4`, as `extended` glosses) are not matched by any gloss in the three projects. (Core glosses are never dead-tested: `jete` has no match either and stays.)

### 6.3 The language tag: what NLTK and WordNet do (`gloss_lang.py`)

Every `<gl>` gets `xml:lang` = `en`, `fr` or `und` (undetermined). The tag is decided by votes, in this order:

1. **Data.** The lexicons' own gloss languages are known (mar, syang, tang are French; gha, pra, ris, sahu, tag, tuk, nar are English). For every gloss in them, the whole string and each `, ; /` piece is counted for its language, except that a gloss whose *words* clearly
   belong to the other language is counted for that one (the French lexicons contain some English glosses). A string used only by English lexicons gets `en`, only by French ones `fr`, and by both (more than 10% each way) `und`: a real homograph.
2. **Words.** No data hit: the gloss's words are checked against the **NLTK** French and English stopword lists (the side with more function words wins), and an accented letter with no English function word means French.
3. **WordNet.** Still undecided: count the **WordNet** synsets of each word in English and in French (`wn.synsets(w, lang='eng'|'fra')`). The Open Multilingual WordNet lists many English words as French lemmas, so presence is not evidence;
   a language wins only when it has at least 3× the other's senses, otherwise `und`.
4. A tag already present in a source file counts as one more vote; a tie is `und`. No evidence at all is `und`.

**Example 8: data decides.** `hawk`, `garlic`, `spinach`: used only by English lexicons, so `en`. `aujourd'hui`: only French ones, so `fr`.
**Example 9: homograph.** `pot` and `chair` are glosses in both an English and a French lexicon, so `und` (`data-both`).
**Example 10: words decide.** `épinards`, `brède` and `genre d'épinards` are in no lexicon as a whole gloss; the accented letter (and no English function word) gives `fr`. `the top` has no data either; the English stopword `the` gives `en`.
**Example 11: WordNet is no help.** `table` has 8 English and 7 French senses, so it is `und`; `cando s.th.` has no WordNet entry in either language and no data, so `und`.

The heuristic is imperfect (mostly on short words); the totals are in 4.6.

### 6.4 French and English glosses and accent restoration

There is **no accent folding** anywhere (see 4.3): a French gloss is always written as the real word, and the engine compares exact strings. De-accented French glosses in the hand MELs (`jete`, `eviter`) are therefore *not* silently
corrected, and the correct spelling is not guessed. For each such gloss that the language vote (6.3) could not place at all (`no-evidence`) and that has no accent, `accented_forms()` lists the accented spellings that fold to it, from the French WordNet lemmas
and from the French lexicons' own glosses. When there is **exactly one**, the real spelling is added beside the hand gloss as `layer="accent"` (extras are corrected in place). Two candidates means nothing is done.

**Example 12.** `jete` → `jeté`, `eviter` → `éviter`, `appetit` → `appétit`, `naitre` → `naître` (32 restorations, 21 of them added as `layer="accent"`; the rest were already in the MEL; `mel-accent-restorations-broad.tsv`). **Example 13.** `eleve` has two accented spellings (`élevé`, `élève`), so it is left alone.

English and French are never translated or mapped to each other by the script: the cross-language link comes only from the MELs (hand-written, data-driven or pair-derived), which is why one MEL can hold `faucon`, `eagle` and `hawk`.

### 6.5 Plurals and other variants (`variants.py`, `variant_layer()`)

The engine compares exact strings, so `brèdes` does not match `brède`, and there is no plural handling in the engine (deliberately not added). The build instead puts the missing variant into the MEL. A gloss A is a *variant* of a gloss B in two ways, never combined:

- **spelling**: the same letters up to case, accents, punctuation and spacing (`key()`: `rice-field` ~ `*rice field`, `earthquake` ~ `earth*quake`, `cowshed` ~ `cow shed`, `ail` ~ `aïl`);
- **number**: plural ↔ singular **with the accents kept** (`key_a()` and `plural_keys()`). The rules are hand-written suffix rules, not NLTK's lemmatizer or WordNet morphology: English `-s -es -ies/-y -ves/-f(e)` and irregulars (`man/men`, `child/children`, `wife/wives`), French `-s -x -aux/-al -eux/-eu`, and
  the same for the first word of a phrase (`pieds nus`). The rules over-generate (`brèdes` → `brède`, `brèdeses`, `brèdess`), which is harmless: a candidate only counts when it equals the key of a gloss that really is in a MEL.

Two decisions use **WordNet** as a *dictionary*, not as a source of synonyms: two words that differ only by an accent and **are both French words** in WordNet-fra are not linked, and a spelling the dictionary lacks is treated as a variant (`in_french_dictionary()`).

What it does with a stray gloss that has a partner **in exactly one MEL** (otherwise it is only listed in `mel-variant-merges-*.tsv`):
(a) a non-core one-gloss MEL whose only gloss is a variant of a gloss elsewhere is merged into that MEL; one that duplicates a gloss of another MEL exactly is dropped;
(b) a gloss of the lexicons that **no** MEL matches at all (normalizing it with the engine's own `_candidates_lower`) is added to the MEL of its partner, written exactly as the data spells it.

**Example 14: number.** `étoiles` (plural, data) → m0426 `étoile` / `star`: in both files m0426 ends as `étoile`, `star`, `étoiles` (`variant`). `brèdes` → m0188 (`brède`, `spinach`, `green vegetable`, `légume` …): in conservative as `variant`; in broad it already came with the enriched layer, so nothing is added.
**Example 15: spelling.** `ail` (mar spelling, not in WordNet-fra) → m0036 `aïl` / `garlic` (both files); `earthquake` → the MEL with `earth*quake` (`m1486`).
**Example 16: not merged.** `sisters`, `tears`, `dents`, `invité` each have a partner in several MELs: only listed (e.g. `sisters` → several MELs, see the TSV). And `fatigue` / `fatigué` (both French words in WordNet-fra) are not linked.
**Example 17: duplicate dropped (before the last step).** A one-gloss v4 MEL such as `[langur]`, when another MEL (`*langur <*monkey>`, `langur`, `monkey`) already has the gloss, is dropped with the subset MELs of 6.1; the 4 that only the variant layer sees are logged as `subsumed-singleton`.

Result: broad 31 and conservative 40 variant glosses, 16 / 22 merged one-gloss MELs, 15 / 18 attached data glosses; broad 1,213 → 1,214 sets, conservative 1,084 → 1,088 (4.3a).

### 6.5a The WordNet translation layer (`wordnet_layer()`)

It runs after the dead-gloss removal and before the variant layer, so it only adds glosses the lexicons use. Each addition is tagged `confidence` high or low (4.7); `wn_min='high'` leaves the low ones out.

1. **Which glosses.** Every piece (`normalize_gloss_phrases`, so `, ; /` alternatives, parentheses and `to`/`se` stripped) of every gloss of TGTM, TGTM94SETS and DEMO93, of at most two words, not junk, with language `fr` or `en` by the vote of 6.3. Homographs (`und`: `pot`, `table`) are skipped (205, listed).
2. **French → English** (`voler`). Take the French WordNet synsets of the word; keep the right part of speech (an infinitive in `-er -ir -oir -re` is taken as a verb, anything else as not a verb); take only the synset's **head lemma** (`fly` from `fly.v.01`, not its synonym `wing`) and only when the synset is a **first sense** of that English word within its part of speech
   (`steal.v.01` is the first verb sense of `steal`, so `voler` → `steal`; `fly.v.07`, which OMW also lists for `voler`, is not a first sense of `fly`, so it is ignored). The translation must be a gloss some lexicon uses (`support > 0`).
3. **Where it goes.** Into every MEL that holds the translation as a gloss on its own (the same normalization). A MEL that says it is about nouns (`fly (n.)`) is skipped for a verb. One MEL gets the gloss at most once.
4. **English → French** (`falcon`, `steal`): the French lemmas of the first senses of the English word. Here the polysemy sits in the French word already in the MEL (`voler`), so a further check is made: the target MEL may have no English gloss, or one whose first sense is the same as, or a sibling of, one of the gloss's first senses
   (WordNet path similarity ≥ 0.25). `steal` is therefore **not** put into the `fly` / `voler` MEL (`rejected-other-sense`, 773 broad / 792 conservative), but `falcon` is put into the bird-of-prey MEL m0209 (`falcon` and `buzzard` are siblings under *bird of prey*).
5. **Limits.** A gloss that would go into more than 12 MELs is only listed (`too-many-targets`: `appeler`, `arriver`, `tirer`, `peau` …; 12 broad, 17 conservative). A gloss added by this layer never starts a further link (no chains).

**Example 19: `voler`.** → every MEL that holds `steal` (via `steal.v.01`: `m0660`, `m4609` `steal (to_)`), `fly` (via `fly.v.01`: `m2154` `fly (v.)`, `m3630` `to fly`) or `flee` (via `flee.v.01`: `m0469`, `m4653`); not into `m5642` (`fly (n.)`). After the subset merge (6.5b) the result in the files is `voler` in `m0660` (steal), `m0472` (fly) and the `flee` MELs, with `steal (to_)`, `fly (v.)` and `to fly` merged into those.
**Example 20: `falcon`.** English gloss of DEMO93 → French lemma `faucon` (`falcon.n.01`) → m0209 (`buse`, `buzzard`, `faucon`, `milan`, `vulture` …).
**Example 21: rejected.** `steal` → `voler` is a French lemma of `steal.v.01`, but the MEL m0472 holds `fly`, whose first sense is not near `steal`'s: not added.
**Example 22: noise that gets through.** `introduire` → `imprison` (m2292 `lock`, `imprison`, `cadenas`) and `father` → `mère` (`beget.v.01`): the French WordNet lists these senses and they are first senses of the English word. Reviewable in the TSV. Generic translations (`GENERIC` and the junk filter: `be`, `être`, `venir`, `faire`, …) are never used, to keep `être`-type MELs out of it.

### 6.5b The last step: merging subset MELs (`subset_merge()`)

After the variant layer. For each MEL the comparison set is the union, over its glosses, of `mel.normalize_gloss(gloss)` lowercased (the same normalization the engine applies to MEL glosses; the raw string is not part of the comparison because the merge appends it to the target).
For a MEL (A; a MEL with hand glosses too), the candidate targets are the MELs B whose set contains A's (identical sets: the earlier MEL is the target), minus those the part-of-speech rule excludes (A says `(n.)`: only into a target that says it too; A says `(v.)` or starts with `to`: not into one that says `(n.)`).
If one largest B remains, A's glosses that B lacks are appended to B (keeping their `source`, `layer`, `xml:lang`) and A is removed; if several unrelated Bs remain, A stays and a row `ambiguous` is written. The step repeats (up to five rounds) because a merge can make another MEL a subset. A hand MEL merged away keeps its glosses as `core` in the target (a gloss the target already had as an extra is upgraded to `core`), so no hand gloss string is lost; the log row is `merged-hand`.

**Example 23.** `m2154` (`fly (v.)`, `fly`, `voler`) and `m3630` (`to fly`, `fly`, `voler`) have the candidates `fly`, `voler`, a subset of `m0472`'s (`fly`, `voler`, `s'envoler`, `mouche`, `wing`); `m0472` becomes `fly`, `voler`, `s'envoler`, `mouche`, `wing`, `fly (v.)`, `to fly` (broad). `m5642` (`fly (n.)`, `fly`, `mouche`) is not merged: it says noun, `m0472` does not say so.
**Example 24: ambiguous.** `m0679` (`to comb`, `comb`) is a subset of four MELs (`m0277` the wool-combing MEL, `m1243` `tooth`/`comb`/`peigne`, `m2368`, `m4487`): left alone and listed.

### 6.6 What the process does not do

- WordNet is used in five places: the language tag (6.3), accent restoration (6.4), the French-dictionary check of the variant layer (6.5), the evidence for the *pairs* (6.1) and the translation layer (6.5a). It is not used for synonyms inside one language, and its senses are not stored anywhere in the files except as the TSV evidence.
- A gloss with no partner in any MEL and no WordNet translation in one is not placed anywhere. **Example 18.** `falcon` occurs only in the DEMO93 lexicons (mar, syang, tuk) and the DEMO93 hand MEL; neither the base (v4) nor any other input has it. Before the WordNet layer nothing linked it to m0209; the layer now does, through `faucon` (6.5a).
  The same holds for the 1,303 TGTM data glosses that are not an exact gloss of any broad MEL (some of them still match through the engine's phrase sub-tokens; I have not separated these).

### 6.7 The evaluation mechanism

The evaluation is a sandbox harness, not part of the build (the scripts are in the session scratchpad, `scratchpad/mel/`, which may be cleared; the results are kept in `tgtm-proposals/`). The idea:

1. **Run the engine** with each MEL on the same data and the same ToC, **strict mode** (`-w`: a form with no MEL gloss can never be in a set), so that a difference in the sets can only come from the MEL:
   `REcli.py upstream TGTM --run n-broad --recon TGTM94SETS.C794-rev1 --mel broad -z fuzzy -w` (`run.sh`; also for `TGTM94SETS` and `DEMO93`). The baseline is the same run with the hand MEL (`n-hand94`).
   The numbers are the run's sets and isolates (4.5).
2. **Regression guard against the 1994 sets** (`goldeval.py`): `SETS0111-SRT.sets.xml` has 1,015 sets, 3,073 reflexes and 5,755 cross-language form pairs. A run's pairs are compared with these (pairs of `(language, headword)`; on TGTM, where the glosses differ from the 1994 file's, headwords only).
   Precision = run pairs between forms the 1994 sets know that are also 1994 pairs; recall = 1994 pairs found. **This is used only to catch breakage, not to rank MELs**: the 1994 sets were built with the hand MEL, so it favours it (TGTM precision 0.980 hand, 0.976 conservative, 0.965 broad),
   and set counts are not a quality metric either.
3. **No pair lost.** All 5,195 cross-language `(lg, lx)` pairs of the hand94 run must still be found in both files (they are; 530 are added in broad and 169 in conservative).
   The same check, and a comparison of the sets themselves, was used to show that the v4-base build gives exactly the sets of the first, hand-based build (1,214 and 1,088 identical sets, none different).
4. **Set review** (`review.py`): each set of a run is compared with the hand94 run and classed *new* (no form in a hand94 set), *enlarged* (one hand94 set plus new forms) or neither; each is written with its MEL, extras marked `+` and variants `~`
   (`broad-new-and-enlarged-sets.tsv`, 330 rows; `conservative-new-and-enlarged-sets.tsv`, 230 rows). The quality judgement is made by reading these (an earlier spot check of 25 broad sets: about 17 right, 3 borderline, 5 wrong).
5. **Matching statistics** (`mstats.py`, `new-mel-stats.csv`): with the engine's own matcher (`mel.compile_associated_mels`) over the 7,863 forms, how many forms and languages each MEL reaches, which layer made the match, and how many MELs match a form (4.6). These describe *what matches what*; they are not precision or recall.
6. **Experiments** use the same loop. A build option changes one thing, e.g. `enriched3` instead of `enriched2` (4.5a: 1,210 against 1,214 sets, noisier new links, not adopted), or the variant layer on and off (4.3a).

Before reporting a change I checked that step 3 still holds, read the changed sets, and looked at whether the gold regression moved. For the WordNet layer the comparison is with the build without it (`n-hbbroad`-style runs: same sets listed in `*-wordnet-changed-sets.tsv`).
