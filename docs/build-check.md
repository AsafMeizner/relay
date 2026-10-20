# Local distribution verification — 2026-10-18

Verified commit 3d70ba88376c with a clean working tree. Two consecutive builds produced byte-identical dist/relay-3d70ba88376c.zip files (17 committed source/documentation files).

SHA-256: 1c39e37c26d08667887d68fc5bd5f362e45604a83207dab5cfc98012ccbb6840

Safe relative ZIP paths checked. Extracted into a temporary directory with PYTHONPATH cleared; the offline CLI completed successfully. A new HTTP server from that extraction returned HTTP 200 for /, /api/state, /app.js and /style.css and shut down cleanly.

The first HTTP smoke check used incorrect /static/ asset URLs and returned 404; corrected to the actual routes above, then all checks passed. No application change was needed.

This verifies the offline distribution and fresh application server, not the full video launcher, visual quality, live inference or public availability. The archive predates this document and must be regenerated from the final audited commit before publication. No publication or model calls occurred.
