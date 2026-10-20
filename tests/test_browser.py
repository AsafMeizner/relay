"""Real browser integration checks; requires Playwright Chromium."""
import json
import threading
from http.server import HTTPServer
from playwright.sync_api import sync_playwright
from relay.web import ReviewApp, handler_for


def test_review_export_and_server_guards():
    app = ReviewApp()
    server = HTTPServer(('127.0.0.1', 0), handler_for(app))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, chromium_sandbox=False)
            page = browser.new_page(accept_downloads=True)
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto(f'http://127.0.0.1:{server.server_port}')
            page.wait_for_selector('.review')
            assert page.locator('#sources article').count() == 3
            assert page.locator('#export').is_disabled()
            page.locator('#reviewer').fill('Test reviewer')
            page.locator('.review').nth(0).check()
            assert page.locator('#export').is_disabled()
            # Bypassing the button must not bypass the server's review guard.
            def export(indices):
                return page.evaluate('''async indices => {
                  const s = await (await fetch('/api/state')).json();
                  const r = await fetch('/api/action', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({action:'export',token:s.token,revision:s.revision,reviewer:'Test reviewer',reviewed_claims:indices})});
                  return {status:r.status, body:await r.json()};
                }''', indices)
            assert export([0])['status'] == 400
            page.locator('.review').nth(1).check()
            with page.expect_download() as info:
                page.locator('#export').click()
            handoff = json.loads(open(info.value.path()).read())
            assert handoff['status'] == 'accepted'
            assert len(handoff['sources']) == 3
            assert 'provenance' in handoff['provenance_notice']
            page.locator('#blocked').click()
            page.wait_for_selector('article.blocked')
            assert page.locator('.review:checked').count() == 0
            assert page.locator('#export').is_disabled()
            assert export([0, 1])['status'] == 400
            page.locator('#reset').click()
            page.locator('article.blocked').wait_for(state='detached')
            assert page.locator('.review:checked').count() == 0
            assert page.locator('#export').is_disabled()
            page.locator('.review').nth(0).check()
            page.locator('.review').nth(1).check()
            old_revision = app.revision
            page.locator('#sources textarea').nth(0).fill('14:12 deployment paused; cause unknown.')
            page.locator('#reviewer').fill('Another reviewer')
            assert page.locator('#export').is_disabled()
            page.locator('#generate').click()
            page.locator('.review').nth(2).wait_for()
            assert app.revision == old_revision + 1
            assert not app.incident.accepted
            assert page.locator('.review:checked').count() == 0
            assert page.locator('#export').is_disabled()
            assert 'deployment paused' in page.locator('#claims').inner_text()
            assert export([0, 1])['status'] == 400
            assert not errors
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_live_browser_failure_preserves_sources_and_retries():
    from relay.workflow import ModelClient

    calls = []

    def transport(payload):
        calls.append(payload)
        if len(calls) == 1:
            raise RuntimeError('SECRET provider detail')
        brief = {'claims': [{'text': 'Deployment paused.', 'citations': [
            {'source_id': 'deployment', 'quote': 'deployment paused'}]}],
            'open_questions': [], 'suggested_actions': []}
        return {'choices': [{'message': {'content': json.dumps(brief)}}]}

    app = ReviewApp(ModelClient('https://example.invalid/v1', 'fake', 'test-model', transport), 2)
    server = HTTPServer(('127.0.0.1', 0), handler_for(app))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, chromium_sandbox=False)
            page = browser.new_page(accept_downloads=True)
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto(f'http://127.0.0.1:{server.server_port}')
            page.wait_for_selector('.review')
            page.locator('#reviewer').fill('Retry reviewer')
            for checkbox in page.locator('.review').all():
                checkbox.check()
            with page.expect_download():
                page.locator('#export').click()
            assert app.incident.accepted
            page.locator('#sources textarea').nth(0).fill('14:12 deployment paused; cause unknown.')
            page.locator('#generate').click()
            page.locator("#status", has_text="sources preserved").wait_for()
            assert page.locator('#sources textarea').nth(0).input_value() == '14:12 deployment paused; cause unknown.'
            assert page.locator('.review').count() == 0
            assert page.locator('#export').is_disabled()
            assert page.locator('#generate').is_enabled()
            assert '1 live attempts remaining' in page.locator('#mode').inner_text()
            assert 'SECRET' not in page.locator('body').inner_text()
            assert not app.incident.accepted
            page.locator('#generate').click()
            page.wait_for_selector('.review')
            assert page.locator('.review:checked').count() == 0
            assert page.locator('#export').is_disabled()
            assert '0 live attempts remaining' in page.locator('#mode').inner_text()
            page.locator('.review').check()
            with page.expect_download() as info:
                page.locator('#export').click()
            handoff = json.loads(open(info.value.path()).read())
            assert handoff['status'] == 'accepted'
            assert handoff['revision'] == 3
            assert handoff['sources'][0]['text'] == '14:12 deployment paused; cause unknown.'
            page.locator('#generate').click()
            page.locator("#status", has_text="limit reached").wait_for()
            assert len(calls) == 2
            assert not errors
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
