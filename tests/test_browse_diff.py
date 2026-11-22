"""Tests for the Browse pane's diff against an earlier commit
(REwww/diff_toc.py, REwww/browse_diff.py)."""

import os
import shutil
import subprocess

import lxml.etree as ET
import pytest

import browse
import browse_diff
import diff_toc
import xslt


@pytest.fixture(autouse=True)
def _styles(repo_root):
    xslt.STYLES_DIR = os.path.join(repo_root, 'styles')


def toc(corrs='', params='', extra=''):
    return ET.fromstring(
        '<tableOfCorr><parameters>%s</parameters>%s%s</tableOfCorr>'
        % (params, corrs, extra))


def corr(num, proto, cells, **attrs):
    a = ''.join(f' {k}="{v}"' for k, v in attrs.items())
    ms = ''.join(
        '<modern dialecte="%s">%s</modern>' % (d, ''.join(f'<seg>{s}</seg>' for s in segs))
        for d, segs in cells.items())
    return f'<corr num="{num}"><proto{a}>{proto}</proto>{ms}</corr>'


def by_num(root, num):
    return next(c for c in root.findall('corr') if c.get('num') == str(num))


def test_identical_files_have_no_differences():
    r = toc(corr(1, 'a', {'x': ['a']}) + corr(2, 'b', {'x': ['b']}))
    out, summary = diff_toc.annotate(r, r)
    assert not any(e.get('diff') for e in out.iter())
    assert all(v == 0 for s in summary.values() for v in s.values())


def test_changed_seg_is_marked_with_old_value():
    old = toc(corr(1, 'a', {'x': ['a', 'b']}))
    new = toc(corr(1, 'a', {'x': ['a', 'c']}))
    out, summary = diff_toc.annotate(old, new)
    segs = by_num(out, 1).find('modern').findall('seg')
    assert [s.get('diff') for s in segs] == [None, 'changed']
    assert segs[1].get('old') == 'b'
    assert by_num(out, 1).get('diff') == 'changed'
    assert summary['seg']['changed'] == 1 and summary['corr']['changed'] == 1


def test_added_and_deleted_segs():
    old = toc(corr(1, 'a', {'x': ['a', 'b']}))
    new = toc(corr(1, 'a', {'x': ['a', 'z', 'b']}))
    out, _ = diff_toc.annotate(old, new)
    segs = by_num(out, 1).find('modern').findall('seg')
    assert [(s.text, s.get('diff')) for s in segs] == [('a', None), ('z', 'added'), ('b', None)]
    out, _ = diff_toc.annotate(new, old)
    segs = by_num(out, 1).find('modern').findall('seg')
    assert [(s.text, s.get('diff')) for s in segs] == [('a', None), ('z', 'deleted'), ('b', None)]


def test_deleted_seg_at_end_keeps_order():
    old = toc(corr(1, 'a', {'x': ['a', 'b', 'c']}))
    new = toc(corr(1, 'a', {'x': ['a']}))
    out, _ = diff_toc.annotate(old, new)
    segs = by_num(out, 1).find('modern').findall('seg')
    assert [(s.text, s.get('diff')) for s in segs] == [
        ('a', None), ('b', 'deleted'), ('c', 'deleted')]


def test_renumbering_is_not_a_change():
    old = toc(corr(1, 'a', {'x': ['a']}) + corr(2, 'b', {'x': ['b']}))
    new = toc(corr(1, 'new', {'x': ['n']}) + corr(2, 'a', {'x': ['a']})
              + corr(3, 'b', {'x': ['b']}))
    out, summary = diff_toc.annotate(old, new)
    assert by_num(out, 1).get('diff') == 'added'
    a, b = by_num(out, 2), by_num(out, 3)
    assert a.get('diff') == 'changed' and a.get('diff_num') and a.get('old_num') == '1'
    assert b.get('old_num') == '2'
    assert not any(e.get('diff') for e in a.iter('modern', 'seg'))
    assert summary['corr']['added'] == 1 and summary['corr']['deleted'] == 0


def test_deleted_corr_is_kept_in_place():
    old = toc(corr(1, 'a', {'x': ['a']}) + corr(2, 'b', {'x': ['b']})
              + corr(3, 'c', {'x': ['c']}))
    new = toc(corr(1, 'a', {'x': ['a']}) + corr(3, 'c', {'x': ['c']}))
    out, summary = diff_toc.annotate(old, new)
    assert [(c.get('num'), c.get('diff')) for c in out.findall('corr')] == [
        ('1', None), ('2', 'deleted'), ('3', None)]
    assert all(s.get('diff') == 'deleted' for s in by_num(out, 2).iter('seg'))
    assert summary['corr']['deleted'] == 1


def test_changed_proto_and_context():
    old = toc(corr(1, 'a', {'x': ['a']}, syll='R', contextR='U'))
    new = toc(corr(1, 'e', {'x': ['a']}, syll='T', contextR='U'))
    out, _ = diff_toc.annotate(old, new)
    c = by_num(out, 1)
    assert c.get('diff') == 'changed'
    assert (c.get('old_proto'), c.get('old_syll')) == ('a', 'R')
    assert c.get('diff_contextR') is None


def test_dialect_added_and_removed():
    old = toc(corr(1, 'a', {'x': ['a'], 'y': ['a']}))
    new = toc(corr(1, 'a', {'x': ['a'], 'z': ['a']}))
    out, _ = diff_toc.annotate(old, new)
    ms = {m.get('dialecte'): m.get('diff') for m in by_num(out, 1).findall('modern')}
    assert ms == {'x': None, 'y': 'deleted', 'z': 'added'}
    assert [d.get('dialecte') for d in out.find('diff_dialects')] == ['x', 'y', 'z']


def test_unicode_normalization_only_difference():
    old = toc(corr(1, 'a', {'x': ['é']}))           # precomposed
    new = toc(corr(1, 'a', {'x': ['é']}))          # e + combining acute
    out, _ = diff_toc.annotate(old, new)
    seg = by_num(out, 1).find('modern/seg')
    assert seg.get('diff') == 'changed' and seg.get('norm') == '1'


def test_classes_controls_rules_and_quirks():
    old = toc(params='<class name="C" value="p,t"/><class name="V" value="a"/>'
                     '<canon name="syllabe" value="CV"/>',
              extra='<rule num="r1" stage="1"><input>a</input><outcome languages="x">b</outcome></rule>'
                    '<quirk id="x1"><lg>x</lg><lx>aa</lx><gl>g</gl><note>n</note></quirk>')
    new = toc(params='<class name="C" value="p,t,k"/><canon name="syllabe" value="CVC"/>',
              extra='<rule num="r1" stage="2"><input>a</input><outcome languages="x">b</outcome></rule>')
    out, s = diff_toc.annotate(old, new)
    cls = {c.get('name'): c for c in out.find('parameters').findall('class')}
    assert cls['C'].get('diff') == 'changed' and cls['C'].get('old_value') == 'p,t'
    assert cls['V'].get('diff') == 'deleted'
    assert out.find('parameters/canon').get('old_value') == 'CV'
    assert out.find('rule').get('old_stage') == '1'
    assert out.find('quirk').get('diff') == 'deleted'
    assert (s['class']['changed'], s['class']['deleted'], s['control']['changed'],
            s['rule']['changed'], s['quirk']['deleted']) == (1, 1, 1, 1, 1)


def render(annotated):
    return xslt.xml_to_html_from_tree(ET.ElementTree(annotated), 'toc2html-view.xsl')


def test_stylesheet_renders_diff_classes_and_opens_sections():
    old = toc(corr(1, 'a', {'x': ['a', 'b']}) + corr(2, 'b', {'x': ['b']}))
    new = toc(corr(1, 'a', {'x': ['a', 'c']}))
    out, _ = diff_toc.annotate(old, new)
    html = render(out)
    assert 'diff-added' in html and 'diff-deleted' in html
    assert '<span class="diff-deleted">b</span>' in html            # old value, red
    assert '<span class="diff-added">c</span>' in html              # new value, green
    assert 'diff-was' not in html
    assert 'collapse show' in html           # the table section opens by itself


def test_stylesheet_unchanged_without_diff_attributes():
    html = render(toc(corr(1, 'a', {'x': ['a']})))
    assert 'diff-' not in html and 'collapse show' not in html


# ── git plumbing ──────────────────────────────────────────────────────────────

def _git(d, *a):
    subprocess.run(['git', '-C', str(d), '-c', 'user.name=t', '-c', 'user.email=t@t',
                    *a], check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path):
    if not shutil.which('git'):
        pytest.skip('git not installed')
    d = tmp_path / 'proj'
    d.mkdir()
    _git(d, 'init', '-q')
    f = d / 'P.correspondences.xml'
    f.write_text(ET.tostring(toc(corr(1, 'a', {'x': ['a', 'b']}))).decode(), encoding='utf-8')
    _git(d, 'add', '.')
    _git(d, 'commit', '-q', '-m', 'first version')
    f.write_text(ET.tostring(toc(corr(1, 'a', {'x': ['a', 'c']}))).decode(), encoding='utf-8')
    _git(d, 'commit', '-qam', 'second: b to c')
    f.write_text(ET.tostring(toc(corr(1, 'a', {'x': ['a', 'd']}))).decode(), encoding='utf-8')
    return f                                     # the working copy differs from HEAD


def test_commits_and_render_diff(repo):
    cs = browse_diff.commits(str(repo))
    assert [c['subject'] for c in cs] == ['second: b to c', 'first version']
    html = browse_diff.render_diff(str(repo), 'toc', cs[1]['sha'])
    assert 'first version' in html and '<span class="diff-deleted">b</span>' in html
    html = browse_diff.render_diff(str(repo), 'toc', cs[0]['sha'][:10])
    assert '<span class="diff-deleted">c</span>' in html


def test_untracked_file_and_bad_sha(repo, tmp_path):
    (repo.parent / 'new.correspondences.xml').write_text('<tableOfCorr/>')
    with pytest.raises(browse_diff.DiffError):
        browse_diff.commits(str(repo.parent / 'new.correspondences.xml'))
    with pytest.raises(browse_diff.DiffError):
        browse_diff.render_diff(str(repo), 'toc', '--output=/tmp/x')
    with pytest.raises(browse_diff.DiffError):
        browse_diff.render_diff(str(repo), 'toc', 'deadbeefdeadbeef')


def test_stub_types_and_status(monkeypatch):
    assert browse_diff.status('toc') == 'ready'
    assert browse_diff.status('sets') == 'ready'
    assert browse_diff.status('other') is None
    monkeypatch.setitem(browse_diff.STUBS, 'future', 'future files')
    assert browse_diff.status('future') == 'stub'
    with pytest.raises(browse_diff.DiffError, match='not implemented'):
        browse_diff.render_diff('x.xml', 'future', 'abcdef1')


def test_project_in_a_subdirectory_of_the_repo(tmp_path):
    """The project need not be the repository root (e.g. a data clone holding
    several project folders)."""
    if not shutil.which('git'):
        pytest.skip('git not installed')
    sub = tmp_path / 'clone' / 'DEMO'
    sub.mkdir(parents=True)
    _git(tmp_path / 'clone', 'init', '-q')
    f = sub / 'D.correspondences.xml'
    f.write_text(ET.tostring(toc(corr(1, 'a', {'x': ['a']}))).decode(), encoding='utf-8')
    _git(tmp_path / 'clone', 'add', '.')
    _git(tmp_path / 'clone', 'commit', '-q', '-m', 'first')
    f.write_text(ET.tostring(toc(corr(1, 'a', {'x': ['b']}))).decode(), encoding='utf-8')
    cs = browse_diff.commits(str(f))
    assert [c['path'] for c in cs] == ['DEMO/D.correspondences.xml']
    assert '<span class="diff-deleted">a</span>' in browse_diff.render_diff(str(f), 'toc', cs[0]['sha'])


# ── fuzzy, MEL, lexicon, sets ─────────────────────────────────────────────────

def X(xml):
    return ET.fromstring(xml)


def run(module, stylesheet, old, new):
    out, summary = module.annotate(X(old), X(new))
    html = xslt.xml_to_html_from_tree(ET.ElementTree(out), stylesheet)
    return out, summary, html


def test_fuzzy_items_from_values_and_edited_to():
    import diff_fuzzy
    old = ('<fuzzy><item dial="tag" to="e"><from>eː</from><from>je</from></item>'
           '<item dial="ris" to="ui"><from>wi</from></item>'
           '<item dial="tuk" to="o"><from>oː</from></item></fuzzy>')
    new = ('<fuzzy><item dial="tag" to="e"><from>eː</from><from>we</from></item>'
           '<item dial="ris" to="uj"><from>wi</from></item>'
           '<item dial="mar" to="a"><from>aː</from></item></fuzzy>')
    out, s, html = run(diff_fuzzy, 'fuzzy2html.xsl', old, new)
    items = out.findall('item')
    assert items[0].find('from[@diff="changed"]').get('old') == 'je'
    assert items[1].get('old_to') == 'ui' and items[1].get('diff') == 'changed'   # not delete + add
    assert [i.get('diff') for i in items[2:]] == ['deleted', 'added']   # tuk was after ris
    assert (s['item']['added'], s['item']['deleted'], s['item']['changed']) == (1, 1, 2)
    assert 'diff-added' in html and 'diff-deleted' in html


def test_mel_renumbered_and_edited():
    import diff_mel
    old = ('<semantics><mel id="m1"><gl>beer</gl><gl>beermash</gl></mel>'
           '<mel id="m2"><gl>place</gl></mel><mel id="m3"><gl>rice</gl><gl>grain</gl></mel>'
           '</semantics>')
    new = ('<semantics><mel id="m1"><gl>new</gl></mel><mel id="m2"><gl>beer</gl><gl>beermash</gl></mel>'
           '<mel id="m3"><gl>place</gl></mel><mel id="m4"><gl>rice</gl><gl>cereal</gl></mel></semantics>')
    out, s, html = run(diff_mel, 'mel2html.xsl', old, new)
    mels = {m.find('gl').text: m for m in out.findall('mel')}
    assert mels['new'].get('diff') == 'added'
    assert mels['beer'].get('diff') is None                      # renumbered only
    assert mels['place'].get('diff') is None
    rice = mels['rice']
    assert rice.get('diff') == 'changed'                         # shares a gloss: matched
    assert [(g.text, g.get('diff')) for g in rice.findall('gl')] == [
        ('rice', None), ('cereal', 'changed')]
    assert rice.findall('gl')[1].get('old') == 'grain'
    assert '<span class="diff-deleted">grain</span>' in html


def test_mel_totals():
    import diff_mel
    old = '<semantics><totals><found value="3"/><gone value="1"/></totals><mel id="m1"><gl>a</gl></mel></semantics>'
    new = '<semantics><totals><found value="5"/><new value="1"/></totals><mel id="m1"><gl>a</gl></mel></semantics>'
    out, s, _ = run(diff_mel, 'mel2html.xsl', old, new)
    t = {e.tag: e for e in out.find('totals')}
    assert t['found'].get('old_value') == '3' and t['new'].get('diff') == 'added'
    assert t['gone'].get('diff') == 'deleted'
    assert (s['stat']['changed'], s['stat']['added'], s['stat']['deleted']) == (1, 1, 1)


def lexicon(*entries):
    return '<lexicon dialecte="x">' + ''.join(
        f'<entry id="x.{i}"><hw>{hw}</hw><gl>{gl}</gl></entry>'
        for i, (hw, gl) in enumerate(entries, 1)) + '</lexicon>'


def test_lexicon_deleted_entry_does_not_flag_renumbered_ones():
    import diff_lexicon
    old = lexicon(('pa', 'leaf'), ('ta', 'load'), ('ka', 'rice'))
    new = lexicon(('pa', 'leaf'), ('ka', 'rice'))              # ka is now x.2
    out, s, html = run(diff_lexicon, 'lexicon2table.xsl', old, new)
    assert [(e.find('hw').text, e.get('diff')) for e in out.findall('entry')] == [
        ('pa', None), ('ta', 'deleted'), ('ka', None)]
    assert s['entry'] == {'added': 0, 'deleted': 1, 'changed': 0}
    assert 'diff-deleted' in html


def test_lexicon_edited_gloss_and_headword():
    import diff_lexicon
    old = lexicon(('pa', 'leaf'), ('kantu', 'rice'))
    new = lexicon(('pa', 'small leaf'), ('kantoo', 'rice'))
    out, s, html = run(diff_lexicon, 'lexicon2table.xsl', old, new)
    a, b = out.findall('entry')
    assert a.get('old_gl') == 'leaf' and a.get('diff') == 'changed'
    assert b.get('old_hw') == 'kantu' and b.get('diff') == 'changed'
    assert s['entry']['changed'] == 2 and '<del class="diff-deleted">leaf</del>' in html


SETS = """<reconstruction><languages>{langs}</languages><sets>{sets}</sets>
<isolates>{iso}</isolates><failures>{fail}</failures></reconstruction>"""


def rfx(lg, lx, i):
    return f'<rfx><lg>{lg}</lg><lx>{lx}</lx><gl>g</gl><id>{lg}.{i}</id></rfx>'


def a_set(num, pfm, *members):
    return (f'<set><id>{num}.0</id><plg>p</plg><pfm>{pfm}</pfm><rcn>1  2</rcn><sf>'
            + ''.join(members) + '</sf></set>')


def test_sets_renumbered_changed_added_deleted():
    import diff_sets
    old = SETS.format(langs='<lg>a</lg><lg>b</lg>', iso='', fail='', sets=
        a_set(1, 'Kan', rfx('a', 'kan', 1), rfx('b', 'kan', 1)) +
        a_set(2, 'Tin', rfx('a', 'tin', 2), rfx('b', 'tin', 2)) +
        a_set(3, 'Pa', rfx('a', 'pa', 3), rfx('b', 'pa', 3)))
    new = SETS.format(langs='<lg>a</lg><lg>b</lg>', iso='', fail='', sets=
        a_set(1, 'Tin', rfx('a', 'tin', 2), rfx('b', 'tin', 2)) +          # renumbered
        a_set(2, 'Pa', rfx('a', 'pa', 3), rfx('b', 'pe', 3)) +             # one member changed
        a_set(3, 'Zu', rfx('a', 'zu', 9), rfx('b', 'zu', 9)))              # new; Kan deleted
    out, s, html = run(diff_sets, 'sets2tabular.xsl', old, new)
    byp = {st.find('pfm').text: st for st in out.findall('sets/set')}
    assert byp['Tin'].get('diff') is None
    assert byp['Pa'].get('diff') == 'changed'
    assert byp['Pa'].find('sf/rfx[lg="b"]').get('diff') == 'changed'
    assert byp['Zu'].get('diff') == 'added' and byp['Kan'].get('diff') == 'deleted'
    assert (s['set']['added'], s['set']['deleted'], s['set']['changed']) == (1, 1, 1)
    assert 'diff-added' in html and '<del class="diff-deleted">pa (g)</del>' in html or 'pa (g)' in html


def test_sets_changed_proto_form_with_same_members():
    import diff_sets
    m = rfx('a', 'x', 1) + rfx('b', 'x', 1)
    old = SETS.format(langs='<lg>a</lg>', iso='', fail='', sets=a_set(1, 'Old', m))
    new = SETS.format(langs='<lg>a</lg>', iso='', fail='', sets=a_set(1, 'New', m))
    out, s, _ = run(diff_sets, 'sets2tabular.xsl', old, new)
    st = out.find('sets/set')
    assert st.get('old_pfm') == 'Old' and s['set']['changed'] == 1


def test_sets_isolates_and_failures():
    import diff_sets
    iso = lambda i, lx: f'<rfx id="a.{i}"><lx>{lx}</lx><lg>a</lg><gl>g</gl></rfx>'
    fail = lambda i, why: (f'<rfx id="a.{i}"><lx>x</lx><lg>a</lg><gl>g</gl>'
                           f'<reasons><reason>{why}</reason></reasons></rfx>')
    old = SETS.format(langs='<lg>a</lg>', sets='', iso=iso(1, 'u') + iso(2, 'v'),
                      fail=fail(5, 'bad canon'))
    new = SETS.format(langs='<lg>a</lg>', sets='', iso=iso(1, 'u2') + iso(3, 'w'),
                      fail=fail(5, 'bad context'))
    out, s, html = run(diff_sets, 'sets2tabular.xsl', old, new)
    assert s['isolate'] == {'added': 1, 'deleted': 1, 'changed': 1}
    assert s['failure']['changed'] == 1
    assert '<del class="diff-deleted">bad canon</del>' in html


def test_render_diff_for_each_type_through_git(tmp_path):
    """End to end for the other types: the header says what is compared."""
    if not shutil.which('git'):
        pytest.skip('git not installed')
    d = tmp_path / 'p'
    d.mkdir()
    _git(d, 'init', '-q')
    cases = {
        'a.fuz.xml': ('fuzzy', '<fuzzy><item dial="a" to="x"><from>y</from></item></fuzzy>',
                      '<fuzzy><item dial="a" to="x"><from>z</from></item></fuzzy>'),
        'a.mel.xml': ('mel', '<semantics><mel id="m1"><gl>a</gl></mel></semantics>',
                      '<semantics><mel id="m1"><gl>a</gl><gl>b</gl></mel></semantics>'),
        'a.data.xml': ('lexicon', lexicon(('pa', 'x')), lexicon(('pa', 'y'))),
    }
    for name, (_t, old, _new) in cases.items():
        (d / name).write_text(old, encoding='utf-8')
    _git(d, 'add', '.')
    _git(d, 'commit', '-q', '-m', 'v1')
    for name, (t, _old, new) in cases.items():
        (d / name).write_text(new, encoding='utf-8')
        sha = browse_diff.commits(str(d / name))[0]['sha']
        html = browse_diff.render_diff(str(d / name), t, sha)
        assert 'compared with' in html and 'diff-added' in html
        assert 'Changes only' not in html


# ── two local files ───────────────────────────────────────────────────────────

def test_render_diff_files(tmp_path):
    a, b = tmp_path / 'A.correspondences.xml', tmp_path / 'B.correspondences.xml'
    a.write_text(ET.tostring(toc(corr(1, 'a', {'x': ['a', 'b']}) + corr(2, 'q', {'x': ['q']}))).decode(), encoding='utf-8')
    b.write_text(ET.tostring(toc(corr(1, 'a', {'x': ['a', 'c']}))).decode(), encoding='utf-8')
    # B is the file being viewed, A is the baseline
    html = browse_diff.render_diff_files(str(b), str(a), 'toc')
    assert '<b>B.correspondences.xml</b> compared with <b>A.correspondences.xml</b> (local file)' in html
    assert '<span class="diff-deleted">b</span>' in html and 'diff-deleted' in html   # q is only in A
    with pytest.raises(browse_diff.DiffError, match='Could not read'):
        (tmp_path / 'bad.xml').write_text('<oops')
        browse_diff.render_diff_files(str(b), str(tmp_path / 'bad.xml'), 'toc')


def test_a_change_is_a_deletion_plus_an_addition(repo_root):
    """The GitHub convention: a change is the old value in red followed by the
    new one in green; there is no separate 'changed' look."""
    old = toc(corr(1, 'a', {'x': ['a', 'b']}), params='<class name="C" value="p,t"/>')
    new = toc(corr(1, 'a', {'x': ['a', 'c']}), params='<class name="C" value="p,t,k"/>')
    out, _ = diff_toc.annotate(old, new)
    html = ' '.join(render(out).split())
    assert '<span class="diff-deleted">b</span><span class="diff-added">c</span>' in html
    # a changed field: its cell is an addition and the old value comes first, in red
    assert '<td class="diff-added"> <del class="diff-deleted">p,t</del> p,t,k</td>' in html
    assert '~' not in html.split('<table', 1)[1]                 # no 'changed' row mark
    css = open(os.path.join(repo_root, 'REwww/static/asset/css/reconengine.css'),
               encoding='utf-8').read()
    assert 'diff-changed' not in css and 'underline' not in css.split('Browse pane: diff', 1)[1]
    # GitHub's diff colours (@primer/primitives, light theme)
    for shade in ('#dafbe1', '#aceebb', '#ffebe9', '#ffcecb'):
        assert shade in css
