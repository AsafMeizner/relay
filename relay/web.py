"""Loopback-only review UI. Run: python3 -m relay.web."""
import argparse
import json
import os
import secrets
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from relay.evidence import Source
from relay.workflow import Incident, ModelClient


def fixture(blocked=False):
    sources = [Source('deployment', '14:02 deployment v42 started.'), Source('monitor', '14:05 checkout error rate 12%. At 14:09 error rate 3%.'), Source('oncall', '14:06 rollback requested. Completion is not confirmed.')]
    brief = {'claims': [
        {'text': 'Checkout errors were observed after deployment began; cause is unconfirmed.', 'citations': [{'source_id': 'deployment', 'quote': sources[0].text}, {'source_id': 'monitor', 'quote': '14:05 checkout error rate 12%.'}]},
        {'text': 'Rollback completion is unconfirmed.', 'citations': [{'source_id': 'oncall', 'quote': 'Rollback completed.' if blocked else 'Completion is not confirmed.'}]}],
        'open_questions': ['Did rollback complete?', 'What caused the checkout errors?'],
        'suggested_actions': ['Ask the incident commander to verify rollback status.']}
    incident = Incident(sources)
    incident.draft(ModelClient('https://example.invalid/v1', '', 'fixture', lambda _: {'choices': [{'message': {'content': json.dumps(brief)}}]}))
    return incident


class ReviewApp:
    def __init__(self, client=None, max_generations=3):
        if not 1 <= max_generations <= 10:
            raise ValueError("Generation limit must be 1–10")
        self.client = client
        self.remaining = max_generations
        self.mode = "Synthetic offline fixture — no AI call"
        self.token = secrets.token_urlsafe(32)
        self.incident = fixture()
        self.revision = 1

    def state(self):
        return {'revision': self.revision, 'mode': self.mode, 'remaining_generations': self.remaining if self.client else None, 'brief': self.incident.brief or {'open_questions': [], 'suggested_actions': []}, 'validation': self.incident.validation or {'sources': [{'id': s.id, 'text': s.text} for s in self.incident.sources], 'claims': [], 'blocked': 1}}

    def action(self, body):
        if body.get('token') != self.token:
            raise ValueError('Invalid local session token')
        if body.get('revision') != self.revision:
            raise ValueError('Draft changed; reload and review again')
        if body.get('action') == 'generate':
            rows = body.get('sources')
            if not isinstance(rows, list) or not 1 <= len(rows) <= 8:
                raise ValueError('Provide 1–8 sources')
            sources = []
            for row in rows:
                if not isinstance(row, dict) or not isinstance(row.get('id'), str) or not isinstance(row.get('text'), str):
                    raise ValueError('Each source needs text and an ID')
                if not row['id'].strip() or len(row['id']) > 80 or not 1 <= len(row['text'].strip()) <= 2000:
                    raise ValueError('Source ID or text is empty or too long')
                sources.append(Source(row['id'].strip(), row['text']))
            incident = Incident(sources)
            if self.client:
                if self.remaining <= 0:
                    raise ValueError('Live generation limit reached; restart server to authorize another session')
                # Failed requests count too. Invalidate old export before attempting inference.
                self.remaining -= 1
                self.revision += 1
                self.incident = incident
                self.mode = 'Model generation failed — no draft available'
                try:
                    incident.draft(self.client)
                except Exception:
                    # Provider errors may include sensitive details; never return them to the UI.
                    raise ValueError('Model generation failed; sources preserved. Retry if attempts remain.') from None
                self.mode = 'Live model draft — ' + self.client.model
            else:
                # Offline extraction is deterministic and makes no inference request.
                brief = {'claims': [{'text': 'Source ' + source.id + ' reports: ' + source.text,
                                    'citations': [{'source_id': source.id, 'quote': source.text}]}
                                   for source in sources],
                         'open_questions': ['Which reports are independently verified?', 'What remains unresolved?'],
                         'suggested_actions': ['Have the incident commander verify these reports before acting.']}
                incident.draft(ModelClient('https://example.invalid/v1', '', 'fixture',
                               lambda _: {'choices': [{'message': {'content': json.dumps(brief)}}]}))
            self.incident = incident
            if not self.client:
                self.revision += 1
            return self.state()
        if body.get('action') == 'reset':
            self.incident = fixture(body.get('blocked') is True)
            self.mode = 'Synthetic offline fixture — no AI call'
            self.revision += 1
            return self.state()
        if body.get('action') != 'export':
            raise ValueError('Unknown action')
        reviewed = body.get('reviewed_claims')
        if not isinstance(reviewed, list) or any(type(i) is not int for i in reviewed):
            raise ValueError('Explicit integer claim indices required')
        result = self.incident.accept(reviewer=body.get('reviewer'), reviewed_claims=reviewed)
        return {**result, 'sources': self.incident.validation['sources'], 'revision': self.revision,
                'provenance_notice': 'Exact excerpts establish provenance only, not factual truth.', 'mode': self.mode}


def handler_for(app):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def reply(self, status, data, content_type='application/json'):
            raw = data.encode() if isinstance(data, str) else json.dumps(data).encode()
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(raw)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(raw)

        def valid_host(self):
            return self.headers.get('Host') == f'127.0.0.1:{self.server.server_port}'

        def do_GET(self):
            if not self.valid_host():
                return self.reply(403, {'error': 'Loopback Host required'})
            if self.path == '/api/state':
                return self.reply(200, {**app.state(), 'token': app.token})
            files = {'/': ('index.html', 'text/html; charset=utf-8'), '/app.js': ('app.js', 'text/javascript; charset=utf-8'), '/style.css': ('style.css', 'text/css; charset=utf-8')}
            if self.path not in files:
                return self.reply(404, {'error': 'Not found'})
            filename, kind = files[self.path]
            return self.reply(200, (Path(__file__).parent / 'static' / filename).read_text(), kind)

        def do_POST(self):
            if not self.valid_host():
                return self.reply(403, {'error': 'Loopback Host required'})
            origin = self.headers.get('Origin')
            if origin and origin != f'http://127.0.0.1:{self.server.server_port}':
                return self.reply(403, {'error': 'Cross-origin request rejected'})
            if self.path != '/api/action':
                return self.reply(404, {'error': 'Not found'})
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 16384:
                    raise ValueError('Invalid request size')
                body = json.loads(self.rfile.read(length))
                if not isinstance(body, dict):
                    raise ValueError('JSON object required')
                result = app.action(body)
                self.reply(200, result)
            except (ValueError, TypeError) as exc:
                self.reply(400, {'error': str(exc)})
    return Handler


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true', help='Enable paid/credit-consuming model generation from browser sources')
    parser.add_argument('--max-generations', type=int, default=3)
    args = parser.parse_args()
    client = None
    if args.live:
        provider = os.environ.get('LLM_PROVIDER', 'nebius')
        key_name = 'NEBIUS_API_KEY' if provider == 'nebius' else 'OPENAI_API_KEY'
        key, model = os.environ.get(key_name), os.environ.get('RELAY_MODEL')
        base = os.environ.get('RELAY_BASE_URL')
        if not key or not model or (provider != 'nebius' and not base):
            parser.error('Live mode requires provider key, RELAY_MODEL and explicit base for alternate providers')
        client = ModelClient(base or 'https://api.tokenfactory.nebius.com/v1', key, model)
    if not 1 <= args.max_generations <= 10:
        parser.error('--max-generations must be 1–10')
    server = HTTPServer(('127.0.0.1', 8765), handler_for(ReviewApp(client, args.max_generations)))
    print('Relay: http://127.0.0.1:8765 (' + ('live model enabled' if client else 'offline fixture') + '; Ctrl+C to stop)', flush=True)
    server.serve_forever()
