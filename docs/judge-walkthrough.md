# Two-minute judge walkthrough

Status: local synthetic demo, October 18, 2026. This walkthrough makes no inference calls. This offline walkthrough is separate from the successful bounded live browser check documented in docs/browser-verification-2026-10-19.md. Three separate Nebius/NVIDIA smoke requests succeeded October 19; see docs/live-results-2026-10-19.md. Use synthetic data only. Do not expose the development server publicly.

## Start

From the repository root run `python3 -m relay.web`, then open http://127.0.0.1:8765 . No key or account is needed. The header labels the offline mode. Restarting the server clears its in-memory state.

## 0:00–0:45 — Trace and accept

1. Choose **Load clean draft**. Read the three original sources and the excerpts alongside both claims.
2. Notice that deployment preceded the error observation, but the draft does not assert a proven cause. Rollback was requested; completion is unconfirmed.
3. Enter a reviewer name. Review each claim using its checkbox, then choose **Accept & download handoff**.
4. Inspect the downloaded JSON for the accepted handoff, reviewer, original sources and revision. Reviewer identity is self-reported, not authenticated. Suggested actions have not run.

Expected result: export requires the name and every claim review. Exact excerpts establish provenance; the human still decides whether the claim is supported in context.

## 0:45–1:15 — Fabricated evidence blocks export

1. Choose **Try fabricated evidence**.
2. Inspect the rollback claim: its proposed quote says `Rollback completed.`, while the original report says `Completion is not confirmed.`
3. Confirm the citation is blocked and acceptance stays unavailable.

Expected result: fabricated evidence cannot be accepted even if all review boxes are checked. Server-side validation also enforces this requirement; disabling a browser button is not the only guard.

## 1:15–2:00 — New evidence invalidates old review

1. Choose **Load clean draft**, enter a name and check the claim reviews.
2. Edit the on-call source to append `14:12 rollback completion confirmed by on-call.` Export becomes unavailable while the sources are edited.
3. Choose **Regenerate from edited sources**. In offline mode this produces one attributed verbatim claim per source, not a model-generated summary.
4. Confirm earlier reviews are cleared. Inspect the new source/claim, review every claim again, then export.

Expected result: a revised draft cannot inherit acceptance from the previous revision. Offline extraction reports the text; it does not resolve contradictions or verify the report's truth.

## Evidence and boundaries

Run `python3 scripts/evaluate_guards.py` for the 10-case deterministic guard evaluation; inspect `docs/guard-evaluation.json`. Seven invalid-evidence cases block acceptance. Three provenance-valid cases can be accepted after review, including misleading semantics and quoted source instructions. All 10 reject unreviewed acceptance. This is not a model benchmark or evidence of prompt-injection resistance.

The automated suite includes Chromium review/export, edited-source review reset, fabricated-evidence blocking, bypass rejection, and simulated generation failure/retry. Live provider quality, actual costs, incident response time savings and production suitability remain unmeasured.

## Recorded live verification

Three separate smoke requests and one successful real-browser retry used the verified nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B model. The browser retry completed in 4.343 seconds with all four claims unreviewed, no automatic acceptance and export disabled. A preceding verification attempt failed after initiating a request; its response was not captured. See docs/browser-verification-2026-10-19.md and the saved JSON response. Actual provider cost is unmeasured; human semantic review remains pending. Do not rerun requests merely for cleaner output. The owner reports a $1 trial limit and paid usage disabled. Attempt limits are not dollar budgets.
