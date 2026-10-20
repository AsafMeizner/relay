# Relay — submission narrative draft

Not submitted. Replace pending integration and public links only after verifica# Relay — submission draft

Not ready for publication: human review, final video, distribution and owner eligibility approval remain pending.

## Inspiration

Incident handoffs often mix observations, interpretations and proposed actions. A polished summary can hide where its claims came from. Relay makes the evidence and review step visible before a handoff can be accepted.

## What it does

Relay turns incident sources into a draft with source-linked claims. Every factual claim must cite an exact excerpt from a known source. Missing or fabricated excerpts block acceptance. A reviewer inspects the full sources, reviews every claim, and exports an accepted JSON handoff. Editing sources creates a new revision and clears previous reviews. Suggested actions are never executed.

Exact quotation matching establishes provenance, not truth. A misleading interpretation can quote a real source; the reviewer remains responsible for assessing it.

## How it is built

Python standard-library application with a local browser interface and an OpenAI-compatible model client. The default demonstration uses synthetic fixtures and deterministic extraction without network requests. Explicit live mode supports bounded generation attempts, capped output and failure recovery. The local server checks Host, Origin, session and draft revision; it is a development server with in-memory state and self-reported reviewer identity.

Nebius Token Factory integration was exercised on October 19 with nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B. Three real smoke requests completed in 2.73–4.31 seconds and passed local structure/citation checks; all drafts remained unaccepted. Agent inspection found omitted timestamps and a redundant question. A bounded real-browser retry completed in 4.343 seconds with four unreviewed claims, no automatic acceptance and export disabled. A preceding verification attempt failed after initiating a request; its response was not captured. Human semantic review remains pending; actual provider cost is unmeasured. See docs/browser-verification-2026-10-19.md. See docs/live-results-2026-10-19.md for genuine tooling feedback and limitations.

## What we verified

Latest verification recorded twenty Python tests plus nineteen subtests passing; four browser/live guard tests also passed before the bounded provider retry. Browser coverage includes review/export and failure/retry flows. Ten hand-authored offline evaluation cases matched their expected deterministic guard behavior. Seven invalid-evidence cases blocked acceptance; all ten required explicit review. Exact but misleading quotations demonstrate the boundary of these checks. These results do not measure model quality, prompt-injection resistance or time savings.

A source test build was verified through checksum validation, clean extraction, offline CLI startup, browser HTTP response and byte-identical rebuilding from the same commit. Public distribution remains pending.

## Intended impact

Designed for a person handing an incident to the next responder: inspect the evidence, identify uncertainty and leave a reviewable artifact. The proposed benefit is easier verification of handoff claims. There are no measured customer outcomes, adoption figures or time-saving estimates yet.

## Challenges and lessons

A quotation can be valid while the accompanying conclusion is wrong. Relay therefore separates mechanical citation checks from human judgment. Regeneration also invalidates previous acceptance, so review cannot silently carry over to changed evidence. Provider failures clear the draft while preserving edited sources for a bounded retry.

## Next steps

Complete human semantic review, obtain user feedback and investigate authenticated review and durable audit storage before considering production use.

## Submission fields still pending

- Human semantic review; preserve documented model limitations and failed-attempt history.
- Owner-approved public MIT repository and final source test-build URL/checksum.
- Public YouTube demonstration under three minutes showing the actual final build.
- Final testing instructions checked against the published artifact.
- Owner eligibility/conflict affirmations and submission approval.

Judge walkthrough: docs/judge-walkthrough.md. Distribution procedure: docs/distribution.md. Full requirements and deadline: docs/hackathon-readiness.md.
