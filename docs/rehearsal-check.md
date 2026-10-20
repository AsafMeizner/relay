# Offline rehearsal verification — 2026-10-18

The detached render completed successfully. Report: 108.4 seconds, 1920×1080 H.264 at 30 fps, stereo AAC at 48 kHz, 37.7 MB, −14.1 LUFS. Output remains local at /workspace/relay-demo-rehearsal/final.mp4.

One warning: `zoom at 10.23s moved clear of a card`. All seven requested zooms were applied. This report verifies technical properties only. Contact sheet and individual frames have NOT been visually inspected; no visual-quality approval is claimed. Do not send this synthetic offline rehearsal as the final submission video.

Validated demo/render-rehearsal.sh with bash -n. Its occupied-port refusal was exercised against the running local demo server: exited before recording with the intended message, and the existing server continued returning HTTP 200. An initial test attempted to reserve the same port and failed because it was already occupied; no server was stopped.

Repository tests: python3 -m pytest tests -q — 17 passed in 2.93 seconds.

Next: inspect frames using an available image-viewing capability, resolve any visual issues, and validate the full fresh-server recording path. Final video still requires verified live Nebius/Nemotron integration.

## Visual check of contact sheet (2026-10-19, human-style review of 12 frames)

- Flow reads clearly: load draft, per-claim review, fabricated evidence blocked (red card), source edit, regenerate, accept.
- Cursor is drawn and tracks the controls.
- Issues: zoom frames 2, 4 and 7 crop text at the left edge (e.g. "ndoff", "don you can trace"); fix by choosing zoom targets that keep the whole heading or card in view. Text in the small unzoomed frames is hard to read, so the final cut should zoom more on the review cards.
- Closing cards are long (about 19 s); shorten.

## Second rehearsal (2026-10-19)

/workspace/relay-demo-rehearsal2/final.mp4: 101.7 s, 36.8 MB (down from 108.4 s). Contact sheet reviewed: text readable in zooms, blocked-evidence card and accept button fully visible. Remaining: some zoom frames still crop one side of wide panels; one warning "zoom at 10.26s moved clear of a card". Still synthetic/offline, not the final video; the final cut needs the live Nebius run.
