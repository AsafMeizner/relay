# Browser verification — October 19, 2026

Command: `python3 -m pytest -q tests/test_browser.py tests/test_web_live.py`
Result: 4 passed in 2.98 seconds; exit 0.

Real Chromium exercised the local interface. Offline review/export guards passed, including server-side rejection of partial review, fabricated citations, and stale reviews after edits. A simulated live transport exercised a failed request followed by recovery: sources remained available, old acceptance was invalidated, provider error details stayed hidden, new claims required fresh review, and the attempt limit prevented further transport calls. These tests make no model-quality claim and used zero provider requests.

## First real-browser attempt: verification failed

The owner confirmed a $1 trial limit with paid usage disabled. The first real-browser attempt initiated one provider request, then the verification script failed because Playwright's `wait_for_function` required evaluation blocked by the app's Content Security Policy. The response, latency, and provider cost were not captured; generation success and browser guard verification remain unverified. This attempt must count in usage history and must not be presented as a passed check. Preserve the app's security policy; replace the check's evaluation with locator-based waiting before any retry.

## Corrected real-browser retry: passed

The check replaced evaluated waiting with Playwright locator assertions, preserving the app's Content Security Policy. Four browser/live guard tests passed before the retry. One bounded real request completed in 4.343 seconds using nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B. The browser reported no page errors, zero remaining attempts, no checked claim reviews, no acceptance and disabled export. Full response and synthetic sources are in live-browser-result-2026-10-19.json.

Four generated claims retained the deployment and monitoring timestamps and the uncertainty about rollback completion. Agent inspection finds each supported by its quoted synthetic source; this is not independent human validation. Open questions and suggested actions are unverified recommendations and never execute. Human semantic review remains pending. This single successful retry is not a quality benchmark. The first failed verification attempt remains part of usage history; its generation outcome was not captured.

The owner reports a $1 trial limit with paid usage disabled. Actual provider cost and credit expiry remain unmeasured. No further provider calls are needed for packaging. Next: final video and distribution packaging, then owner publication/upload approvals and personal eligibility confirmation.
