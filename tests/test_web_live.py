"""Bounded live-mode behavior with fake transports; no API calls."""
import json
import pytest
from relay.web import ReviewApp
from relay.workflow import ModelClient


def request(app, action='generate', **kwargs):
    return app.action(dict(token=app.token, revision=app.revision, action=action, **kwargs))


def test_live_failure_invalidates_export_and_recovers():
    calls = []
    def transport(payload):
        calls.append(payload)
        if len(calls) == 1:
            raise RuntimeError('SECRET provider detail')
        return {'choices': [{'message': {'content': json.dumps({'claims': [{'text': 'Paused.', 'citations': [{'source_id': 'log', 'quote': 'deployment paused'}]}], 'open_questions': [], 'suggested_actions': []})}}]}
    app = ReviewApp(ModelClient('https://example.invalid/v1', 'fake', 'test-model', transport), 2)
    request(app, 'export', reviewer='Reviewer', reviewed_claims=[0, 1])
    old_revision = app.revision
    with pytest.raises(ValueError, match='Model generation failed') as error:
        request(app, sources=[{'id': 'log', 'text': 'deployment paused'}])
    assert 'SECRET' not in str(error.value)
    assert app.revision == old_revision + 1
    assert app.remaining == 1
    assert not app.incident.accepted
    assert app.state()['validation']['claims'] == []
    assert app.state()['validation']['sources'][0]['text'] == 'deployment paused'
    with pytest.raises(ValueError, match='missing or blocked'):
        request(app, 'export', reviewer='Reviewer', reviewed_claims=[])
    state = request(app, sources=[{'id': 'log', 'text': 'deployment paused'}])
    assert state['revision'] == old_revision + 2
    assert state['remaining_generations'] == 0
    assert state['mode'] == 'Live model draft — test-model'
    assert request(app, 'export', reviewer='Reviewer', reviewed_claims=[0])['status'] == 'accepted'
    request(app, 'reset')
    with pytest.raises(ValueError, match='limit reached'):
        request(app, sources=[{'id': 'log', 'text': 'deployment paused'}])
    assert len(calls) == 2
    assert calls[0]['max_tokens'] == 2048


def test_live_generation_limits():
    for limit in (0, 11):
        with pytest.raises(ValueError):
            ReviewApp(max_generations=limit)
