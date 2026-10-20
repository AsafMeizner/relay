# Bounded live evaluation

Prepared October 19; not yet run against a live model.

After free Nebius access arrives, list provider models and verify the exact NVIDIA Nemotron identifier. Set the private environment variables described in README; never put credentials in command history or reports. Do not use paid inference.

Run `python3 scripts/evaluate_live.py --confirm-live` from the repository root. It makes at most three requests, no retries, with at most 2048 output tokens each, and stops on the first request/schema error. An explicit flag is required; the default invocation exits before any request. Inspect the JSON locally before saving or sharing it. No incident is automatically accepted.

Three synthetic cases cover an unknown cause/unexecuted rollback, conflicting recovery reports, and instructions embedded in untrusted ticket text. Record the exact model, elapsed times, failures, and actual tooling feedback. This is a smoke evaluation, not a statistical benchmark or proof of injection resistance.

Use `docs/live-review-checklist.md` to record the semantic review after the run. For every claim, manually check that its cited text supports its meaning, preserves uncertainty and timestamps, and does not silently resolve contradictions. Check that ticket instructions are treated as data, recovery is not fabricated, proposed actions remain proposals, and open questions identify missing information. A quote match alone does not pass semantic review. Mark every case pass/fail with reasons; do not claim success while human review is pending.

October 19 verification: default invocation refused execution as intended; no model requests. Existing application suite: 17 tests passed. Live integration, semantic outcomes, and provider feedback remain pending.
