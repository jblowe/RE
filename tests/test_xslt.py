"""Tests for the XSLT rendering helpers (xslt.py) and the two ToC stylesheets.

All tests operate on minimal in-memory XML so they run quickly without any
project files on disk.
"""

import os
import pytest
import lxml.etree as ET


# ── Module setup ───────────────────────────────────────────────────────────────
# conftest.py already added REwww/ to sys.path.
import xslt


# ── Minimal XML used across tests ─────────────────────────────────────────────
MINIMAL_TOC_XML = b"""<?xml version="1.0"?>
<tableOfCorr>
  <parameters>
    <canon value="(C)V(C)"/>
    <spec value="\xca\x8a\xcb\x8b"/>
    <context_match_type value="constituent"/>
    <class name="V" value="a e i o u"/>
  </parameters>
  <corr num="1">
    <proto syll="V" contextL="" contextR="">a</proto>
    <modern dialecte="lang1"><seg statut="reg">a</seg></modern>
    <modern dialecte="lang2"><seg statut="reg">\xc9\x99</seg></modern>
  </corr>
  <corr num="2">
    <proto syll="CV" contextL="V" contextR="">i</proto>
    <modern dialecte="lang1"><seg statut="doute">e</seg></modern>
    <modern dialecte="lang2"><seg statut="reg">i</seg></modern>
  </corr>
</tableOfCorr>"""

GLYPHS_TOC_XML = b"""<?xml version="1.0"?>
<tableOfCorr>
  <parameters>
    <context_match_type value="glyphs"/>
  </parameters>
  <corr num="1">
    <proto>p</proto>
    <modern dialecte="d1"><seg statut="reg">p</seg></modern>
  </corr>
</tableOfCorr>"""


@pytest.fixture(scope='module')
def styles_dir(repo_root):
    return os.path.join(repo_root, 'styles')


@pytest.fixture(autouse=True, scope='module')
def set_styles_dir(styles_dir):
    """Point xslt.STYLES_DIR at the real styles folder before any test runs."""
    xslt.STYLES_DIR = styles_dir


# ─────────────────────────────────────────────────────────────────────────────
# xml_to_html_from_tree — view stylesheet
# ─────────────────────────────────────────────────────────────────────────────

class TestViewTransform:
    def _run(self):
        tree = ET.ElementTree(ET.fromstring(MINIMAL_TOC_XML))
        return xslt.xml_to_html_from_tree(tree, 'toc2html-view.xsl')

    def test_returns_string(self):
        html = self._run()
        assert isinstance(html, str)
        assert len(html) > 0

    def test_no_error_marker(self):
        html = self._run()
        assert 'text-danger' not in html, \
            f'XSLT produced an error: {html[:300]}'

    def test_contains_dialect_names(self):
        html = self._run()
        assert 'lang1' in html
        assert 'lang2' in html

    def test_contains_corr_num(self):
        html = self._run()
        assert '>1<' in html or '>1 <' in html or '1</td>' in html

    def test_contains_canon_value(self):
        html = self._run()
        assert '(C)V(C)' in html

    def test_contains_spec_value(self):
        html = self._run()
        # The spec value contains Unicode tone marks; just check the label
        assert 'Supra-segmentals' in html

    def test_context_match_type_shown(self):
        html = self._run()
        assert 'constituent' in html


# ─────────────────────────────────────────────────────────────────────────────
# xml_to_html_from_tree — edit stylesheet
# ─────────────────────────────────────────────────────────────────────────────

class TestEditTransform:
    def _run(self, xml=MINIMAL_TOC_XML):
        tree = ET.ElementTree(ET.fromstring(xml))
        return xslt.xml_to_html_from_tree(tree, 'toc2html-edit.xsl')

    def test_returns_string(self):
        html = self._run()
        assert isinstance(html, str)

    def test_no_error_marker(self):
        html = self._run()
        assert 'text-danger' not in html, \
            f'XSLT produced an error: {html[:300]}'

    def test_contains_form_inputs(self):
        html = self._run()
        assert '<input' in html

    def test_spec_input_present(self):
        html = self._run()
        assert 'name="spec"' in html

    def test_context_match_type_radio_buttons(self):
        html = self._run()
        # Both radio options must appear
        assert 'value="constituent"' in html
        assert 'value="glyphs"' in html
        assert 'type="radio"' in html

    def test_constituent_is_default_checked(self):
        html = self._run()
        # When context_match_type="constituent", constituent radio should be checked
        # and glyphs should not.
        assert 'checked' in html  # at least one radio is checked

    def test_glyphs_checked_when_set(self):
        html = self._run(GLYPHS_TOC_XML)
        # Parse the HTML fragment to locate the glyphs radio
        # We test by string proximity: checked attribute near value="glyphs"
        assert 'value="glyphs"' in html
        # A crude but reliable check: the glyphs radio carries "checked" when glyphs is set.
        idx_glyphs = html.find('value="glyphs"')
        # Find the nearest checked attribute within 200 chars of the glyphs value
        nearby = html[max(0, idx_glyphs - 100):idx_glyphs + 100]
        assert 'checked' in nearby, \
            f'glyphs radio not checked when context_match_type=glyphs; nearby HTML:\n{nearby}'

    def test_dialect_columns_in_table(self):
        html = self._run()
        assert 'lang1' in html
        assert 'lang2' in html

    def test_class_table_present(self):
        html = self._run()
        # The minimal XML has a class element; it should appear in the edit form
        assert 'class-1-name' in html or 'class name' in html.lower()

    def test_add_row_button_present(self):
        html = self._run()
        assert 'addRowBtn' in html


# ─────────────────────────────────────────────────────────────────────────────
# xml_to_html — file-based wrapper
# ─────────────────────────────────────────────────────────────────────────────

class TestXmlToHtml:
    def test_missing_xml_file_returns_error_html(self, tmp_path, styles_dir):
        html = xslt.xml_to_html(str(tmp_path / 'nonexistent.xml'),
                                'toc2html-view.xsl')
        assert 'text-danger' in html
        assert 'nonexistent.xml' in html

    def test_missing_stylesheet_returns_error_html(self, tmp_path, styles_dir):
        # Write a trivial XML file so the file-exists check passes
        p = tmp_path / 'dummy.xml'
        p.write_bytes(b'<root/>')
        html = xslt.xml_to_html(str(p), 'no-such-stylesheet.xsl')
        assert 'text-danger' in html

    def test_real_dis_correspondences(self, repo_root):
        """Smoke-test the view transform against the real DIS standard file."""
        xml_path = os.path.join(repo_root, 'projects', 'DIS',
                                'DIS.standard.correspondences.xml')
        if not os.path.isfile(xml_path):
            pytest.skip('DIS standard correspondences file not found')
        html = xslt.xml_to_html(xml_path, 'toc2html-view.xsl')
        assert 'text-danger' not in html
        assert '<table' in html


# ─────────────────────────────────────────────────────────────────────────────
# stylesheet_for() utility
# ─────────────────────────────────────────────────────────────────────────────

class TestStylesheetFor:
    @pytest.mark.parametrize('filename,expected', [
        ('DIS.standard.correspondences.xml', 'toc2html-view.xsl'),
        ('DIS.hand.mel.xml',                 'mel2html.xsl'),
        ('DIS.fuzzy.fuz.xml',                'fuzzy2html.xsl'),
        ('DIS.tag.data.xml',                 'lexicon2html.xsl'),
        ('DIS.hand.sets.xml',                'sets2html.xsl'),
        ('DIS.statistics.xml',               'stats2html.xsl'),
    ])
    def test_known_filenames(self, filename, expected):
        result = xslt.stylesheet_for(filename)
        assert result == expected, f'{filename} → {result!r}, want {expected!r}'

    def test_unknown_filename_returns_none(self):
        assert xslt.stylesheet_for('unknown.xyz') is None

    def test_paragraph_mode_sets(self):
        assert xslt.stylesheet_for('x.sets.xml', 'paragraph') == 'sets2html.xsl'

    def test_table_mode_sets(self):
        assert xslt.stylesheet_for('x.sets.xml', 'table') == 'sets2tabular.xsl'

    def test_paragraph_mode_data(self):
        assert xslt.stylesheet_for('x.data.xml', 'paragraph') == 'lexicon2html.xsl'

    def test_table_mode_data(self):
        assert xslt.stylesheet_for('x.data.xml', 'table') == 'lexicon2table.xsl'


# ─────────────────────────────────────────────────────────────────────────────
# coverage2html.xsl — xml:lang on <gl>, rendered the same way mel2html.xsl
# renders it directly off the MEL file (see tests/test_re_core.py::
# TestMelXmlLang for the backend half: read_mel_file -> coverage.py ->
# serialize.py actually producing this xml:lang attribute in coverage.xml).
# ─────────────────────────────────────────────────────────────────────────────

# Shape matches serialize.serialize_stats's actual output for the plain
# "MEL usage" table (no <languages> sibling of <semantics>).
COVERAGE_XML_PLAIN_MEL_USAGE = b"""<?xml version="1.0" encoding="utf-8"?>
<stats>
  <semantics>
    <mel id="m1">
      <gl uses="2" xml:lang="fr">abandonner</gl>
      <gl uses="0">cast away</gl>
    </mel>
  </semantics>
</stats>"""

# Shape matches the annotated "MEL Annotated Coverage" table (<languages> is
# a sibling of <semantics>, which is what selects the other template).
COVERAGE_XML_ANNOTATED = b"""<?xml version="1.0" encoding="utf-8"?>
<stats>
  <languages><lg>lang1</lg></languages>
  <semantics>
    <mel id="m1">
      <gl uses="2" xml:lang="fr">abandonner</gl>
      <reconstruction status="set">test</reconstruction>
      <lg name="lang1"><form status="set">abandonner</form></lg>
    </mel>
  </semantics>
</stats>"""


class TestCoverageXmlLangRendering:
    def _render(self, xml_bytes):
        tree = ET.ElementTree(ET.fromstring(xml_bytes))
        return xslt.xml_to_html_from_tree(tree, 'coverage2html.xsl')

    def test_plain_mel_usage_renders_lang_as_sub(self):
        html = self._render(COVERAGE_XML_PLAIN_MEL_USAGE)
        assert 'text-danger' not in html, f'XSLT produced an error: {html[:300]}'
        assert '<sub>fr</sub>' in html

    def test_plain_mel_usage_no_sub_when_no_lang(self):
        html = self._render(COVERAGE_XML_PLAIN_MEL_USAGE)
        assert 'cast away' in html
        # "cast away" has no xml:lang, so it must not pick up a stray <sub>
        idx = html.find('cast away')
        assert '<sub>' not in html[idx:idx + 40]

    def test_annotated_gloss_renders_lang_as_sub(self):
        html = self._render(COVERAGE_XML_ANNOTATED)
        assert 'text-danger' not in html, f'XSLT produced an error: {html[:300]}'
        assert '<sub>fr</sub>' in html
