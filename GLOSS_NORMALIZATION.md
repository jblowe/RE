# Gloss Normalization

*Examples and figures re-run on 2026-11-04 against `src/mel.py` as of commit `921e611`.*

This describes the gloss-normalization pipeline used to match reflex and MEL
glosses against each other (`mel.normalize_gloss`, in
[`src/mel.py`](src/mel.py)), the role of `xml:lang`, and a side-by-side
comparison against two earlier implementations that are kept in `mel.py` for
reference:

- **`normalize_gloss`** — the pipeline in use.
- **`normalize_gloss_phrases`** — steps 1–5 of `normalize_gloss` only (whole
  phrases: no phrasal-verb detection, no individual words). Used by
  [`src/merge_mels.py`](src/merge_mels.py), which merges MELs on, and writes
  out, phrase-level glosses; matching re-derives the word-level candidates
  from them. A test checks its output is always a subset of `normalize_gloss`'s.
- **`normalize_gloss_current`** — the 2.0.0 normalizer plus trailing-punctuation
  stripping: the version just before stopword removal, phrasal-verb detection
  and trailing-support-verb stripping were added. Nothing calls it.
- **`normalize_gloss_legacy`** — a verbatim port of the normalizer in the
  separate RE.dev repository (`src/mel.py:67` there). Only the comparison
  script calls it.

**What changed since 2.0.0.** Four things were added to the normalizer itself:
trailing-punctuation stripping, trailing support verbs, English phrasal verbs
(confirmed with WordNet) and stopword removal. Two further changes are in the
matching code that calls it (`compile_associated_mels`): MEL glosses now go
through the same normalization as reflex glosses (in 2.0.0 only reflex glosses
were normalized, so a MEL gloss such as `badigeonner (avec terre)` could not
match the reflex `badigeonner`), and all candidates are compared in lower case
(2.0.0 compared exactly). Everything else in the pipeline below, including
never splitting on spaces, is as in 2.0.0.

## Background: NLTK and WordNet

[NLTK](https://www.nltk.org/) (Natural Language Toolkit) is a Python library
bundling common NLP resources and utilities — tokenizers, part-of-speech
taggers, stopword lists for dozens of languages, and access to lexical
databases. We use two pieces of it here: its packaged **stopword lists**
(closed-class function words — "the", "of", "but", "de", "le" — that carry
little content meaning on their own) and its interface to
**[WordNet](https://wordnet.princeton.edu/)**, a large lexical database of
English built at Princeton. WordNet groups words into *synsets* (sets of
synonyms sharing a sense) and, usefully for us, already treats many English
phrasal verbs as their own lexical entries distinct from the bare verb —
`give_up` (abandon), `give_away` (donate), `give_in` (yield) each have their
own synsets and definitions, separate from `give` itself (which has 45
unrelated senses). That's what makes WordNet lookup a good *arbiter* for
"is this really a phrasal verb," rather than just a heuristic guess.

The code reads only NLTK's `stopwords` and `wordnet` corpora (the install
instructions in [`src/README.md`](src/README.md) also fetch `omw-1.4`).
`punkt_tab` and `averaged_perceptron_tagger_eng`, which were installed while
exploring part-of-speech tagging, are not used.

## Status: live

`mel.normalize_gloss(gloss, lang=None)` — the function the matching
code actually uses (via `_candidates_lower`, called from
`compile_associated_mels`) — is the full
pipeline described below. It was first evaluated as a separate copy
(`normalize_gloss_experimental`); once the comparison further down looked good
it was promoted, and a later commit (`921e611`, 2026-07-14) added
trailing-support-verb stripping and the French `avoir`/`être` stopwords.

`mel.normalize_gloss_legacy(gloss)` is a verbatim port of the RE.dev
implementation. It needed no adaptation: the original only used `re`, already
imported here. One trivial fix was applied while porting — the original had
`re.sub('\|.*', ...)`, an invalid escape sequence Python warns about; changed
to the equivalent raw string `r'\|.*'`, with no behavior change. It is not
called from anywhere in the pipeline — comparison only, like
`normalize_gloss_current`.

Three small scripts in `src/` exercise the normalizers on real glosses; none
is part of the pipeline (see [Reproducing the examples](#reproducing-the-examples)).
The examples below are hand-picked from the 5,153 distinct reflex glosses of
TGTM's ten attested lexicons, plus a handful of French examples from
`TGTM.hand-extended-v4.mel.xml` (an external MEL file, not part of this repo,
that already tags some glosses with `xml:lang`).

## The gory details: `xml:lang`

**Where it exists today.** Some MEL files carry `xml:lang` on individual
`<gl>` elements, e.g. `TGTM.hand-extended-v4.mel.xml`:

```xml
<gl xml:lang="xx">sari</gl>
<gl xml:lang="en">dhoti</gl>
<gl xml:lang="fr">abandonner</gl>
```

`xx` shows up as a placeholder/unspecified-language code on some entries;
`en`/`fr` are the two languages actually in use. **Not every `<gl>` has the
attribute** — plenty have no `xml:lang` at all, and that's expected to
remain true. **No attested-lexicon `<gl>` currently carries `xml:lang`** —
reflex glosses are to be **"uptagged"** with it, so the code already
threads a `lang` argument through in anticipation, even though today it's
always `None` on the reflex side.

**How it's captured.** `read.read_mel_file` reads each `<gl>`'s
`{http://www.w3.org/XML/1998/namespace}lang` attribute (the fully-qualified
name ElementTree uses internally for the reserved `xml:` namespace) into
`mel.Mel.gloss_langs`, a `{gloss_text: lang_code}` dict covering only the
glosses that actually had the attribute. `coverage.py` and `serialize.py`
carry it into the coverage report as `<gl xml:lang="...">`, and
`coverage2html.xsl` renders it as a `<sub>` next to the gloss — the same way
`mel2html.xsl` already renders it straight from the MEL file.
`normalize_gloss(gloss, lang=...)` is the same idea one level down: given
the language (from `Mel.gloss_langs.get(gloss)` on the MEL side, or
eventually a reflex form's own tag), pick the right stopword list and
decide whether to even attempt (English) phrasal-verb detection. Note that
the matching code's call (in `_candidates_lower`) does not pass `lang` yet, so
in production `normalize_gloss` is always called with `lang=None` today, even for MEL glosses whose `Mel.gloss_langs`
would give a real answer — wiring that through is one of the open questions
below.

**The fallback policy — union, not a guess.** When `lang` is `None`
(unknown) or an unrecognized code (like `xx`), stopword removal uses the
**union** of English and French stopwords rather than picking one language
or skipping filtering. We checked empirically rather than assuming: the two
NLTK lists overlap by only 9 entries, all harmless elided-contraction
fragments (`m`, `d`, `t`, `s`, `y`, `on`, `ma`, `as`, `me`) that are function
words in both languages. (We'd worried French "or" — gold, a content noun —
might collide with English "or" the conjunction; it doesn't, "or" isn't in
NLTK's French list at all, only "ou" is.) So unioning is low-risk and covers
untagged glosses in either language. The French list is NLTK's plus `avoir`
and `être`.

**French support verbs and the English `to`/`be` marker.** The step that
strips a leading grammar particle (`_strip_particles`) knows only the English
markers `to` and `be`, so `be old` becomes `old`. French has no leading-marker
equivalent, but the two cases that matter are now covered another way
(`921e611`):

- `être` and `avoir` are French **stopwords**, so they are never offered as
  individual-word candidates: `être vieux` ("be old") gives `être vieux`,
  `vieux`, and `avoir soif` gives `avoir soif`, `soif`. The phrase itself is
  kept whole, with its leading verb, because the phrase-level candidate is the
  one a MEL gloss written the same way would match.
- A **trailing** support verb is stripped before splitting, in both languages
  (`, be`, `, to be`, `, avoir`, `, être`), so it cannot survive as a
  phrase-level candidate.

What is still not symmetric is that a leading `être`/`avoir` is not removed
from the phrase itself, as `be` is. And in the other direction, a
mixed-language data-entry artifact — `<gl xml:lang="fr">to danse</gl>` — has
its English `to` stripped even though the entry is tagged French, giving
`danse` (correct output, coincidentally, but for the wrong reason). None of
this breaks anything; it is an honest account of what `lang`-awareness does
not cover.

**Phrasal-verb detection is English-only.** `_PHRASAL_PARTICLES` is a dict
keyed by `xml:lang` code so a French list can be added later
(`_find_phrasal_verb` already looks it up by `lang`), but only `'en'` is
populated right now. For any `lang` other than `en`/`None`, phrasal-verb
detection is skipped outright.

## The pipeline, in order

Steps marked *new* were added after 2.0.0. "Before" for those rows is
2.0.0's actual output, from running its normalizer.

| # | Process | What it does | English examples (before → after) | French examples (before → after) |
|---|---|---|---|---|
| 1 | **Remove parenthesized/bracketed asides** | Strips `(...)`, `[...]`, `<...>` and their contents | `(plural)` → *(empty — dropped; TGTM's bracketed glosses are whole grammatical annotations, not asides)*<br>`(*imperative of verb roots ending in a short vowel)` → *(empty, same reason)* | `casser (maïs)` → `casser`<br>`emprunter (objet)` → `emprunter` |
| 2 | **Remove keyterm marker** | Strips a bare `*` (Lexware/Toolbox proto-form marker) | `*again` → `again`<br>`*O.K.` → `O.K` *(the final `.` goes in step 5)* | *(no French example found with a bare, non-parenthesized `*` in the sampled data)* |
| 3 | **Handle Lexware `\|` variants** | `a\|b` is tried both as `ab` (joined) and `a` (truncated at `\|`) | `call for buffaloe\|s` → `call for buffaloes`, `call for buffaloe` (both variants carried forward) | *(no French `\|` example found in the sampled data — Lexware `\|` is a Toolbox/English-lexicon-file convention here)* |
| 4 | **Strip a trailing support verb** *(new)* | Drops a trailing `, be`, `, to be`, `, avoir` or `, être` before splitting. Without it the bare verb survives as a phrase-level candidate, because stopword removal only touches the individual-word step | `born, be` → `born` (before: `born`, `be`)<br>`bend/bent, be` → `bend`, `bent` (before: also `be`)<br>`become, to be` → `become` | *(no `, être` / `, avoir` gloss in the sampled data; the rule covers both)* |
| 5 | **Split into phrases; strip trailing punctuation** | Splits each variant on `/ , ; :` — but *not* on spaces, since multi-word phrases (like MEL glosses) must survive intact. *New:* a surrounding `?` and a trailing `!` or `.` are removed | `abandon/cast away` → `abandon`, `cast away`<br>`base, depth, the palm of the hand` → `base`, `depth`, `the palm of the hand` *(phrases only)*<br>`*here!` → `here` (before: `here!`) | `démon, monstre` → `démon`, `monstre`<br>`hauteur, longueur` → `hauteur`, `longueur`<br>`aimer qqch.` → `aimer qqch`, `aimer`, `qqch` (before: `aimer qqch.`, `aimer`, `qqch.`) |
| 6 | **Strip leading particles** | Drops a leading English `to`/`be` from a phrase | `approve, to confirm` → `approve`, `confirm`<br>`lose, be defeated` → `lose`, `defeated` | *(English only — a leading `être`/`avoir` stays in the phrase and is dropped from the individual words in step 9)*<br>`être vieux` → `être vieux`, `vieux` |
| 7 | **Detect phrasal verbs** *(new, English only)* | A candidate particle (from a fixed list) after the first word, confirmed as a genuine WordNet lemma (`verb_particle`), becomes its own candidate; the bare verb and particle stop being offered as separate, potentially-misleading candidates | `give up the ship` → adds `give up` (not `give`, `up` separately)<br>`look after the children` → adds `look after` (not `look`, `after`)<br>`bring a log back towards the center of the fire` → adds `bring back` (particle not adjacent to the verb — a *separable* phrasal verb) | *(not attempted — no French particle list yet; would need one before this step does anything for `lang='fr'`)* |
| 8 | **Extract individual words** | Every remaining word in a phrase is also offered as its own candidate | `adult female` → `adult`, `female`<br>`vésicule biliaire` → `vésicule`, `biliaire` | `égrener le maïs` → `égrener`, `le`, `maïs` *(before stopword removal)* |
| 9 | **Remove stopwords** *(new)* | Drops function words from the individual-word candidates of step 8; the stopword list is chosen by `xml:lang` (English, French — which also includes `avoir` and `être` — or their union if unknown) | `back of the body` → `back`, `body` (`of`, `the` dropped; before: `back`, `of`, `the`, `body`)<br>`any of a number of plants whose seed catches on clothes` → `number`, `plants`, `whose`, `seed`, `catches`, `clothes` | `céréale cuite de sarrazin` (`lang="fr"`) → `céréale`, `cuite`, `sarrazin` (`de` dropped)<br>`égrener le maïs` (`lang="fr"`) → `égrener`, `maïs` (`le` dropped) |
| 10 | **Deduplicate** | Preserves first-seen order (phrases, then phrasal verbs, then words); drops exact repeats | `break, break down` → `break`, `break down` (not `break` twice)<br>`come back, to bring back` → `come back`, `bring back` (not also bare `come`, `back`, `bring`) | *(same mechanism, language-independent — no separate French example needed)* |

### A combined example

Because these steps interact, a single real gloss often shows several at
once. `bring a log back towards the center of the fire` (English, no tag)
becomes:

```
('bring a log back towards the center of the fire',
 'bring back', 'log', 'towards', 'center', 'fire')
```

— the phrasal verb `bring back` is pulled out (separable, particle several
words after the verb), stopwords `a`, `the`, `of` are gone from the
individual-word candidates, and the original full phrase is still kept as a
candidate in its own right.

## Comparison against the legacy implementation

`normalize_gloss_legacy` is much cruder than either of the later versions: **no**
parenthetical/bracket handling at all (those characters just stay glued to
whatever word they're next to, since splitting is on `/`, ` `, `,` only),
**no** leading-particle stripping, and — critically — it **splits on
spaces**, so a multi-word MEL gloss like `Ficus religiosa` or `Bermuda grass`
can never survive as its own match candidate, only its individual words can.
It also returns a plain list with no deduplication.

**Methodology.** A standalone script,
[`src/compare_normalize_gloss.py`](src/compare_normalize_gloss.py), reads two
gloss lists generated from TGTM by
[`src/generate_tgtm_gloss_lists.py`](src/generate_tgtm_gloss_lists.py): the
5,153 distinct reflex glosses from TGTM's ten attested lexicons
(`tgtm_reflex_glosses.txt`), plus 8,144 distinct glosses from
`TGTM.hand-extended-v4.mel.xml` (`tgtm_mel_glosses.txt`). It tags each row
with its source (`reflex` or `mel`), runs both `normalize_gloss_legacy` and
`normalize_gloss` on every one of the 13,297 resulting glosses, and writes a
TSV: `seq`, `source`, `gloss`, `score`, `legacy_count`, `legacy`,
`new_count`, `new`. The mel gloss file carries `xml:lang` as a second
tab-separated column for the 4,684 glosses that had it in the source MEL
file (`normalize_gloss` is called with that language, unlike its production
callers — see the note in the `xml:lang` section above); the reflex gloss
file has no language column at all yet (attested lexicons aren't tagged),
so those rows always use `lang=None` (see the `xml:lang` section above for
what that falls back to).

A direct `==` between the two would call almost everything different even
when they substantially agree, since legacy returns a plain,
non-deduplicated list and normalize_gloss a deduplicated tuple in a
different order. So both are instead treated as a *set* of candidate
keyterms: `score` is their **Jaccard similarity** (`|intersection| /
|union|` — 1.0 when the two functions found exactly the same keyterms, 0.0
when they share none, in between for partial overlap), and
`legacy_count`/`new_count` are the number of *unique* keyterms each one
produced.

**A parsing gotcha the data itself turned up.** A handful of real gloss
strings contain a literal embedded tab character (e.g.
`a\tfraction, to divide`, `get up\t(v.i.)`) — a data-entry artifact, not
something we introduced. The first version of the gloss-list reader
naively split every line on its first tab, so these got silently mangled:
`a\tfraction, to divide` became gloss=`a`, "lang"=`fraction, to divide`. The
fix: split only on the *last* tab, and only treat it as a lang tag if what
follows is actually a plausible code (`en`/`fr`/`xx`, or in
`eval_normalize_gloss.py`'s more generic reader, anything matching
`[a-z]{2,3}`); otherwise the whole line — embedded tab included — is the
gloss and `lang` is `None`. Affects 1 reflex gloss and 7 mel glosses out of
13,297; the numbers below are post-fix.

**Headline numbers** (13,297 glosses, normalizer as of `921e611`).

- **Mean Jaccard score: 0.746.**
- **7,028 rows (52.9%) score a perfect 1.0** — the two functions found
  exactly the same keyterms.
- **442 rows (3.3%) score 0.0** — completely disjoint.
- **5,827 rows (43.8%)** land somewhere in between (partial overlap).

**Sample rows.**

| seq | source | gloss | score | legacy_count | legacy | new_count | new |
|---|---|---|---|---|---|---|---|
| 3 | reflex | `(*imperative of consonantic verb-roots)` | 0.000 | 4 | `['(imperative', 'of', 'consonantic', 'verb-roots)']` | 0 | `()` |
| 99 | reflex | `abandon/cast away` | 0.250 | 3 | `['abandon', 'cast', 'away']` | 2 | `('abandon', 'cast away')` |
| 101 | reflex | `abcess` | 1.000 | 1 | `['abcess']` | 1 | `('abcess',)` |
| 103 | reflex | `able, to be healthy, to be cure\|d` | 0.667 | 6 | `['able', 'to', 'be', 'healthy', 'to', 'be', 'cured', 'cure']` | 4 | `('able', 'healthy', 'cured', 'cure')` |
| 657 | reflex | `call for buffaloe\|s` | 0.286 | 4 | `['call', 'for', 'buffaloes', 'buffaloe']` | 5 | `('call for buffaloes', 'call for', 'call for buffaloe', 'buffaloes', 'buffaloe')` |
| 5725 | mel | `Bermuda grass` | 0.667 | 2 | `['Bermuda', 'grass']` | 3 | `('Bermuda grass', 'Bermuda', 'grass')` |
| 5734 | mel | `Ficus religiosa` | 0.667 | 2 | `['Ficus', 'religiosa']` | 3 | `('Ficus religiosa', 'Ficus', 'religiosa')` |

Row 5734 is a good worst case for legacy: a Latin binomial species name.
Legacy offers only `Ficus` and `religiosa` as separate match candidates —
either could spuriously match an unrelated MEL entry (a different fig
species, or the unrelated concept "religious"). The new pipeline keeps
`Ficus religiosa` intact as its own candidate while still offering the
individual words too. Note its score (0.667) is identical to `Bermuda
grass`'s — same shape of disagreement (legacy's 2 words are a subset of
normalize_gloss's 3 candidates), so the same Jaccard value, even though the
actual words differ. `abcess` (nothing to normalize) is the trivial case:
both produce the exact same single-item set, so 1.000. `(*imperative of
consonantic verb-roots)` is the opposite trivial case: legacy extracts 4
broken word-fragments, normalize_gloss correctly recognizes pure bracketed
annotation and produces nothing — 0 shared, 0.000.

## Reproducing the examples

The three scripts and where they stand:

- [`src/generate_tgtm_gloss_lists.py`](src/generate_tgtm_gloss_lists.py) — the
  one script that needs the external TGTM data (it expects
  `~/GitHub/RE-Tamangish-Files/TGTM`). It writes the two gloss lists next to
  itself.
- [`src/eval_normalize_gloss.py`](src/eval_normalize_gloss.py) — generic
  single-function evaluator (any gloss file in, `normalize_gloss` results
  out).
- [`src/compare_normalize_gloss.py`](src/compare_normalize_gloss.py) — the
  legacy-vs-current comparison above.

**The two gloss lists are not checked in** (`tgtm_reflex_glosses.txt` and
`tgtm_mel_glosses.txt`; they are derived from external data and regenerate
in seconds), and neither is the 13,297-row output TSV. To reproduce:

```bash
cd src
python3 generate_tgtm_gloss_lists.py        # writes the two .txt lists here
python3 compare_normalize_gloss.py out.tsv  # writes the comparison TSV
```

Because a few glosses contain literal tabs (see above), compute statistics
from the lists in code rather than by splitting the TSV on tabs.

## Open questions / next steps

- Wire `lang` through `compile_associated_mels`/`_candidates_lower` for the
  MEL side (`Mel.gloss_langs.get(mel_gloss)` is already sitting right
  there). Today even production calls go through with `lang=None`, so
  `xml:lang`-aware stopword and phrasal-verb behavior is exercised only by the
  eval and compare scripts, which pass it explicitly, and not by a real run.
- Add a French particle list for step 7 (phrasal-verb detection).
- Once attested lexicons are "uptagged" with `xml:lang`, thread that through
  `read.read_lexicon`/`RE.ModernForm` the same way `Mel.gloss_langs` already
  works for MEL files, so reflex-side glosses stop defaulting to `lang=None`.
- Decide whether a leading `être`/`avoir` should be stripped from the phrase
  (as `be` is). Today it is only dropped from the individual words.
- Splitting `normalize_gloss`/`normalize_gloss_current`/`normalize_gloss_legacy`
  (and their shared helpers) into their own module was considered and
  declined: they share private state with the MEL-matching half of
  `mel.py` (`compile_associated_mels`/`_candidates_lower` call directly into
  them and need `Mel.gloss_langs`), so a split would mean making several
  underscore-prefixed helpers public just to import them across two files.
  Not worth it at about 330 lines.
