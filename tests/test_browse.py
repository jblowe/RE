"""Tests for the Browse pane (REwww/browse.py and its two routes)."""

import os
import shutil

import pytest

import browse
import routes
import xslt   # REwww/xslt.py (conftest puts REwww/ on sys.path)


@pytest.fixture(autouse=True)
def _styles(repo_root):
    xslt.STYLES_DIR = os.path.join(repo_root, 'styles')


@pytest.fixture
def project(tmp_path, repo_root):
    """A small project directory: a copy of DIS plus a sets file, a runs/
    folder, non-XML files and an XML file of no known kind."""
    dis = os.path.join(repo_root, 'projects', 'DIS')
    if not os.path.isdir(dis):
        pytest.skip('DIS project not found')
    d = tmp_path / 'P'
    d.mkdir()
    for name in ('DIS.standard.correspondences.xml', 'DIS.tag.data.xml',
                 'DIS.hand.mel.xml', 'DIS.fuzzy.fuz.xml', 'DIS.classes.xml'):
        shutil.copy(os.path.join(dis, name), d / name)
    (d / 'x.sets.xml').write_text(
        '<reconstruction><languages><lg>a</lg></languages><sets/>'
        '<isolates><rfx><lg>a</lg><lx>x</lx><gl>g</gl></rfx></isolates>'
        '</reconstruction>', encoding='utf-8')
    (d / 'odd.xml').write_text('<something><a/></something>', encoding='utf-8')
    (d / 'broken.xml').write_text('<oops', encoding='utf-8')
    (d / 'notes.md').write_text('# not xml', encoding='utf-8')
    (d / 'table.csv').write_text('a,b', encoding='utf-8')
    (d / '.hidden.xml').write_text('<fuzzy/>', encoding='utf-8')
    runs = d / 'runs'
    runs.mkdir()
    (runs / 'P.20260101-000000.sets.xml').write_text('<reconstruction/>', encoding='utf-8')
    return str(d)


class TestClassify:
    def test_type_comes_from_the_root_element_not_the_name(self, project):
        kinds = {f['name']: f['type'] for f in browse.list_files(project)}
        assert kinds['DIS.standard.correspondences.xml'] == 'toc'
        assert kinds['DIS.tag.data.xml'] == 'lexicon'
        assert kinds['DIS.hand.mel.xml'] == 'mel'
        assert kinds['DIS.fuzzy.fuz.xml'] == 'fuzzy'
        assert kinds['x.sets.xml'] == 'sets'
        # a class file has no stylesheet of its own, whatever its name
        assert kinds['DIS.classes.xml'] == 'other'
        assert kinds['odd.xml'] == 'other'

    def test_a_file_named_like_a_type_but_with_another_root(self, tmp_path):
        p = tmp_path / 'X.fuz.xml'
        p.write_text('<tableOfCorr/>', encoding='utf-8')
        assert browse.classify(str(p))[0] == 'toc'

    def test_unreadable_xml_is_other(self, project):
        assert browse.classify(os.path.join(project, 'broken.xml'))[0] == 'other'


class TestListFiles:
    def test_only_xml_in_the_project_directory(self, project):
        names = {f['name'] for f in browse.list_files(project)}
        assert 'notes.md' not in names and 'table.csv' not in names
        assert '.hidden.xml' not in names
        assert 'runs' not in names
        assert 'P.20260101-000000.sets.xml' not in names      # run outputs are not listed

    def test_ordered_by_type_then_name(self, project):
        files = browse.list_files(project)
        types = [f['type'] for f in files]
        order = ['toc', 'lexicon', 'mel', 'fuzzy', 'sets', 'other']
        assert types == sorted(types, key=order.index)
        for t in set(types):
            names = [f['name'].lower() for f in files if f['type'] == t]
            assert names == sorted(names)

    def test_entry_fields(self, project):
        f = next(f for f in browse.list_files(project) if f['name'] == 'DIS.tag.data.xml')
        assert f['group'] == 'Lexicons' and f['size'] > 0
        assert [v['key'] for v in f['views']] == ['paragraph', 'table']

    def test_sets_views_include_isolates_only_when_present(self, project, tmp_path):
        f = next(f for f in browse.list_files(project) if f['name'] == 'x.sets.xml')
        assert [v['key'] for v in f['views']] == ['paragraph', 'table', 'isolates']
        bare = tmp_path / 'bare.sets.xml'
        bare.write_text('<reconstruction><sets/></reconstruction>', encoding='utf-8')
        assert [v['key'] for v in browse.classify(str(bare))[2]] == ['paragraph', 'table']

    def test_missing_directory(self, tmp_path):
        assert browse.list_files(str(tmp_path / 'nope')) == []


class TestResolve:
    def test_listed_file(self, project):
        assert browse.resolve(project, 'DIS.tag.data.xml') == \
            os.path.realpath(os.path.join(project, 'DIS.tag.data.xml'))

    @pytest.mark.parametrize('name', [
        '', '../P/DIS.tag.data.xml', 'runs/P.20260101-000000.sets.xml',
        '/etc/passwd', 'notes.md', '.hidden.xml', 'missing.xml', '..'])
    def test_refused(self, project, name):
        assert browse.resolve(project, name) is None

    def test_symlink_out_of_the_project_is_refused(self, project, tmp_path):
        outside = tmp_path / 'outside.xml'
        outside.write_text('<fuzzy/>', encoding='utf-8')
        os.symlink(outside, os.path.join(project, 'link.xml'))
        assert browse.resolve(project, 'link.xml') is None


class TestRender:
    def test_each_standard_type_renders(self, project):
        for name, marker in [('DIS.standard.correspondences.xml', '<table'),
                             ('DIS.tag.data.xml', 'tag'),
                             ('DIS.hand.mel.xml', 'm1'),
                             ('DIS.fuzzy.fuz.xml', '<table')]:
            html = browse.render(os.path.join(project, name))
            assert 'text-danger' not in html, name
            assert marker in html, name

    def test_lexicon_views_differ(self, project):
        path = os.path.join(project, 'DIS.tag.data.xml')
        para, table = browse.render(path, 'paragraph'), browse.render(path, 'table')
        assert para == browse.render(path)                 # first view is the standard one
        assert '<table' in table and para != table

    def test_sets_isolates_view(self, project):
        html = browse.render(os.path.join(project, 'x.sets.xml'), 'isolates')
        assert 'text-danger' not in html

    def test_unknown_view_gives_the_standard_one(self, project):
        path = os.path.join(project, 'DIS.tag.data.xml')
        assert browse.render(path, 'nonsense') == browse.render(path)

    def test_other_xml_is_shown_as_escaped_source(self, project):
        html = browse.render(os.path.join(project, 'odd.xml'))
        assert 'showing the source' in html
        assert '&lt;something&gt;' in html and '<something>' not in html

    def test_broken_xml_gives_a_message(self, project):
        assert 'text-danger' in browse.render(os.path.join(project, 'broken.xml'))


class TestRoutes:
    @pytest.fixture
    def run_id(self, project, monkeypatch):
        monkeypatch.setitem(routes.proj_module.projects, 'P', project)
        with routes._runs_lock:
            routes._runs['browse-test'] = {'id': 'browse-test', 'project': 'P',
                                           'status': 'done', 'files': {}}
        yield 'browse-test'
        with routes._runs_lock:
            routes._runs.pop('browse-test', None)

    def test_files(self, client, run_id):
        data = client.get(f'/api/browse/{run_id}/files').get_json()
        assert data['project'] == 'P'
        assert 'DIS.tag.data.xml' in {f['name'] for f in data['files']}

    def test_render(self, client, run_id):
        r = client.get(f'/api/browse/{run_id}/render?file=DIS.tag.data.xml&view=table')
        assert r.status_code == 200 and b'<table' in r.data

    def test_render_refuses_paths(self, client, run_id):
        for bad in ('../x.xml', 'runs/P.20260101-000000.sets.xml', 'notes.md', ''):
            r = client.get(f'/api/browse/{run_id}/render', query_string={'file': bad})
            assert r.status_code == 404, bad

    def test_diff_with_another_file(self, client, run_id):
        """?other= compares with a same-type file of the project; it refuses
        other kinds of file and anything that is not a project file."""
        url = f'/api/browse/{run_id}/diff'

        def diff(other):
            q = {'file': 'DIS.fuzzy.fuz.xml', 'other': other}
            return client.get(url, query_string=q).get_data(as_text=True)

        assert 'No differences.' in diff('DIS.fuzzy.fuz.xml')
        assert 'not the same kind' in diff('DIS.hand.mel.xml')
        for bad in ('../x.xml', 'nope.xml', '/etc/passwd', 'notes.md'):
            assert 'No such file' in diff(bad), bad

    def test_unknown_run(self, client):
        assert client.get('/api/browse/nope/files').status_code == 404
        assert client.get('/api/browse/nope/render?file=a.xml').status_code == 404

    def test_page_has_the_browse_tab(self, client):
        html = client.get('/').get_data(as_text=True)
        assert 'id="tab-browse-nav"' in html and 'id="browse-file"' in html
