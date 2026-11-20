"""Tests for src/merge_mels.py (average-linkage merging of MELs).

Self-contained: every test writes tiny MEL files under tmp_path.
"""

import collections
import io
import json
import random
import xml.etree.ElementTree as ET

import pytest

import merge_mels as mm
import mel as mel_module
import read

XML_LANG = '{http://www.w3.org/XML/1998/namespace}lang'


# ── helpers ───────────────────────────────────────────────────────────────────

def write_mel(path, mels):
    """mels: {id: [gloss | (gloss, lang) | None, ...]}  (None -> empty <gl/>)."""
    root = ET.Element('semantics')
    for mel_id, glosses in mels.items():
        m = ET.SubElement(root, 'mel', id=mel_id)
        for g in glosses:
            lang = None
            if isinstance(g, tuple):
                g, lang = g
            gl = ET.SubElement(m, 'gl')
            gl.text = g
            if lang:
                gl.set(XML_LANG, lang)
    ET.ElementTree(root).write(path, encoding='utf-8', xml_declaration=True)
    return str(path)


def merge(paths, **kw):
    kw.setdefault('events', [])
    kw.setdefault('stats', collections.Counter())
    return mm.merge_files([str(p) for p in paths], **kw)


def gloss_sets(merged):
    return sorted(sorted(gl) for _, _, gl in merged)


def source_sets(merged):
    return sorted(sorted(s.name for s in srcs) for _, srcs, _ in merged)


def render(merged):
    buf = io.StringIO()
    mm.write_mel_file(merged, buf)
    return buf.getvalue()


# ── normalization ─────────────────────────────────────────────────────────────

SAMPLE_GLOSSES = [
    'body, animal body', 'spine; backbone', 'to give up the ship', 'numb, be',
    'bark (of a tree)', "one's self", 'water|rain', 'boiled grain: ideally rice',
    'be sick', 'fatigué, être', 'a/b', '*keyterm', 'what?', 'stop!',
]


@pytest.mark.parametrize('gloss', SAMPLE_GLOSSES)
def test_phrase_normalizer_is_part_of_normalize_gloss(gloss):
    """normalize_gloss_phrases is steps 1-5 of normalize_gloss; they must not
    drift apart."""
    assert set(mel_module.normalize_gloss_phrases(gloss)) <= set(mel_module.normalize_gloss(gloss))


def test_phrase_normalizer_examples():
    n = mel_module.normalize_gloss_phrases
    assert n('body, animal body') == ('body', 'animal body')   # no bare 'animal'
    assert n('numb, be') == ('numb',)
    assert n('bark (of a tree)') == ('bark',)
    assert n('to give up the ship') == ('give up the ship',)


def test_merging_uses_normalized_lowercased_glosses(tmp_path):
    f = write_mel(tmp_path / 'a.xml', {'1': ['Body, Animal Body', 'Bark (of a tree)']})
    (mel_id, srcs, glosses), = merge([f])
    assert list(glosses) == ['animal body', 'bark', 'body']


# ── guardrails ────────────────────────────────────────────────────────────────

def test_empty_glosses_are_dropped_and_never_bridge(tmp_path):
    f = write_mel(tmp_path / 'a.xml', {
        '1': [None, 'cat', 'feline'],
        '2': [None, 'dog', 'canine'],
        '3': [None],               # nothing left: dropped entirely
    })
    stats = collections.Counter()
    merged = merge([f], stats=stats)
    assert gloss_sets(merged) == [['canine', 'dog'], ['cat', 'feline']]
    assert stats['empty_glosses'] == 3 and stats['empty_mels'] == 1


def test_duplicates_and_subsets_are_absorbed_and_keep_their_ids(tmp_path):
    f = write_mel(tmp_path / 'a.xml', {
        '1': ['x', 'y', 'z'], '2': ['x', 'y', 'z'], '3': ['x', 'y'], '4': ['p', 'q']})
    merged = merge([f])
    assert gloss_sets(merged) == [['p', 'q'], ['x', 'y', 'z']]
    assert source_sets(merged) == [['a.xml:1', 'a.xml:2', 'a.xml:3'], ['a.xml:4']]


def test_chaining_is_resisted_but_near_duplicates_merge(tmp_path):
    # A-x-B-y-C is a chain: transitive closure would make one MEL of 10 glosses.
    f = write_mel(tmp_path / 'a.xml', {
        'A': ['a1', 'a2', 'a3', 'x'],
        'B': ['x', 'b1', 'b2', 'y'],
        'C': ['y', 'c1', 'c2', 'c3'],
        # P and Q are near-duplicates
        'P': ['p1', 'p2', 'p3', 'p4'],
        'Q': ['p1', 'p2', 'p3', 'q1'],
    })
    merged = merge([f], threshold=0.35)
    assert source_sets(merged) == [['a.xml:A'], ['a.xml:B'], ['a.xml:C'],
                                   ['a.xml:P', 'a.xml:Q']]


def test_average_not_single_link(tmp_path):
    """C is close to B only; D is a near-duplicate of B. B+D merge, and C
    (which overlaps B but not D) is judged against the *pair*, so it stays out
    where single linkage would have pulled it in."""
    f = write_mel(tmp_path / 'a.xml', {
        'B': ['b1', 'b2', 'b3', 'k1', 'k2'],
        'D': ['b1', 'b2', 'b3', 'k1', 'd1'],
        'C': ['k2', 'c1', 'c2', 'c3'],
    })
    merged = merge([f], threshold=0.35)
    assert source_sets(merged) == [['a.xml:B', 'a.xml:D'], ['a.xml:C']]


def test_max_size_refuses_merge(tmp_path):
    f = write_mel(tmp_path / 'a.xml', {
        '1': ['a', 'b', 'c', 'd', 'e'], '2': ['a', 'b', 'c', 'd', 'f']})
    stats = collections.Counter()
    ev = []
    merged = merge([f], max_size=5, stats=stats, events=ev)
    assert len(merged) == 2 and stats['refused'] == 1
    assert [e['event'] for e in ev] == ['refused']
    merged = merge([f], max_size=6)
    assert len(merged) == 1 and len(merged[0][2]) == 6


def test_refusal_is_permanent(tmp_path):
    """Once X+Y is refused for size, X+Y+Z can only be larger."""
    f = write_mel(tmp_path / 'a.xml', {
        '1': ['a', 'b', 'c', 'd', 'e'], '2': ['a', 'b', 'c', 'd', 'f'],
        '3': ['a', 'b', 'c', 'd', 'g']})
    merged = merge([f], max_size=6)
    assert all(len(gl) <= 6 for _, _, gl in merged)


def test_input_mel_over_max_size_passes_through(tmp_path):
    big = [f'g{i}' for i in range(10)]
    f = write_mel(tmp_path / 'a.xml', {'1': big, '2': big[:9] + ['other']})
    stats = collections.Counter()
    merged = merge([f], max_size=5, stats=stats)
    assert len(merged) == 2 and stats['over_cap'] == 2


def test_component_limit_warns_and_skips_unless_allowed(tmp_path, capsys):
    f = write_mel(tmp_path / 'a.xml', {
        '1': ['a', 'b', 'c', 'd'], '2': ['a', 'b', 'c', 'e'], '3': ['a', 'b', 'c', 'f']})
    stats = collections.Counter()
    merged = merge([f], component_limit=2, stats=stats)
    assert len(merged) == 3 and stats['skipped_components'] == [3]
    assert 'exceeds --component-limit' in capsys.readouterr().err
    merged = merge([f], component_limit=2, allow_large=True)
    assert len(merged) < 3


def test_leftover_overlap_is_kept(tmp_path):
    """'strike' belongs to two unrelated senses; both merged MELs keep it."""
    f = write_mel(tmp_path / 'a.xml', {
        'hit1': ['strike', 'hit', 'beat', 'smack'], 'hit2': ['hit', 'beat', 'smack', 'thump'],
        'wk1': ['strike', 'walkout', 'protest', 'stoppage'],
        'wk2': ['walkout', 'protest', 'stoppage', 'picket']})
    merged = merge([f], threshold=0.35)
    assert len(merged) == 2
    assert all('strike' in gl for _, _, gl in merged)


def test_idempotent_on_its_own_output(tmp_path):
    f = write_mel(tmp_path / 'a.xml', {
        'A': ['a1', 'a2', 'a3', 'x'], 'B': ['x', 'b1', 'b2', 'y'],
        'P': ['p1', 'p2', 'p3', 'p4'], 'Q': ['p1', 'p2', 'p3', 'q1']})
    first = merge([f])
    out = tmp_path / 'once.xml'
    out.write_text(render(first), encoding='utf-8')
    second = merge([out])
    assert gloss_sets(second) == gloss_sets(first)


# ── provenance, ids, format ───────────────────────────────────────────────────

def test_new_ids_and_originalid_sources(tmp_path):
    f = write_mel(tmp_path / 'a.xml', {
        'm1': ['p1', 'p2', 'p3', 'p4'], 'm2': ['p1', 'p2', 'p3', 'q1'], 'm3': ['z']})
    merged = merge([f])
    assert [m[0] for m in merged] == ['merged001', 'merged002']
    root = ET.fromstring(render(merged))
    first = root.findall('mel')[0]
    originals = [(o.get('file'), o.text) for o in first.find('sources').iterfind('originalid')]
    assert originals == [('a.xml', 'm1'), ('a.xml', 'm2')]
    assert [g.text for g in first.iterfind('gl')] == ['p1', 'p2', 'p3', 'p4', 'q1']


def test_output_is_readable_by_re_mel_reader(tmp_path):
    f = write_mel(tmp_path / 'a.xml', {'m1': ['cat', 'feline']})
    out = tmp_path / 'out.xml'
    out.write_text(render(merge([f])), encoding='utf-8')
    mels = read.read_mel_file(str(out))
    assert len(mels) == 1 and mels[0].id == 'merged001'
    assert sorted(mels[0].glosses) == ['cat', 'feline']


def test_multiple_files_with_colliding_ids(tmp_path):
    a = write_mel(tmp_path / 'a.xml', {'m1': ['p1', 'p2', 'p3', 'p4']})
    b = write_mel(tmp_path / 'b.xml', {'m1': ['p1', 'p2', 'p3', 'q1'], 'm2': ['zzz']})
    merged = merge([a, b])
    assert source_sets(merged) == [['a.xml:m1', 'b.xml:m1'], ['b.xml:m2']]
    assert 'file="a.xml"' in render(merged) and 'file="b.xml"' in render(merged)


def test_result_does_not_depend_on_file_order(tmp_path):
    a = write_mel(tmp_path / 'a.xml', {'m1': ['p1', 'p2', 'p3', 'p4'], 'm2': ['x', 'y']})
    b = write_mel(tmp_path / 'b.xml', {'m1': ['p1', 'p2', 'p3', 'q1'], 'm9': ['y', 'x', 'w']})
    assert render(merge([a, b])) == render(merge([b, a]))


def test_natural_id_order(tmp_path):
    f = write_mel(tmp_path / 'a.xml', {'m10': ['ten'], 'm2': ['two'], 'm1': ['one']})
    merged = merge([f])
    assert [s[0].id for _, s, _ in merged] == ['m1', 'm2', 'm10']


def test_xml_lang_kept_when_unambiguous(tmp_path):
    # m1 and m2 have the same normalized glosses, so they fold into one MEL.
    f = write_mel(tmp_path / 'a.xml', {
        'm1': [('give', 'en'), ('donner', 'fr'), 'present', ('bank', 'en')],
        'm2': [('give', 'en'), ('donner', 'fr'), 'present', ('bank', 'fr')]})
    merged = merge([f])
    assert len(merged) == 1
    root = ET.fromstring(render(merged))
    langs = {g.text: g.get(XML_LANG) for g in root.iter('gl')}
    assert langs['give'] == 'en' and langs['donner'] == 'fr'
    assert langs['present'] is None
    assert langs['bank'] is None          # en in one source, fr in another: ambiguous


def test_unreadable_input_fails_loudly(tmp_path):
    bad = tmp_path / 'bad.xml'
    bad.write_text('<semantics><mel>', encoding='utf-8')
    with pytest.raises(SystemExit):
        mm.main([str(bad)])


# ── command line ──────────────────────────────────────────────────────────────

def test_cli_mel_on_stdout_report_on_stderr_log_to_file(tmp_path, capsys):
    f = write_mel(tmp_path / 'a.xml', {
        'm1': ['p1', 'p2', 'p3', 'p4'], 'm2': ['p1', 'p2', 'p3', 'q1']})
    log = tmp_path / 'merge.log'
    mm.main([f, '--log', str(log), '--id-prefix', 'x'])
    cap = capsys.readouterr()
    root = ET.fromstring(cap.out)               # stdout is exactly the MEL file
    assert [m.get('id') for m in root.iter('mel')] == ['x001']
    assert 'merge_mels summary' in cap.err
    events = [json.loads(l) for l in log.read_text().splitlines()]
    kinds = [e['event'] for e in events]
    assert 'merge' in kinds and kinds[-1] == 'output'
    merge_event = next(e for e in events if e['event'] == 'merge')
    assert merge_event['shared'] == ['p1', 'p2', 'p3']


@pytest.mark.parametrize('bad', ['0', '-0.1', '1.5'])
def test_cli_rejects_bad_threshold(tmp_path, bad):
    f = write_mel(tmp_path / 'a.xml', {'m1': ['a']})
    with pytest.raises(SystemExit):
        mm.main([f, '--threshold', bad])


# ── omitted glosses ───────────────────────────────────────────────────────────

def test_dropped_glosses_are_counted_and_nothing_else_is_omitted(tmp_path):
    f = write_mel(tmp_path / 'a.xml', {
        '1': [None, 'cat', '(only a parenthetical)', 'feline (animal)'],
        '2': ['dog', 'Dog', 'canine']})
    stats = collections.Counter()
    merged = merge([f], stats=stats)
    assert stats['empty_glosses'] == 1
    assert stats['glosses_unnormalizable'] == 1
    assert stats['unnormalizable_examples'] == ['(only a parenthetical)']
    assert stats['glosses_read'] == 6                    # non-empty <gl> elements
    assert stats['input_keys'] == {'cat', 'feline', 'dog', 'canine'}
    assert mm.omitted_glosses(stats, merged) == []


def test_omitted_glosses_reports_a_missing_gloss(tmp_path):
    f = write_mel(tmp_path / 'a.xml', {'1': ['cat', 'feline']})
    stats = collections.Counter()
    merged = merge([f], stats=stats)
    stats['input_keys'].add('ghost')
    assert mm.omitted_glosses(stats, merged) == ['ghost']


# ── components ────────────────────────────────────────────────────────────────

def chain_of_hubs(tmp_path, n=12):
    """n MELs that all share the hub gloss 'body' but are otherwise unrelated:
    one gloss-linked group, but no two of them similar enough to merge."""
    return write_mel(tmp_path / 'hub.xml', {
        f'm{i}': ['body', f'a{i}', f'b{i}', f'c{i}', f'd{i}'] for i in range(n)})


def test_components_are_by_similarity_not_by_shared_gloss(tmp_path):
    f = chain_of_hubs(tmp_path)
    stats = collections.Counter()
    merged = merge([f], stats=stats)
    assert len(merged) == 12                              # nothing is similar enough
    assert stats['gloss_linked_groups'] == [12]           # ...though they all share 'body'
    assert stats['components'] == 12 and stats['singleton_components'] == 12


def test_hub_glosses_no_longer_trip_the_component_limit(tmp_path, capsys):
    f = chain_of_hubs(tmp_path)
    stats = collections.Counter()
    merge([f], component_limit=3, stats=stats)
    assert stats['skipped_components'] == []
    assert 'exceeds --component-limit' not in capsys.readouterr().err


def test_merges_never_cross_a_component(tmp_path):
    f = write_mel(tmp_path / 'a.xml', {
        'p1': ['p1', 'p2', 'p3', 'p4'], 'p2': ['p1', 'p2', 'p3', 'q1'],
        'x1': ['x1', 'x2', 'x3', 'x4'], 'x2': ['x1', 'x2', 'x3', 'y1'],
        'lone': ['body']})
    stats = collections.Counter()
    merge([f], stats=stats)
    assert sorted(stats['component_sizes']) == [1, 2, 2]
    assert stats['singleton_components'] == 1


# ── similarity statistics, sweep and replay ───────────────────────────────────

def random_mels(tmp_path, seed, n=90, vocab=45):
    rng = random.Random(seed)
    words = [f'w{i}' for i in range(vocab)]
    return write_mel(tmp_path / f'r{seed}.xml', {
        f'm{i}': rng.sample(words, rng.randint(3, 9)) for i in range(n)})


@pytest.mark.parametrize('seed', [1, 2, 3])
@pytest.mark.parametrize('threshold', [0.2, 0.35, 0.5])
def test_sweeping_from_a_lower_floor_gives_the_same_output(tmp_path, seed, threshold):
    """UPGMA merges in non-increasing order of similarity, so clustering down
    to a floor and replaying at `threshold` equals clustering at `threshold`."""
    f = random_mels(tmp_path, seed)
    direct = merge([f], threshold=threshold, sweep_floor=0, max_size=12)
    swept = merge([f], threshold=threshold, sweep_floor=0.1, max_size=12)
    assert render(direct) == render(swept)


@pytest.mark.parametrize('seed', [1, 2])
def test_every_sweep_row_matches_a_run_at_that_threshold(tmp_path, seed):
    f = random_mels(tmp_path, seed)
    stats = collections.Counter()
    merge([f], threshold=0.35, sweep_floor=0.15, max_size=12, stats=stats)
    assert stats['sweep_rows']
    for row in stats['sweep_rows']:
        assert not row['approx']
        direct = collections.Counter()
        merged = merge([f], threshold=row['threshold'], sweep_floor=0,
                       max_size=12, stats=direct)
        assert len(merged) == row['mels']
        assert sum(1 for c in direct['cohesion'] if c) == row['merged_mels']
        assert max(len(gl) for _, _, gl in merged) == row['largest']


def test_oversize_components_fall_back_to_a_higher_sweep_floor(tmp_path):
    f = random_mels(tmp_path, 5)
    whole = merge([f], threshold=0.35, sweep_floor=0.1, max_size=12)
    stats = collections.Counter()
    small = merge([f], threshold=0.35, sweep_floor=0.1, max_size=12,
                  component_limit=8, stats=stats)
    assert render(whole) == render(small)
    assert stats['skipped_components'] == [] or max(stats['component_sizes']) > 8


def test_merge_similarities_never_increase_within_a_component(tmp_path):
    f = random_mels(tmp_path, 4)
    stats = collections.Counter()
    merge([f], threshold=0.35, sweep_floor=0.05, max_size=12, stats=stats)
    for rec in stats['sweep']['comps']:
        sims = [v for kind, v, *_ in rec['steps']]
        assert sims == sorted(sims, reverse=True)


def test_cohesion_matches_a_direct_computation(tmp_path):
    f = random_mels(tmp_path, 6)
    stats = collections.Counter()
    merged = merge([f], threshold=0.3, sweep_floor=0, max_size=12, stats=stats)
    assert len(stats['cohesion']) == len(merged)
    checked = 0
    for (mel_id, srcs, glosses), coh in zip(merged, stats['cohesion']):
        if coh is None:                 # a single MEL (plus any duplicates it absorbed)
            continue
        checked += 1
        # every merge was made at >= threshold, so the average over all pairs is too
        assert coh['mean'] >= 0.3 - 1e-9
        assert coh['min'] <= coh['median'] <= 1 and coh['min'] <= coh['mean']
        assert coh['sd'] >= 0 and coh['k'] >= 2
    assert checked


def test_replay_tracks_the_exact_mean_pairwise_similarity(tmp_path):
    f = random_mels(tmp_path, 7)
    stats = collections.Counter()
    merge([f], threshold=0.3, sweep_floor=0, max_size=12, stats=stats)
    weight = stats['sweep']['weight']
    for rec in stats['sweep']['comps']:
        cl, mean_pair, _, _ = mm.replay(len(rec['idx']), rec['steps'], 0.3)
        for members, mp in zip(cl, mean_pair):
            if len(members) < 2:
                continue
            sims = [mm.pair_sim(rec['glosssets'][a], rec['glosssets'][b], weight)
                    for a in members for b in members if a < b]
            assert mp == pytest.approx(sum(sims) / len(sims))


def test_pair_stats_summarize_values():
    ps = mm.PairStats()
    vals = [i / 100 for i in range(1, 100)]
    ps.add(vals[:50])
    ps.add(vals[50:])
    assert ps.n == 99
    assert ps.mean == pytest.approx(0.5)
    assert ps.sd == pytest.approx(0.2860, abs=1e-3)
    assert ps.quantile(0.5) == pytest.approx(0.5, abs=0.01)
    assert ps.count_at_least(0.9) == pytest.approx(10, abs=2)


def test_cli_report_has_the_new_sections(tmp_path, capsys):
    f = random_mels(tmp_path, 8)
    log = tmp_path / 'm.log'
    mm.main([f, '--log', str(log), '--max-size', '12'])
    err = capsys.readouterr().err
    for heading in ('glosses (input -> output)', 'input glosses omitted from the output: 0',
                    'components (groups of MELs that could possibly merge)',
                    'similarity statistics', 'cohesion of the', 'threshold sweep'):
        assert heading in err
    events = [json.loads(l) for l in log.read_text().splitlines()]
    assert any(e['event'] == 'sweep' for e in events)
    outs = [e for e in events if e['event'] == 'output']
    assert any(e['cohesion'] for e in outs)


def test_cli_rejects_bad_sweep_floor(tmp_path):
    f = write_mel(tmp_path / 'a.xml', {'m1': ['a']})
    with pytest.raises(SystemExit):
        mm.main([f, '--sweep-floor', '1.5'])
