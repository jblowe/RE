"""Tests for the counts shown in the ToC, Fuzzy, Coverage and MEL views.

Every count in the ToC / classes / fuzzy views and in the Coverage report is a
count of REFLEXES IN COGNATE SETS (each reflex at most once per item); the MEL
pane counts entries in the lexicons as a whole. These tests build tiny,
self-contained fixtures so they do not depend on any project on disk (except
one end-to-end run of the small bundled DIS project).
"""

import os
import types

import lxml.etree as ET
import pytest

import RE
import mel as mel_module
import coverage
import serialize
import xslt   # REwww/xslt.py (conftest puts REwww/ on sys.path)


# ── helpers ───────────────────────────────────────────────────────────────────

def corr(num, proto, **daughters):
    """A Correspondence whose daughter cells are given per language."""
    return RE.Correspondence(num, (None, None), ['CV'], proto, dict(daughters))


def modern(language, glyphs, gloss='g'):
    return RE.ModernForm(language, glyphs, gloss, f'{language}-{glyphs}-{gloss}')


def params(name='proto', fuzzy=None):
    return types.SimpleNamespace(proto_language_name=name, fuzzy=fuzzy)


def proto_form(correspondences, forms, mel=None, language='proto'):
    attested = frozenset().union(*(f.attested_support for f in forms))
    return RE.ProtoForm(language, correspondences, frozenset(forms), attested, mel)


# ─────────────────────────────────────────────────────────────────────────────
# align_parse: which variant ("seg") of each correspondence matched
# ─────────────────────────────────────────────────────────────────────────────

class TestAlignParse:
    c1 = corr('1', 'p', L=['p', 'pʰ'], M=['b'])
    c2 = corr('2', 'a', L=['a'], M=['a'])
    epen = corr('3', 'i', L=['∅', 'i'], M=['i'])

    @staticmethod
    def acc(language):
        return lambda c: c.daughter_forms.get(language) or []

    def test_plain_variant(self):
        r = RE.align_parse((self.c1, self.c2), 'pa', self.acc('L'))
        assert [(c.id, i) for c, i in r] == [('1', 0), ('2', 0)]

    def test_second_variant(self):
        r = RE.align_parse((self.c1, self.c2), 'pʰa', self.acc('L'))
        assert [(c.id, i) for c, i in r] == [('1', 1), ('2', 0)]

    def test_other_language(self):
        r = RE.align_parse((self.c1, self.c2), 'ba', self.acc('M'))
        assert [(c.id, i) for c, i in r] == [('1', 0), ('2', 0)]

    def test_epenthesis_consumes_nothing(self):
        r = RE.align_parse((self.c1, self.epen, self.c2), 'pa', self.acc('L'))
        assert [(c.id, i) for c, i in r] == [('1', 0), ('3', 0), ('2', 0)]

    def test_epenthesis_variant_that_is_present(self):
        r = RE.align_parse((self.c1, self.epen, self.c2), 'pia', self.acc('L'))
        assert [(c.id, i) for c, i in r] == [('1', 0), ('3', 1), ('2', 0)]

    def test_no_alignment(self):
        assert RE.align_parse((self.c1, self.c2), 'xa', self.acc('L')) is None
        assert RE.align_parse((self.c1, self.c2), 'pab', self.acc('L')) is None

    def test_fuzzied_token_matches_its_fuzzied_key(self):
        # the table's 'pʰ' is fuzzied to 'p', so a fuzzied form 'pa' aligns to it
        c = corr('9', 'p', L=['pʰ'])
        r = RE.align_parse((c, self.c2), 'pa', self.acc('L'), {'pʰ': 'p'})
        assert [(x.id, i) for x, i in r] == [('9', 0), ('2', 0)]

    def test_unfuzzed_token_preferred_when_keys_coincide(self):
        r = RE.align_parse((self.c1, self.c2), 'pa', self.acc('L'), {'pʰ': 'p'})
        assert [(c.id, i) for c, i in r] == [('1', 0), ('2', 0)]

    def test_missing_language_cell(self):
        # a language with no cell ('' in the table) matches nothing
        c = corr('4', 'z', L='')
        assert RE.align_parse((c,), 'z', self.acc('L')) is None


# ─────────────────────────────────────────────────────────────────────────────
# tally_set_usage: reflexes in sets, each at most once per item
# ─────────────────────────────────────────────────────────────────────────────

class TestTallySetUsage:
    c1 = corr('1', 'p', L=['p', 'pʰ'], M=['b'])
    c2 = corr('2', 'a', L=['a'], M=['a'])

    def _tally(self, roots, parameters=None):
        stats = RE.Statistics()
        RE.tally_set_usage(roots, {'proto': parameters or params()}, stats)
        return stats

    def two_sets(self):
        s1 = proto_form((self.c1, self.c2), [modern('L', 'pʰa'), modern('M', 'ba')])
        s2 = proto_form((self.c1, self.c2), [modern('L', 'pa', 'h'), modern('M', 'ba', 'h')])
        return [s1, s2]

    def test_rows_cells_segs(self):
        stats = self._tally(self.two_sets())
        u = stats.toc_usage['proto']
        assert u['rows'] == {'1': 4, '2': 4}
        assert u['cells'] == {('1', 'L'): 2, ('1', 'M'): 2, ('2', 'L'): 2, ('2', 'M'): 2}
        assert u['segs'][('1', 'L', 0)] == 1          # 'pa'
        assert u['segs'][('1', 'L', 1)] == 1          # 'pʰa'
        assert u['segs'][('1', 'M', 0)] == 2
        assert u['segs'][('2', 'L', 0)] == 2
        assert stats.alignment_failures == 0

    def test_item_used_twice_in_one_word_counts_once(self):
        s = proto_form((self.c1, self.c2, self.c1), [modern('L', 'pap'), modern('M', 'bab')])
        u = self._tally([s]).toc_usage['proto']
        assert u['rows']['1'] == 2 and u['cells'][('1', 'L')] == 1
        assert u['segs'][('1', 'L', 0)] == 1

    def test_alternative_and_original_of_one_reflex_count_once(self):
        original = modern('L', 'pʰa')
        alternative = RE.QuirkyForm('pa', original)   # shares attested_support
        s = proto_form((self.c1, self.c2), [original, alternative, modern('M', 'ba')])
        u = self._tally([s]).toc_usage['proto']
        assert u['cells'][('1', 'L')] == 1

    def test_unalignable_reflex_still_counts_rows_but_is_reported(self):
        s = proto_form((self.c1, self.c2), [modern('L', 'qq'), modern('M', 'ba')])
        stats = self._tally([s])
        assert stats.alignment_failures == 1
        assert stats.toc_usage['proto']['rows']['1'] == 2
        assert ('1', 'L', 0) not in stats.toc_usage['proto']['segs']

    def test_fuzzy_rules_counted_once_per_reflex_in_sets_only(self):
        fuzzied = RE.FuzzyForm('pa', modern('L', 'pʰa'))
        fuzzied.rules_fired = [('L', 'pʰ'), ('L', 'pʰ')]        # fired twice in one form
        in_set = proto_form((self.c1, self.c2), [fuzzied, modern('M', 'ba')])
        # a second fuzzied reflex that is NOT in any set must not be counted
        RE.FuzzyForm('pa', modern('L', 'pʰa', 'isolate')).rules_fired.append(('L', 'pʰ'))
        stats = self._tally([in_set], params(fuzzy={('L', 'pʰ'): 'p'}))
        assert stats.fuzzy_usage == {('L', 'pʰ'): 1}

    def test_derivations_of_one_set_do_not_multiply_counts(self):
        # the same support derived two ways: every reflex still counts once per
        # item, and counts under an item if either derivation uses it
        forms = [modern('L', 'pa'), modern('M', 'ba')]
        c1b = corr('1b', 'p', L=['p'], M=['b'])
        d1 = proto_form((self.c1, self.c2), forms)
        d2 = proto_form((c1b, self.c2), forms)
        # a RE.ProtoForm's supporting_forms is a frozenset of the same forms
        u = self._tally([d1, d2]).toc_usage['proto']
        assert u['rows'] == {'1': 2, '1b': 2, '2': 2}     # not 4 for '2'
        assert u['cells'][('2', 'L')] == 1

    def test_reflex_in_two_sets_counts_in_each(self):
        shared = modern('L', 'pa')
        s1 = proto_form((self.c1, self.c2), [shared, modern('M', 'ba')])
        s2 = proto_form((self.c1, self.c2), [shared, modern('M', 'ba', 'other')])
        u = self._tally([s1, s2]).toc_usage['proto']
        assert u['cells'][('1', 'L')] == 2 and u['cells'][('1', 'M')] == 2

    def test_fuzzy_rule_counts_per_set_not_per_derivation(self):
        fuzzied = RE.FuzzyForm('pa', modern('L', 'pʰa'))
        fuzzied.rules_fired = [('L', 'pʰ')]
        forms = [fuzzied, modern('M', 'ba')]
        d1 = proto_form((self.c1, self.c2), forms)
        d2 = proto_form((self.c1, self.c2), forms)
        stats = self._tally([d1, d2], params(fuzzy={('L', 'pʰ'): 'p'}))
        assert stats.fuzzy_usage == {('L', 'pʰ'): 1}

    def test_intermediate_levels_are_counted_against_their_own_table(self):
        d1 = corr('1', 'P', L=['x'])                  # level 'low': L -> low
        d2 = corr('1', 'Q', low=['P'])                 # level 'high': low -> high
        low = proto_form((d1,), [modern('L', 'x'), modern('L', 'x', 'h')], language='low')
        high = proto_form((d2,), [low, modern('M', 'P')], language='high')
        stats = RE.Statistics()
        RE.tally_set_usage([high], {'low': params('low'), 'high': params('high')}, stats)
        assert set(stats.toc_usage) == {'low', 'high'}
        assert stats.toc_usage['low']['rows']['1'] == 2
        assert stats.toc_usage['high']['rows']['1'] == 1 + 1


@pytest.fixture(scope='module')
def dis_run():
    """One real run of the small bundled DIS project."""
    import read
    repo_root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
    project_path = os.path.join(repo_root, 'projects', 'DIS')
    if not os.path.isdir(project_path):
        pytest.skip('DIS project not found')
    settings = read.read_settings(project_path, 'DIS', 'standard',
                                  mel_token='hand', fuzzy_token='fuzzy')
    return RE.upstream(settings, only_with_mel=True), settings


class TestTallyEndToEnd:
    """Counts from a real run (the small bundled DIS project)."""

    def test_no_alignment_failures(self, dis_run):
        B, _ = dis_run
        assert B.statistics.alignment_failures == 0

    def test_counts_match_an_independent_walk(self, dis_run):
        B, _ = dis_run
        by_set = {}
        for pf in B.forms:
            by_set.setdefault(pf.supporting_forms, []).append(pf)
        expected = 0
        for support, derivations in by_set.items():
            for reflex in {f.attested_support for f in support}:
                corrs = set()
                for pf in derivations:
                    corrs |= {c.id for c in pf.correspondences}
                expected += len(corrs)
        usage = B.statistics.toc_usage['tgtm']
        assert sum(usage['rows'].values()) == expected
        assert sum(usage['cells'].values()) == expected
        assert sum(usage['segs'].values()) >= expected

    def test_fuzzy_usage_is_only_forms_in_sets(self, dis_run):
        B, _ = dis_run
        in_sets = {f for pf in B.forms for f in pf.attested_support}
        fuzzied_in_sets = 0
        for pf in B.forms:
            for f in pf.supporting_forms:
                base = f.modern if isinstance(f, RE.Stage0Form) else f
                if isinstance(base, RE.FuzzyForm):
                    fuzzied_in_sets += len(set(base.rules_fired))
        assert sum(B.statistics.fuzzy_usage.values()) == fuzzied_in_sets
        assert in_sets   # sanity: the run produced sets


# ─────────────────────────────────────────────────────────────────────────────
# <toc_usage> in the statistics file, and REwww stamping it onto the table
# ─────────────────────────────────────────────────────────────────────────────

TOC_XML = b"""<?xml version="1.0"?>
<tableOfCorr>
  <parameters><class name="V" value="a, e"/></parameters>
  <corr num="1">
    <proto syll="CV">p</proto>
    <modern dialecte="L"><seg>p</seg><seg>ph</seg><seg>f</seg></modern>
    <modern dialecte="M"><seg>b</seg></modern>
  </corr>
  <corr num="2">
    <proto syll="V">a</proto>
    <modern dialecte="L"><seg>a</seg></modern>
    <modern dialecte="M"><seg>a</seg></modern>
  </corr>
</tableOfCorr>"""


@pytest.fixture
def usage_files(tmp_path):
    toc = tmp_path / 'X.correspondences.xml'
    toc.write_bytes(TOC_XML)
    stats = RE.Statistics()
    stats.language_stats = {}
    stats.toc_usage = {'proto': {
        'rows': {'1': 5},
        'cells': {('1', 'L'): 4, ('1', 'M'): 1},
        'segs': {('1', 'L', 0): 3, ('1', 'L', 1): 1, ('1', 'M', 0): 1}}}
    settings = types.SimpleNamespace(proto_languages={'proto': 'sub/X.correspondences.xml'})
    out = tmp_path / 'stats.xml'
    serialize.serialize_stats(stats, settings, types.SimpleNamespace(run='r', only_with_mel=True), str(out))
    return str(out), str(toc)


class TestTocUsage:
    def test_serialized_counts(self, usage_files):
        stats_path, _ = usage_files
        level = ET.parse(stats_path).getroot().find('toc_usage/level')
        assert level.get('proto') == 'proto' and level.get('file') == 'X.correspondences.xml'
        row = level.find('corr')
        assert row.get('num') == '1' and row.get('uses') == '5'
        cell = row.find("modern[@dialecte='L']")
        assert cell.get('uses') == '4'
        assert [(s.get('idx'), s.get('uses')) for s in cell.findall('seg')] == [('0', '3'), ('1', '1')]

    def test_stamped_on_table(self, usage_files):
        stats_path, toc = usage_files
        tree = xslt.compute_corr_freq(stats_path, toc)
        root = tree.getroot()
        c1, c2 = root.findall('corr')
        assert c1.get('freq') == '5'
        assert [s.get('freq') for s in c1.find("modern[@dialecte='L']").findall('seg')] == ['3', '1', '0']
        assert c1.find("modern[@dialecte='M']").get('freq') == '1'
        # never used: 0 everywhere, not missing
        assert c2.get('freq') == '0'
        assert c2.find('modern/seg').get('freq') == '0'

    def test_run_without_counts_gives_none(self, tmp_path, usage_files):
        _, toc = usage_files
        bare = tmp_path / 'old.xml'
        bare.write_bytes(b'<mel_analysis><totals/></mel_analysis>')
        assert xslt.compute_corr_freq(str(bare), toc) is None

    def test_other_table_gives_none(self, usage_files, tmp_path):
        stats_path, _ = usage_files
        other = tmp_path / 'Other.correspondences.xml'
        other.write_bytes(TOC_XML)
        assert xslt.compute_corr_freq(stats_path, str(other)) is None


class TestTocFreqRendering:
    """0 = red, 1 = light red, 2+ = gray subscript number after the value."""

    @pytest.fixture(autouse=True)
    def _styles(self, repo_root):
        xslt.STYLES_DIR = os.path.join(repo_root, 'styles')

    def html(self, usage_files):
        stats_path, toc = usage_files
        tree = xslt.compute_corr_freq(stats_path, toc)
        return xslt.xml_to_html_from_tree(tree, 'toc2html-freq.xsl')

    def cell(self, html, num, dialect_index):
        tr = ET.fromstring(html.encode(), ET.HTMLParser(encoding='utf-8')).xpath(
            f"//tr[@id='toc-corr-{num}']")[0]
        return tr.xpath('td')[6 + dialect_index]

    def test_no_error(self, usage_files):
        assert 'text-danger' not in self.html(usage_files)

    def test_two_or_more_is_a_gray_subscript(self, usage_files):
        c = self.cell(self.html(usage_files), 1, 0)       # L: p=3, ph=1, f=0
        spans = c.xpath('span')
        assert [s.text for s in spans] == ['p', 'ph', 'f']
        subs = c.xpath('sub[@class="cov-uses"]')
        assert [s.text.strip() for s in subs] == ['3']

    def test_zero_is_red_and_one_is_light_red_without_numbers(self, usage_files):
        c = self.cell(self.html(usage_files), 1, 0)
        p, ph, f = c.xpath('span')
        assert 'background-color' not in p.get('style')
        assert '#f8d7da' in ph.get('style')
        assert '#dc3545' in f.get('style')
        assert len(c.xpath('sub')) == 1                    # only p's "3"

    def test_every_zero_cell_is_red(self, usage_files):
        c = self.cell(self.html(usage_files), 2, 0)
        assert '#dc3545' in c.xpath('span')[0].get('style')
        assert not c.xpath('sub')

    def test_class_members_use_the_same_convention(self, usage_files):
        html = self.html(usage_files)
        t = ET.fromstring(html.encode(), ET.HTMLParser(encoding='utf-8'))
        cls = t.xpath("//table[contains(@class,'toc-classes-table')]//td")
        spans = [s for td in cls for s in td.xpath('.//span')]
        assert [s.text for s in spans] == ['a', 'e']
        # 'a' appears as the proto of row 2 only (0 uses): red; 'e' nowhere: red
        assert all('#dc3545' in s.get('style') for s in spans)


# ─────────────────────────────────────────────────────────────────────────────
# Coverage: counts are reflexes in cognate sets only
# ─────────────────────────────────────────────────────────────────────────────

class TestCoverageCountsOnlySets:
    def build(self):
        m1 = mel_module.Mel(['rice', 'cooked rice'], 'm1')
        m2 = mel_module.Mel(['bone'], 'm2')
        in_set1, in_set2 = modern('L', 'pa', 'rice'), modern('M', 'ba', 'cooked rice')
        isolate = modern('L', 'zz', 'rice')               # an isolate: must not count
        failure = modern('M', 'qq', 'bone')               # a failure: must not count
        glosses = {f.gloss for f in (in_set1, in_set2, isolate, failure)}
        table = mel_module.compile_associated_mels([m1, m2], glosses)
        pf = proto_form((), [in_set1, in_set2], mel=m1)
        iso_pf = proto_form((), [isolate], mel=m1)
        root = types.SimpleNamespace(forms=[pf], isolates_dict={isolate: [iso_pf]},
                                     failures=[failure])
        lexicons = {'L': types.SimpleNamespace(forms=[in_set1, isolate]),
                    'M': types.SimpleNamespace(forms=[in_set2, failure])}
        return [m1, m2], lexicons, table, root

    def test_usage_counts_only_reflexes_in_sets(self):
        mels, lexicons, table, root = self.build()
        stats = coverage.build_coverage_statistics(mels, lexicons, table, ['L', 'M'], root)
        # Matching is symmetric: the reflex 'rice' matches the synonym 'cooked rice'
        # (whose normalized words include 'rice') and the reflex 'cooked rice'
        # matches the synonym 'rice', so each in-set reflex counts under both
        # synonyms. The isolate's 'rice' does not count at all.
        assert stats.mel_usage['m1']['rice'] == 2
        assert stats.mel_usage['m1']['cooked rice'] == 2
        assert stats.mel_usage['m2']['bone'] == 0          # only a failure matched it
        assert stats.mel_usage['m2']['usage'] is False
        assert stats.summary_stats['unused_mels'] == 1
        assert stats.summary_stats['unused_mel_glosses'] == 1
        assert stats.language_stats['L']['forms'] == 1
        assert stats.language_stats['M']['forms'] == 1

    def test_reflex_in_two_sets_counts_once_per_mel_but_under_each_mel(self):
        m1 = mel_module.Mel(['rice'], 'm1')
        m2 = mel_module.Mel(['rice', 'grain'], 'm2')
        f1, f2 = modern('L', 'pa', 'rice'), modern('M', 'ba', 'rice')
        table = mel_module.compile_associated_mels([m1, m2], {'rice'})
        root = types.SimpleNamespace(
            forms=[proto_form((), [f1, f2], mel=m1), proto_form((), [f1, f2], mel=m2),
                   proto_form((), [f1, f2], mel=m2)],     # a second derivation of m2's set
            isolates_dict={}, failures=[])
        stats = coverage.build_annotated_coverage([m1, m2], table, ['L', 'M'], root)
        assert stats.synonym_usage[('m1', 'rice')] == 2
        assert stats.synonym_usage[('m2', 'rice')] == 2    # not 4: derivations don't multiply

    def test_reflex_in_two_different_sets_of_one_mel_counts_twice(self):
        m1 = mel_module.Mel(['rice'], 'm1')
        shared = modern('L', 'pa', 'rice')
        table = mel_module.compile_associated_mels([m1], {'rice'})
        root = types.SimpleNamespace(
            forms=[proto_form((), [shared, modern('M', 'ba', 'rice')], mel=m1),
                   proto_form((), [shared, modern('M', 'bo', 'rice')], mel=m1)],
            isolates_dict={}, failures=[])
        stats = coverage.build_annotated_coverage([m1], table, ['L', 'M'], root)
        assert stats.synonym_usage[('m1', 'rice')] == 4    # shared (once in each set) + each set's own M reflex


# ─────────────────────────────────────────────────────────────────────────────
# MEL pane: counts over the lexicons as a whole, and the KWIC view
# ─────────────────────────────────────────────────────────────────────────────

class TestMelPane:
    @pytest.fixture(autouse=True)
    def _styles(self, repo_root):
        xslt.STYLES_DIR = os.path.join(repo_root, 'styles')

    def mel_lexicon(self, tmp_path):
        m1 = mel_module.Mel(['give up the ship', 'abandon', '(plural)'], 'm1')
        lexicons = {
            'L': RE.Lexicon('L', [modern('L', 'aa', 'abandon'), modern('L', 'ab', 'abandon'),
                                  modern('L', 'ac', 'give up the ship')]),
            'M': RE.Lexicon('M', [modern('M', 'ba', 'abandon')])}
        glosses = {f.gloss for lx in lexicons.values() for f in lx.forms}
        table = mel_module.compile_associated_mels([m1], glosses)
        out = tmp_path / 'mel_lexicon.xml'
        serialize.serialize_mel_lexicon_annotated([m1], lexicons, table, ['L', 'M'], 'x.mel.xml', str(out))
        return str(out)

    def test_counts_are_lexicon_entries_not_sets(self, tmp_path):
        root = ET.parse(self.mel_lexicon(tmp_path)).getroot()
        uses = {g.text: g.get('uses') for g in root.findall('semantics/mel/gl')}
        assert uses == {'give up the ship': '1', 'abandon': '3', '(plural)': '0'}

    def test_normalized_keys_are_written(self, tmp_path):
        root = ET.parse(self.mel_lexicon(tmp_path)).getroot()
        norms = root.findall('semantics/mel/norm')
        assert len(norms) == 3
        assert [k.text for k in norms[0].findall('k')][:2] == ['give up the ship', 'give up']
        assert norms[2].findall('k') == []                  # bracketed annotation: nothing left

    def kwic_rows(self, html):
        t = ET.fromstring(html.encode(), ET.HTMLParser(encoding='utf-8'))
        return t, t.xpath("//table[contains(@class,'kwic-table')]/tbody/tr")

    def test_kwic_button_and_table(self, tmp_path):
        html = xslt.xml_to_html(self.mel_lexicon(tmp_path), 'coverage2html.xsl')
        assert 'text-danger' not in html
        t, rows = self.kwic_rows(html)
        assert t.xpath("//button[@id='btn-toggle-kwic']")[0].text == 'KWIC'
        assert len(rows) == 3                               # one row per MEL gloss
        head = [th.text for th in t.xpath("//table[contains(@class,'kwic-table')]/thead/th")
                or t.xpath("//table[contains(@class,'kwic-table')]//th")]
        assert head == ['MEL', 'Left context', 'Gloss (normalized)', 'Right context']

    def test_kwic_row_contents_and_hovers(self, tmp_path):
        _, rows = self.kwic_rows(xslt.xml_to_html(self.mel_lexicon(tmp_path), 'coverage2html.xsl'))
        first, second, third = rows
        # row 1: centre = one pill per normalized key
        pills = first.xpath("td[@class='kwic-center']/span[@class='kwic-pill']")
        assert [p.text for p in pills][:2] == ['give up the ship', 'give up']
        # the key identical to the literal gloss has no hover and is not bold ...
        assert pills[0].get('title') is None
        assert 'font-weight:bold' not in pills[0].get('style')
        # ... the others differ from it: bold, hover = the literal gloss
        assert pills[1].get('title') == 'give up the ship'
        assert 'font-weight:bold' in pills[1].get('style')
        assert first.xpath("td[@class='kwic-center']")[0].get('title') is None
        assert ''.join(first.xpath("td[@class='kwic-left']")[0].itertext()).strip() == ''
        # right context: literal glosses. 'abandon' normalizes to itself: plain, no hover
        right = first.xpath("td[@class='kwic-right']/span[@class='kwic-gl']")
        assert [r.text for r in right] == ['abandon', '(plural)']
        assert right[0].get('title') is None and right[0].get('style') is None
        # row 2: left = the preceding gloss; its keys differ from it: bold + hover
        left = second.xpath("td[@class='kwic-left']/span")
        assert [s.text for s in left] == ['give up the ship']
        assert left[0].get('title').startswith('give up the ship | give up')
        assert 'font-weight:bold' in left[0].get('style')
        assert [s.text for s in second.xpath("td[@class='kwic-right']/span")] == ['(plural)']
        # '(plural)' has no normalized keys at all: nothing to show on hover, so plain
        assert second.xpath("td[@class='kwic-right']/span")[0].get('title') is None
        # row 3: nothing normalized survives, so the literal gloss is shown (muted)
        raw = third.xpath("td[@class='kwic-center']/span[@class='kwic-pill kwic-pill-raw']")
        assert [r.text for r in raw] == ['(plural)']
        assert raw[0].get('title') is None

    def test_no_kwic_without_normalized_glosses(self, tmp_path):
        path = self.mel_lexicon(tmp_path)
        tree = ET.parse(path)
        for n in tree.getroot().xpath('//norm'):
            n.getparent().remove(n)
        tree.write(path)
        html = xslt.xml_to_html(path, 'coverage2html.xsl')
        assert 'btn-toggle-kwic' not in html and 'kwic-table' not in html

    def test_coverage_report_has_no_kwic(self, tmp_path):
        xml = b"""<mel_analysis><languages><lg>L</lg></languages><semantics>
            <mel id="m1"><gl uses="1">a</gl><norm><k>a</k></norm>
            <reconstruction status="set">x</reconstruction></mel></semantics></mel_analysis>"""
        tree = ET.ElementTree(ET.fromstring(xml))
        html = xslt.xml_to_html_from_tree(tree, 'coverage2html.xsl')
        assert 'btn-toggle-kwic' not in html and 'kwic-table' not in html


# ─────────────────────────────────────────────────────────────────────────────
# pick_derivation: which MEL a set is credited to must not depend on input order
# ─────────────────────────────────────────────────────────────────────────────

class TestPickDerivationIsDeterministic:
    def test_same_support_under_two_mels_goes_to_the_lowest_id(self):
        c = corr('1', 'p', L=['p'], M=['b'])
        forms = [modern('L', 'p'), modern('M', 'b')]
        support = frozenset(forms)
        attested = frozenset().union(*(f.attested_support for f in forms))
        m_a, m_b = mel_module.Mel(['x'], 'm1'), mel_module.Mel(['y'], 'm2')
        sets = [((c,), support, attested, m_b), ((c,), support, attested, m_a)]
        for ordering in (sets, list(reversed(sets))):
            picked, _ = RE.pick_derivation(ordering, RE.Statistics(), True)
            picked = list(picked)
            assert len(picked) == 1 and picked[0][3] is m_a
