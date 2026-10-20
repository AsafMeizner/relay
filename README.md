# Relay

Evidence-linked incident handoffs with explicit human review. Relay turns incident notes and logs into a draft whose factual claims carry exact source excerpts. Missing sources and fabricated excerpts block acceptance. Matching excerpts establish provenance, not truth: a named reviewer must assess every claim before accepting a handoff. Suggested actions are never executed.

Status: local prototype submitted to the Nebius x NVIDIA Global AI Hackathon. Real Nebius Token Factory + NVIDIA Nemotron-3-Nano generation was exercised October 19 (three smoke requests and one bounded browser retry); outputs were checked by an agent against synthetic sources, not independently validated by a human. No measured time savings and no production-readiness claim.

## Run locally

Python 3.10+; the application uses only the standard library. From this directory:

```bash
python3 -m relay
```

This prints a clearly labeled offline fixture, its sources, review requirements and an unaccepted draft. It makes no network requests and requires no key.

## Live model draft

The client uses the OpenAI-compatible chat completions interface. Set these environment variables privately; never commit keys:

- `LLM_PROVIDER=nebius`
- `NEBIUS_API_KEY`: your Token Factory key
- `RELAY_MODEL`: an exact available NVIDIA Nemotron model ID verified against your provider's model listing
- `RELAY_BASE_URL=https://api.tokenfactory.nebius.com/v1` (default)

Then run `python3 -m relay --live`. This sends the built-in synthetic incident sources to your configured model provider and may consume credits. Three live smoke responses and a bounded browser retry are documented in docs/live-results-2026-10-19.md and docs/browser-verification-2026-10-19.md. Non-Nebius compatible providers use `OPENAI_API_KEY` with an explicitly configured `RELAY_BASE_URL` and `RELAY_MODEL`; Gemini-specific integration is not implemented.

## Browser review demo

Run `python3 -m relay.web`, then open http://127.0.0.1:8765 . This local browser demo uses synthetic offline fixtures and makes no AI calls. Inspect all three sources, enter a reviewer name, review both claims, and export the accepted JSON handoff. The fabricated-excerpt example blocks export; resetting a draft clears earlier reviews.

The server binds only to loopback, validates Host and Origin, and requires a local session token and current draft revision. Reviewer names are self-reported; state exists only in memory and resets when the process restarts. Do not expose this development server publicly.

## Review API

`Incident.draft(client)` invalidates earlier acceptance, generates a draft and validates citation excerpts. `Incident.accept(reviewer='Name', reviewed_claims=[0, 1, ...])` requires a named reviewer and every claim index, and rejects blocked drafts. This is a local workflow primitive, not authenticated human identity verification. The CLI deliberately leaves drafts unaccepted.

Source content and model output are untrusted. Exact substring checks do not detect misleading context, unsupported inferences or prompt injection reliably. Reviewers must inspect the full sources, uncertainty and proposed actions. Use synthetic data for evaluation; there is no production access control or persistence layer yet.

## Tests

Install development dependencies with `python3 -m pip install pytest playwright` and `python3 -m playwright install chromium`, then run:

```bash
python3 -m pytest tests -q
```

The tests cover fabricated excerpts, unknown sources, malformed citations, duplicate sources, explicit review, regeneration and invalid model responses. A real Chromium test exercises source inspection, review and export, blocked evidence, and server enforcement when the button is bypassed. Tests use fake transports and consume no API credits.

## Measured guard evaluation

Run `python3 scripts/evaluate_guards.py` to reproduce the deterministic results in [docs/guard-evaluation.json](docs/guard-evaluation.json). On October 18, 2026, all 10 hand-authored cases matched their expected guard behavior, with zero model calls. Seven invalid-evidence cases blocked acceptance: fabricated quotes, unknown sources, missing citations, empty quotes, malformed citations, mixed valid/invalid citations and missing claim text. All 10 cases rejected acceptance without explicit review.

The other three cases demonstrate the boundary: exact quotes pass provenance checks, including quotes attached to misleading claims or containing source instructions. A reviewer can accept these cases. This measures deterministic guard behavior, not model quality, semantic correctness or prompt-injection resistance. The sample is small and hand-authored; no accuracy or time-saving estimate follows from it.

## Judge experience

Follow [docs/judge-walkthrough.md](docs/judge-walkthrough.md) for a two-minute offline walkthrough (no key, no account, no inference). Live generation is available through the CLI and the explicitly enabled local server. A downloadable source test build with checksum is described in [docs/distribution.md](docs/distribution.md); it includes the tests. Rules and submission notes: docs/hackathon-readiness.md.

## License

MIT. See LICENSE.

Browser source editing: edit the synthetic reports and choose “Regenerate from edited sources”. Offline extraction creates one verbatim attributed claim per source, without an AI call or causal inference. Regeneration creates a new revision and clears all claim reviews; edited sources disable export until regenerated. To enable browser model generation after credits are authorized, use the same private provider configuration and run `python3 -m relay.web --live --max-generations 3`. Each attempt, including failures, consumes one of the session’s bounded attempts (1–10). Output is capped at 2048 tokens per request; this is not a dollar budget. Resetting fixtures does not replenish attempts. Failed generation invalidates previous acceptance, clears the draft and preserves edited sources for retry; provider error details are hidden. Default browser mode remains offline. Actual provider cost is unmeasured; no further calls are needed for the final video.
