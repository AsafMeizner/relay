# Source distribution license review — October 19, 2026

Scope: tracked Relay source at commit 7d198add8dc8 and the source-only test archive. This is a technical inventory, not legal clearance or verification of sole ownership.

## Findings
- Root LICENSE contains the MIT license and copyright notice for Relay contributors.
- Static import inspection of every Python file found only standard-library modules, local Relay modules, pytest and Playwright. The application runtime itself uses only the Python standard library.
- Development tools installed in the verification environment: pytest 9.1.1 declares MIT; Playwright 1.63.0 declares Apache-2.0. Their installed license texts were inspected. These packages and Chromium are installed separately, not bundled in the source archive. Their own distributions retain their notices; Relay's MIT license does not relicense them.
- No vendored dependency code, tracked binary assets or media were identified in the preceding tracked-file inventory. Git history attributes development to agent identities. That history does not establish legal ownership, employment permission or originality against external works.
- Synthetic incident examples are represented as synthetic throughout the project. No production incident dataset is required.

## Remaining scope and gates
The final MP4 is outside this source review. Its narration, music, fonts and rendering inputs require a separate asset inventory and actual visual inspection before distribution. Do not infer media rights from this source inventory.

The existing owner employment/conflict/ownership confirmation and independent human semantic review remain required before publication. No public release or legal eligibility determination follows from this review. If dependencies, vendored code or media are added to the archive, repeat the inventory and preserve applicable third-party notices.
