"""Tests for the core RE engine modules (src/RE.py, src/read.py, src/serialize.py).

These tests import the Python modules directly without going through REcli or
the Flask front-end, so they run quickly and don't require a display.
"""

import os
import sys
import pytest


# conftest.py already inserted src/ at the front of sys.path.


# ─────────────────────────────────────────────────────────────────────────────
# Import sanity
# ─────────────────────────────────────────────────────────────────────────────

class TestImports:
    def test_re_importable(self):
        import RE  # noqa: F401

    def test_read_importable(self):
        import read  # noqa: F401

    def test_serialize_importable(self):
        import serialize  # noqa: F401

    def test_mel_importable(self):
        import mel  # noqa: F401

    def test_projects_importable(self):
        import projects  # noqa: F401


# ─────────────────────────────────────────────────────────────────────────────
# parse_spec_value — codepoint / literal detection
# ─────────────────────────────────────────────────────────────────────────────

class TestParseSpecValue:
    """Unit tests for read.parse_spec_value."""

    @pytest.fixture(autouse=True)
    def _import(self):
        import read as _read
        self._parse = _read.parse_spec_value

    # ── codepoint mode ────────────────────────────────────────────────────────

    def test_single_codepoint(self):
        """U+0303 → COMBINING TILDE (U+0303)."""
        result = self._parse('U+0303')
        assert result == ['̃']

    def test_single_codepoint_lowercase(self):
        result = self._parse('u+0303')
        assert result == ['̃']

    def test_two_codepoints_comma_separated(self):
        result = self._parse('U+0303, U+0308')
        assert result == ['̃', '̈']

    def test_two_codepoints_space_separated(self):
        result = self._parse('U+0303 U+0308')
        assert result == ['̃', '̈']

    def test_six_hex_digit_codepoint(self):
        """Six-digit hex codepoints (supplementary plane) are accepted."""
        result = self._parse('U+1F600')
        assert result == ['\U0001F600']

    def test_codepoint_with_surrounding_whitespace(self):
        result = self._parse('  U+0303  ')
        assert result == ['̃']

    # ── literal mode ──────────────────────────────────────────────────────────

    def test_literal_single_char(self):
        result = self._parse('ˈ')
        assert result == ['ˈ']

    def test_literal_comma_separated(self):
        result = self._parse('ˊ,ˋ')
        assert result == ['ˊ', 'ˋ']

    def test_literal_with_spaces_around_comma(self):
        result = self._parse('ˊ, ˋ')
        assert result == ['ˊ', 'ˋ']

    def test_literal_mixed_latin_unicode(self):
        """A literal string that contains 'U' but not in U+XXXX format stays literal."""
        result = self._parse('Up,Down')
        assert result == ['Up', 'Down']

    # ── edge cases ────────────────────────────────────────────────────────────

    def test_empty_string_returns_empty(self):
        assert self._parse('') == []

    def test_whitespace_only_returns_empty(self):
        assert self._parse('   ') == []

    def test_trailing_comma_ignored(self):
        """A trailing comma after the last item produces no empty entry."""
        result = self._parse('ˊ,ˋ,')
        assert '' not in result
        assert result == ['ˊ', 'ˋ']

    # ── round-trip via read_syllable_canon ────────────────────────────────────

    def test_codepoint_spec_in_syllable_canon(self):
        """U+0303 stored in XML is converted to the actual combining tilde."""
        import read as _read
        import xml.etree.ElementTree as ET
        params = ET.fromstring(
            '<parameters>'
            '  <canon value="CV"/>'
            '  <spec value="U+0303"/>'
            '</parameters>')
        sc = _read.read_syllable_canon(params)
        assert sc.supra_segmentals == ['̃']

    def test_literal_spec_in_syllable_canon(self):
        """A literal supra-segmental string is preserved as-is."""
        import read as _read
        import xml.etree.ElementTree as ET
        params = ET.fromstring(
            '<parameters>'
            '  <canon value="CV"/>'
            '  <spec value="ˊ,ˋ"/>'
            '</parameters>')
        sc = _read.read_syllable_canon(params)
        assert 'ˊ' in sc.supra_segmentals
        assert 'ˋ' in sc.supra_segmentals

    # ── raw_spec roundtrip ────────────────────────────────────────────────────

    def test_codepoint_raw_spec_preserved(self):
        """raw_spec on SyllableCanon matches the verbatim XML attribute value."""
        import read as _read
        import xml.etree.ElementTree as ET
        params = ET.fromstring(
            '<parameters>'
            '  <canon value="CV"/>'
            '  <spec value="U+0303"/>'
            '</parameters>')
        sc = _read.read_syllable_canon(params)
        assert sc.raw_spec == 'U+0303'

    def test_literal_raw_spec_preserved(self):
        import read as _read
        import xml.etree.ElementTree as ET
        params = ET.fromstring(
            '<parameters>'
            '  <canon value="CV"/>'
            '  <spec value="ˈ"/>'
            '</parameters>')
        sc = _read.read_syllable_canon(params)
        assert sc.raw_spec == 'ˈ'

    def test_spec_for_storage_returns_raw_spec(self):
        """spec_for_storage returns raw_spec verbatim — even for a printable
        codepoint like U+02C8 that spec_display would collapse to the literal ˈ."""
        import read as _read
        from utils import spec_for_storage
        import xml.etree.ElementTree as ET
        params = ET.fromstring(
            '<parameters>'
            '  <canon value="CV"/>'
            '  <spec value="U+02C8"/>'
            '</parameters>')
        sc = _read.read_syllable_canon(params)
        # supra_segmentals has the actual char ˈ
        assert sc.supra_segmentals == ['ˈ']
        # but spec_for_storage gives back the original codepoint string
        assert spec_for_storage(sc) == 'U+02C8'

    def test_spec_for_storage_fallback_when_no_raw_spec(self):
        """spec_for_storage falls back to spec_display when raw_spec is None."""
        import RE as _RE
        from utils import spec_for_storage, spec_display
        sc = _RE.SyllableCanon({}, 'CV', ['ˈ'], 'constituent')
        assert sc.raw_spec is None
        assert spec_for_storage(sc) == spec_display(['ˈ'])


# ─────────────────────────────────────────────────────────────────────────────
# SyllableCanon defaults
# ─────────────────────────────────────────────────────────────────────────────

class TestSyllableCanon:
    """Test SyllableCanon construction via read_syllable_canon (the normal path)."""

    @pytest.fixture(autouse=True)
    def _import(self):
        import read as _read
        import xml.etree.ElementTree as ET
        self._read = _read
        self._ET   = ET

    def _params_el(self, xml_str):
        """Parse a <parameters>…</parameters> fragment and return the Element."""
        return self._ET.fromstring(xml_str)

    def test_default_context_match_type(self):
        """context_match_type defaults to 'constituent' when absent from XML."""
        params = self._params_el('<parameters><canon value="CV"/></parameters>')
        sc = self._read.read_syllable_canon(params)
        assert sc.context_match_type == 'constituent'

    def test_explicit_glyphs(self):
        params = self._params_el(
            '<parameters>'
            '  <canon value="CV"/>'
            '  <context_match_type value="glyphs"/>'
            '</parameters>')
        sc = self._read.read_syllable_canon(params)
        assert sc.context_match_type == 'glyphs'

    def test_supra_segmentals_parsed(self):
        params = self._params_el(
            '<parameters>'
            '  <canon value="CV"/>'
            '  <spec value="ˊ,ˋ"/>'
            '</parameters>')
        sc = self._read.read_syllable_canon(params)
        assert 'ˊ' in sc.supra_segmentals

    def test_default_supra_segmentals(self):
        params = self._params_el('<parameters><canon value="CV"/></parameters>')
        sc = self._read.read_syllable_canon(params)
        assert sc.supra_segmentals == []

    def test_fields_present(self):
        """SyllableCanon has the expected attributes."""
        params = self._params_el('<parameters><canon value="(C)V(C)"/></parameters>')
        sc = self._read.read_syllable_canon(params)
        assert hasattr(sc, 'context_match_type')
        assert hasattr(sc, 'supra_segmentals')
        assert hasattr(sc, 'regex')


# ─────────────────────────────────────────────────────────────────────────────
# read.read_correspondences on a real project file
# ─────────────────────────────────────────────────────────────────────────────

class TestReadCorrespondences:
    """Test loading a real correspondences file via read_correspondence_file.

    Returns a RE.Parameters object with .syllable_canon and .table attributes.
    """

    @pytest.fixture(autouse=True)
    def _setup(self, repo_root):
        self.corr_path = os.path.join(
            repo_root, 'projects', 'DIS', 'DIS.standard.correspondences.xml')
        if not os.path.isfile(self.corr_path):
            pytest.skip('DIS standard correspondences file not found')
        import read
        self._read = read

    def _load(self):
        return self._read.read_correspondence_file(
            self.corr_path, 'DIS', None, None)

    def test_reads_without_error(self):
        params = self._load()
        assert params is not None

    def test_syllable_canon_has_context_match_type(self):
        params = self._load()
        assert params.syllable_canon.context_match_type in ('constituent', 'glyphs')

    def test_table_has_correspondences(self):
        params = self._load()
        assert len(params.table.correspondences) > 0

    def test_each_correspondence_has_id(self):
        params = self._load()
        for c in params.table.correspondences[:5]:   # spot-check first five
            assert hasattr(c, 'id') and c.id is not None


# ─────────────────────────────────────────────────────────────────────────────
# partition_correspondences — unit tests with synthetic data
# ─────────────────────────────────────────────────────────────────────────────

class TestPartitionCorrespondences:
    """White-box tests for RE.partition_correspondences.

    partition_correspondences(correspondences, accessor, fuzzy_mapping=None)
    returns (partitions_dict, token_lengths_list).

    accessor is a callable that takes a Correspondence and returns an iterable
    of string tokens (the daughter forms for that correspondence).
    """

    @pytest.fixture(autouse=True)
    def _import(self):
        import RE as _RE
        self._RE = _RE

    def test_empty_correspondences_returns_empty_partitions(self):
        """No correspondences → empty partitions dict and empty lengths list."""
        partitions, lengths = self._RE.partition_correspondences(
            [], lambda c: [], None)
        assert dict(partitions) == {}
        assert lengths == []

    def test_returns_tuple(self):
        partitions, lengths = self._RE.partition_correspondences(
            [], lambda c: [], None)
        assert hasattr(partitions, '__getitem__')
        assert isinstance(lengths, list)

    def test_single_token_accessor(self):
        """A correspondence with a single known token is correctly partitioned."""
        from types import SimpleNamespace
        fake_corr = SimpleNamespace(id='1')
        # Accessor always returns ['a'] for any correspondence
        partitions, lengths = self._RE.partition_correspondences(
            [fake_corr], lambda c: ['a'], None)
        assert 'a' in partitions
        assert fake_corr in partitions['a']
        assert 1 in lengths   # length of 'a' is 1

    def test_empty_token_is_ignored(self):
        """The empty string token is not added to the partition."""
        from types import SimpleNamespace
        fake_corr = SimpleNamespace(id='2')
        partitions, lengths = self._RE.partition_correspondences(
            [fake_corr], lambda c: [''], None)
        assert '' not in partitions


# ─────────────────────────────────────────────────────────────────────────────
# MEL homophone filtering in create_sets
# ─────────────────────────────────────────────────────────────────────────────

class TestMelHomophoneFiltering:
    """Verify that unmatched forms are added to a MEL group only when they are
    genuine homophones (same pre-fuzzy surface form) of a matched form in the
    same language — not merely forms that coincide after fuzzying.

    Two concrete cases:
      • True homophones (same surface form, different gloss) SHOULD appear.
      • Fuzz-coincident forms (different surface form, same fuzzied form) should NOT.
    """

    @pytest.fixture(autouse=True)
    def _import(self):
        import RE as _RE
        self._RE = _RE

    def _make_modern(self, language, glyphs, gloss):
        return self._RE.ModernForm(language, glyphs, gloss, id=f'{language}-{gloss}')

    def _make_fuzzy(self, fuzzied_glyphs, actual_modern):
        return self._RE.FuzzyForm(fuzzied_glyphs, actual_modern)

    def _run_create_sets(self, support_forms, mels_list, only_with_mel=True):
        """Minimal wrapper: build a projections dict with one reconstruction.

        Returns (cognate_sets, statistics) — the raw tuple from create_sets.
        mels_list is a list of mel.Mel objects (the real type used in production).
        """
        reconstruction = 'test-rcn'
        projections = {reconstruction: tuple(support_forms)}
        stats = self._RE.Statistics()
        # create_sets returns (set_of_tuples, statistics)
        return self._RE.create_sets(projections, stats, mels_list, only_with_mel)

    def _mel(self, glosses, id_str):
        """Build a real mel.Mel object."""
        import mel as mel_module
        return mel_module.Mel(glosses, id_str)

    def _forms_in_sets(self, result):
        """Flatten all supporting forms from create_sets output."""
        cognate_sets, _stats = result
        all_forms = set()
        for entry in cognate_sets:
            # each entry is (reconstruction, frozen_support, attested_support, mel)
            frozen_support = entry[1]
            all_forms |= frozen_support
        return all_forms

    def test_true_homophones_both_appear(self):
        """Two ModernForms with the SAME glyphs in the same language both
        appear in the MEL group, even if only one gloss matches the MEL."""
        # 'tag' has two identical-sounding entries: 'Xs' "to know" and 'Xs' "to repeat"
        tag_know   = self._make_modern('tag',   'Xs', 'to know')
        tag_repeat = self._make_modern('tag',   'Xs', 'to repeat')
        lang2_form = self._make_modern('lang2', 'xs', 'to know')

        # One MEL that covers "to know"; "to repeat" has no MEL match.
        mels = [self._mel(['to know'], 'mel-know')]
        sets = self._run_create_sets((tag_know, tag_repeat, lang2_form), mels)

        all_forms = self._forms_in_sets(sets)
        assert tag_know   in all_forms, '"to know" should appear in a set'
        assert tag_repeat in all_forms, \
            'True homophone "to repeat" should appear alongside "to know"'

    def test_fuzzy_coincident_forms_excluded(self):
        """Two FuzzyForms with DIFFERENT pre-fuzzy glyphs that normalise to the
        same string are NOT both pulled into the MEL group."""
        # 'mar' has two tonal variants that fuzzy to the same string '˥ɲi':
        #   ⁵⁴⁵ɲi "deux" — matches MEL 355
        #   ⁵¹ɲi  "nous" — no MEL match; different pre-fuzzy form
        mar_deux_actual = self._make_modern('mar', '⁵⁴⁵ɲi', 'deux')
        mar_nous_actual = self._make_modern('mar', '⁵¹ɲi',  'nous')
        mar_deux = self._make_fuzzy('˥ɲi', mar_deux_actual)
        mar_nous = self._make_fuzzy('˥ɲi', mar_nous_actual)
        lang2_form = self._make_modern('lang2', 'two', 'deux')

        mels = [self._mel(['deux'], 'mel-355')]
        sets = self._run_create_sets((mar_deux, mar_nous, lang2_form), mels)

        all_forms = self._forms_in_sets(sets)
        assert mar_deux in all_forms, '"deux" should appear in the mel-355 set'
        assert mar_nous not in all_forms, \
            'Fuzz-coincident "nous" should NOT appear in the mel-355 set'


# ─────────────────────────────────────────────────────────────────────────────
# projects module
# ─────────────────────────────────────────────────────────────────────────────

class TestProjects:
    @pytest.fixture(autouse=True)
    def _import(self):
        import projects
        self._proj = projects

    def test_get_dirs_returns_dict(self):
        d = self._proj.get_dirs()
        assert isinstance(d, dict)

    def test_dis_in_projects(self):
        d = self._proj.get_dirs()
        assert 'DIS' in d, f'DIS not found in projects: {list(d)}'

    def test_dis_path_is_directory(self):
        d = self._proj.get_dirs()
        assert os.path.isdir(d['DIS']), f"DIS path {d['DIS']!r} is not a directory"

    def test_polynesian_in_projects(self):
        d = self._proj.get_dirs()
        assert 'POLYNESIAN' in d
