"""Tests for REwww Flask route handlers.

Fast tests (no RE reconstruction):
  - index page, /api/projects, error handling, history, poll for unknown run

Slow tests (marked @pytest.mark.slow — run a real DIS reconstruction):
  - POST /api/run → poll until done → inspect result structure
"""

import json
import time
import pytest


# ─────────────────────────────────────────────────────────────────────────────
# Fast tests
# ─────────────────────────────────────────────────────────────────────────────

class TestIndexPage:
    def test_returns_200(self, client):
        r = client.get('/')
        assert r.status_code == 200

    def test_html_content_type(self, client):
        r = client.get('/')
        assert 'text/html' in r.content_type

    def test_contains_known_project(self, client):
        r = client.get('/')
        body = r.data.decode()
        # DIS and POLYNESIAN are checked-in projects; at least one must appear.
        assert 'DIS' in body or 'POLYNESIAN' in body


class TestApiProjects:
    def test_returns_200(self, client):
        r = client.get('/api/projects')
        assert r.status_code == 200

    def test_returns_json(self, client):
        r = client.get('/api/projects')
        data = r.get_json()
        assert isinstance(data, dict)

    def test_dis_project_present(self, client):
        r = client.get('/api/projects')
        data = r.get_json()
        assert 'DIS' in data

    def test_dis_has_expected_keys(self, client):
        r = client.get('/api/projects')
        dis = r.get_json()['DIS']
        for key in ('path', 'recons', 'mels', 'fuzzies'):
            assert key in dis, f'missing key {key!r} in DIS project data'

    def test_dis_has_standard_recon(self, client):
        r = client.get('/api/projects')
        recons = r.get_json()['DIS']['recons']
        assert any('standard' in rc for rc in recons), \
            f'standard recon not found in {recons}'


class TestApiRunValidation:
    def test_unknown_project_returns_400(self, client):
        r = client.post('/api/run',
                        data=json.dumps({'project': 'NO_SUCH_PROJECT'}),
                        content_type='application/json')
        assert r.status_code == 400

    def test_error_message_mentions_project(self, client):
        r = client.post('/api/run',
                        data=json.dumps({'project': 'NO_SUCH_PROJECT'}),
                        content_type='application/json')
        body = r.get_json()
        assert 'error' in body
        assert 'NO_SUCH_PROJECT' in body['error']

    def test_empty_body_returns_400(self, client):
        # project key is missing → treated as unknown project
        r = client.post('/api/run',
                        data=json.dumps({}),
                        content_type='application/json')
        assert r.status_code == 400


class TestApiPoll:
    def test_unknown_run_id_returns_404(self, client):
        """Polling an unknown run_id returns 404 with an error payload."""
        r = client.get('/api/poll/00000000-0000-0000-0000-000000000000')
        assert r.status_code == 404

    def test_unknown_run_id_has_error_key(self, client):
        r = client.get('/api/poll/00000000-0000-0000-0000-000000000000')
        data = r.get_json()
        assert 'error' in data


class TestApiHistory:
    """api_history returns { "runs": [...] } — a dict with a 'runs' key."""

    def test_dis_history_returns_200(self, client):
        r = client.get('/api/history/DIS')
        assert r.status_code == 200

    def test_dis_history_has_runs_key(self, client):
        r = client.get('/api/history/DIS')
        data = r.get_json()
        assert 'runs' in data

    def test_dis_history_runs_is_list(self, client):
        r = client.get('/api/history/DIS')
        assert isinstance(r.get_json()['runs'], list)

    def test_unknown_project_history_runs_is_empty(self, client):
        r = client.get('/api/history/NO_SUCH_PROJECT')
        data = r.get_json()
        assert data['runs'] == []


class TestApiRaw:
    def test_unknown_run_returns_error_or_404(self, client):
        r = client.get('/api/raw/no-such-run/sets')
        # Implementation may return 200 with error HTML, 404, or 400 — all acceptable.
        assert r.status_code in (200, 400, 404)

    def test_unknown_run_not_empty(self, client):
        r = client.get('/api/raw/no-such-run/sets')
        assert len(r.data) > 0


class TestApiLoadRun:
    def test_missing_run_id_returns_error(self, client):
        r = client.post('/api/load_run',
                        data=json.dumps({'run_id': 'nonexistent-run'}),
                        content_type='application/json')
        data = r.get_json()
        # Should indicate failure somehow
        assert data is not None
        assert 'error' in data or data.get('done') is False


# ─────────────────────────────────────────────────────────────────────────────
# Slow integration tests — run real DIS reconstructions
# ─────────────────────────────────────────────────────────────────────────────

def _start_run(client, project, recon, mel=None, fuzzy=None, upstream=None):
    """POST /api/run and return the JSON response."""
    body = {'project': project, 'recon': recon}
    if mel:
        body['mel'] = mel
    if fuzzy:
        body['fuzzy'] = fuzzy
    if upstream:
        body['upstream'] = upstream
    r = client.post('/api/run',
                    data=json.dumps(body),
                    content_type='application/json')
    assert r.status_code == 200, f'api_run failed: {r.data}'
    return r.get_json()


def _poll_until_done(client, run_id, timeout=120, interval=2):
    """Poll /api/poll/<run_id> until status is 'done' or 'error', or timeout.

    Note: api_poll does NOT include a 'done' key; completion is indicated by
    status == 'done'.  The 'error' status means the run thread threw an
    exception; returning immediately avoids spinning for the full timeout.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = client.get(f'/api/poll/{run_id}')
        data = r.get_json()
        if data.get('status') in ('done', 'error'):
            return data
        time.sleep(interval)
    raise TimeoutError(f'Run {run_id} did not complete within {timeout}s')


@pytest.mark.slow
def test_slavic_run_none(client):
    """Full reconstruction: SLAVIC / standard / no MEL.

    SLAVIC has no hook (no Perl pipeline) and no MEL file, making it the
    lightest project for integration testing.  The poll response should
    reach done=True with no error and carry context_match_type / spec.
    """
    start = _start_run(client, 'SLAVIC', 'standard')
    assert 'run_id' in start
    assert 'run_name' in start

    result = _poll_until_done(client, start['run_id'])

    assert result.get('status') == 'done', \
        f"Run did not complete: status={result.get('status')!r}, error={result.get('error')}"
    assert not result.get('error'), \
        f"Run finished with error: {result.get('error')}"


@pytest.mark.slow
def test_slavic_poll_returns_context_match_type(client):
    """context_match_type and spec are present in the poll response once done."""
    start = _start_run(client, 'SLAVIC', 'standard')
    result = _poll_until_done(client, start['run_id'])
    assert result.get('status') == 'done', \
        f"Run did not complete: {result.get('status')!r}"

    # These are read from the correspondences file inside the run thread.
    assert 'context_match_type' in result, \
        'context_match_type missing from poll response'
    assert 'spec' in result, \
        'spec missing from poll response'
    assert result['context_match_type'] in ('constituent', 'glyphs'), \
        f"unexpected context_match_type: {result['context_match_type']!r}"


@pytest.mark.slow
def test_slavic_lexicon_langs_after_run(client):
    """After a completed run /api/lexicon_langs returns a non-empty language list."""
    start = _start_run(client, 'SLAVIC', 'standard')
    result = _poll_until_done(client, start['run_id'])
    assert result.get('status') == 'done', \
        f"Run did not complete: {result.get('status')!r}"

    r = client.get(f"/api/lexicon_langs/{start['run_id']}")
    assert r.status_code == 200
    data = r.get_json()
    assert 'languages' in data
    assert len(data['languages']) > 0
