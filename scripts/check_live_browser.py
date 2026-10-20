"""One-request browser smoke check; explicit opt-in, never accepts a live draft."""
import argparse
import json
import os
import threading
import time
from http.server import HTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from relay.web import ReviewApp, handler_for
from relay.workflow import ModelClient


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--confirm-live', action='store_true')
    args = parser.parse_args()
    if not args.confirm_live:
        parser.error('Requires --confirm-live; consumes provider credits')
    if os.environ.get('LLM_PROVIDER') != 'nebius':
        parser.error('Nebius provider required')
    client = ModelClient('https://api.tokenfactory.nebius.com/v1', os.environ['NEBIUS_API_KEY'],
                         'nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B')
    app = ReviewApp(client, 1)
    server = HTTPServer(('127.0.0.1', 0), handler_for(app))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    result = {'model': client.model, 'request_limit': 1, 'human_semantic_review': 'pending',
              'cost_usd': None, 'cost_note': 'Not measured; owner reports $1 trial limit and paid usage disabled.'}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, chromium_sandbox=False)
            page = browser.new_page()
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto(f'http://127.0.0.1:{server.server_port}')
            page.wait_for_selector('.review')
            assert page.locator('#export').is_disabled()
            start = time.monotonic()
            page.locator('#generate').click()
            # Locator polling respects the app's CSP; no evaluated wait predicate.
            expect(page.locator('#generate')).to_be_enabled(timeout=70000)
            expect(page.locator('#mode')).to_contain_text('0 live attempts remaining')
            result['latency_seconds'] = round(time.monotonic() - start, 3)
            result['state'] = app.state()
            result['sources'] = [{'id': s.id, 'text': s.text} for s in app.incident.sources]
            assert app.remaining == 0
            assert not app.incident.accepted
            assert page.locator('#export').is_disabled()
            assert page.locator('.review:checked').count() == 0
            assert not errors
            result['browser_checks'] = 'passed: one attempt, no automatic review or acceptance, export disabled, no page errors'
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
    target = Path('docs/live-browser-result-2026-10-19.json')
    target.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'evidence': str(target), 'mode': app.mode, 'latency_seconds': result['latency_seconds'], 'accepted': app.incident.accepted}))


if __name__ == '__main__':
    main()
