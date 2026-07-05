import mel
import utils
from RE import Statistics, ProtoForm
from collections import Counter, defaultdict


# ── Per-language MEL-vocabulary coverage ────────────────────────────────────
#
# How much of each language's raw gloss vocabulary is covered by the MEL, and
# how much of the MEL's vocabulary is actually used. This reuses the run's
# already-read lexicons and already-compiled association table -- nothing
# here re-reads a file or re-normalizes a gloss.
def check_mel_coverage(mels, attested_lexicons, associated_mels_table):
    coverage_statistics = Statistics()
    mel_glosses = set()
    for m in (mels or []):
        mel_glosses |= set(m.glosses)

    glosses_not_matched_by_language = {}
    unmatched_glosses = set()
    matched_glosses = set()
    used_mel_ids = set()
    # Real per-synonym usage counts: (mel_id, synonym_gloss) -> number of
    # distinct input glosses that matched via that specific synonym. A single
    # input gloss can match more than one synonym of the same MEL (e.g. a
    # descriptive gloss containing both "grain" and "rice"), so this can't be
    # derived from used_mel_ids alone -- mel.matched_synonyms() recovers the
    # specific synonym(s) from the same association table built once for the
    # whole run, no extra matching pass required.
    synonym_usage = Counter()
    all_matched = all_not_matched = all_forms = 0
    glosses = Counter()

    for language, lexicon in attested_lexicons.items():
        glosses_not_matched_by_language[language] = set()
        matched = not_matched = 0
        forms = len(lexicon.forms)
        for gloss in utils.glosses_by_language(lexicon):
            glosses[gloss] += 1
            matched_mels = (mel.associated_mels(associated_mels_table, gloss, True)
                            if associated_mels_table is not None else [])
            if matched_mels:
                matched += 1
                matched_glosses.add(gloss)
                used_mel_ids.update(m.id for m in matched_mels)
                for m in matched_mels:
                    for syn in mel.matched_synonyms(associated_mels_table, gloss, m):
                        synonym_usage[(m.id, syn)] += 1
            else:
                not_matched += 1
                glosses_not_matched_by_language[language].add(gloss)
                unmatched_glosses.add(gloss)

        print(f'{language}: {matched + not_matched} distinct glosses, {matched} matched, {not_matched} did not match, {forms} forms')
        coverage_statistics.language_stats[language] = {
            'input_glosses': matched + not_matched,
            'matched': matched,
            'not_matched': not_matched,
            'forms': forms
        }
        all_matched += matched
        all_not_matched += not_matched
        all_forms += forms

    number_of_mels = len(mels or [])
    unused_mels = number_of_mels - len(used_mel_ids)
    mel_usage = {}
    for m in (mels or []):
        mel_usage[m.id] = {gl: synonym_usage.get((m.id, gl), 0) for gl in m.glosses}
        mel_usage[m.id]['usage'] = m.id in used_mel_ids

    # unused_mel_glosses/used_mel_glosses are counted over the same domain as
    # number_of_mels_glosses -- distinct gloss *strings*, not (mel, gloss)
    # slots. The same string can appear as a synonym in more than one MEL
    # (e.g. "shoulder" in both es9 and es14); a string counts as used if any
    # MEL slot bearing it was matched, so the two stats stay consistent
    # (mismatching domains previously made used_mel_glosses go negative).
    used_gloss_strings = {gl for (mel_id, gl), count in synonym_usage.items() if count > 0}
    unused_mel_glosses = len(mel_glosses - used_gloss_strings)

    coverage_statistics.add_stat('distinct_input_glosses', len(glosses))
    coverage_statistics.add_stat('unused_mels', unused_mels)
    coverage_statistics.add_stat('number_of_mels', number_of_mels)
    coverage_statistics.add_stat('number_of_mels_glosses', len(mel_glosses))
    coverage_statistics.add_stat('unused_mel_glosses', unused_mel_glosses)
    coverage_statistics.add_stat('used_mel_glosses', len(mel_glosses) - unused_mel_glosses)

    coverage_statistics.unmatched_by_language = glosses_not_matched_by_language
    coverage_statistics.unmatched_glosses = unmatched_glosses
    coverage_statistics.matched_glosses = matched_glosses
    coverage_statistics.mel_usage = mel_usage
    # {mel_id: {gloss_text: xml:lang value}}, straight from the MEL file (see
    # read.read_mel_file / mel.Mel.gloss_langs) -- carried through so
    # serialize.py can render it on <gl> the same way mel2html.xsl does.
    coverage_statistics.mel_gloss_langs = {m.id: m.gloss_langs
                                           for m in (mels or []) if m.gloss_langs}

    print(f'\nmel summary: mels {number_of_mels}, mel glosses {len(mel_glosses)}, unused mel glosses {unused_mel_glosses}, unused mels {unused_mels}')
    print(f'gloss summary: {all_matched + all_not_matched} distinct glosses, {all_matched} matched, {all_not_matched} did not match, {all_forms} forms')

    return coverage_statistics


def check_glosses(settings, args, glosses):
    x = settings
    g = glosses
    pass


# ── Annotated coverage: which MEL each attested reflex actually landed under ──
#
# Built in one pass, directly from the finished root-level run (sets,
# isolates, failures) plus the same association table used to build those
# sets in the first place. This replaces the old mel_annotated.py, which
# re-parsed sets.xml/coverage.xml from disk and rebuilt a second, independent
# search index to recover exactly this information after the fact.
def _reflex_display(form):
    """(glyphs, gloss) for a leaf supporting form, using the pre-fuzzy
    surface form when one exists (matches what sets.xml itself displays)."""
    actual = getattr(form, 'actual', None)  # FuzzyForm / QuirkyForm
    glyphs = actual.glyphs if actual is not None else form.glyphs
    return glyphs, (getattr(form, 'gloss', '') or '')


def build_annotated_coverage(mels, associated_mels_table, languages, root_lexicon):
    mel_forms = defaultdict(list)      # (mel_id, lang) -> [(glyphs, status, gl)]
    seen_mel_forms = set()             # (mel_id, lang, glyphs) dedup
    pseudo_forms = defaultdict(list)   # gloss -> [(lang, glyphs, status, gl)]
    seen_pseudo = set()                # (gloss, lang, glyphs, status) dedup
    # The root-level reconstruction(s) (the Protoform itself, e.g. "*toŋ")
    # associated with each MEL -- one entry per distinct set/isolate that
    # landed under that MEL. Colored the same way as mesolanguage badges.
    mel_reconstructions = defaultdict(list)  # mel_id -> [(glyphs, status)]
    seen_reconstructions = set()             # (mel_id, glyphs, status) dedup
    meso_included = 0
    meso_excluded = 0

    def real_mel(m):
        return m if (m and getattr(m, 'glosses', None)) else None

    def add_form(mel_id, lang, glyphs, status, gl):
        key = (mel_id, lang, glyphs)
        if key not in seen_mel_forms:
            seen_mel_forms.add(key)
            mel_forms[(mel_id, lang)].append((glyphs, status, gl))

    def add_reconstruction(mel_id, glyphs, status):
        key = (mel_id, glyphs, status)
        if key not in seen_reconstructions:
            seen_reconstructions.add(key)
            mel_reconstructions[mel_id].append((glyphs, status))

    def add_pseudo(gl, lang, glyphs, status):
        key = (gl, lang, glyphs, status)
        if key not in seen_pseudo:
            seen_pseudo.add(key)
            pseudo_forms[gl or '?'].append((lang, glyphs, status, gl))

    def resolve_by_gloss(gl, lang, glyphs, status):
        matched = (mel.associated_mels(associated_mels_table, gl, True)
                  if (associated_mels_table is not None and gl) else [])
        if matched:
            for m in matched:
                add_form(m.id, lang, glyphs, status, gl)
        elif gl and gl != 'missing':
            add_pseudo(gl, lang, glyphs, status)

    # Recursively walk a set's supporting-forms tree (mirrors the recursion
    # serialize.render_xml uses to write sets.xml): leaves are attested
    # reflexes; internal nodes are mesolanguage (intermediate proto-language)
    # reconstructions.
    def walk_set(form, set_mel, status):
        nonlocal meso_included, meso_excluded
        for sf in form.supporting_forms:
            if isinstance(sf, ProtoForm):
                if set_mel is not None:
                    meso_included += 1
                    add_form(set_mel.id, sf.language, '*' + sf.glyphs, status, '')
                else:
                    meso_excluded += 1
                walk_set(sf, set_mel, status)
            else:
                glyphs, gl = _reflex_display(sf)
                if set_mel is not None:
                    add_form(set_mel.id, sf.language, glyphs, status, gl)
                else:
                    # This set has no single unifying real MEL (only_with_mel
                    # was off): fall back to resolving each reflex's own gloss.
                    resolve_by_gloss(gl, sf.language, glyphs, status)

    for pf in getattr(root_lexicon, 'forms', []):
        set_mel = real_mel(pf.mel)
        if set_mel is not None:
            add_reconstruction(set_mel.id, pf.glyphs, 'set')
        walk_set(pf, set_mel, 'set')

    for form, proto_forms in getattr(root_lexicon, 'isolates_dict', {}).items():
        glyphs, gl = _reflex_display(form)
        real_mels = set()
        for pf in proto_forms:
            m = real_mel(pf.mel)
            if m is not None:
                real_mels.add(m)
                add_reconstruction(m.id, pf.glyphs, 'isolate')
        if real_mels:
            for m in real_mels:
                add_form(m.id, form.language, glyphs, 'isolate', gl)
        else:
            resolve_by_gloss(gl, form.language, glyphs, 'isolate')

    for form in getattr(root_lexicon, 'failures', []):
        glyphs, gl = _reflex_display(form)
        resolve_by_gloss(gl, form.language, glyphs, 'failure')

    stats = Statistics()
    stats.languages = list(languages)
    stats.mel_forms = mel_forms
    stats.pseudo_forms = pseudo_forms
    stats.mel_reconstructions = mel_reconstructions
    stats.add_stat('meso_included', meso_included)
    stats.add_stat('meso_excluded', meso_excluded)
    return stats


# ── Single entry point: the whole coverage.xml in one Statistics object ─────
#
# Combines the vocabulary-coverage summary and the annotated per-MEL,
# per-language, per-status table -- the two things that used to live in
# separate files (coverage.xml written here, then re-derived at request time
# by mel_annotated.py). Call this once, right after the root-level run
# finishes (B.isolates_dict / B.failures already set), and hand the result
# straight to serialize.serialize_stats.
def build_coverage_statistics(mels, attested_lexicons, associated_mels_table,
                              languages, root_lexicon):
    stats = check_mel_coverage(mels, attested_lexicons, associated_mels_table)
    annotated = build_annotated_coverage(
        mels, associated_mels_table, languages, root_lexicon)
    stats.languages = annotated.languages
    stats.mel_forms = annotated.mel_forms
    stats.pseudo_forms = annotated.pseudo_forms
    stats.mel_reconstructions = annotated.mel_reconstructions
    stats.summary_stats.update(annotated.summary_stats)
    return stats
