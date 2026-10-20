# Source test build

The downloadable source ZIP runs locally with Python 3.10+ and no runtime packages or credentials. It is a local test build, not a hosted service. Final public download URL is pending owner-approved publication; availability alone does not establish organizer acceptance of this format.

## Build from a clean checkout

Run `python3 scripts/build_distribution.py`. The script packages committed application, documentation and scripts plus README and MIT LICENSE. It refuses uncommitted changes. Output goes to `dist/relay-<commit>.zip` with a SHA-256 sidecar; BUILD.txt identifies the complete source commit. Tests are bundled; running them needs pytest and Playwright (see README).

## Verify and run

Download the ZIP and its `.zip.sha256` sidecar together. In their directory run `sha256sum -c relay-<commit>.zip.sha256`, replacing `<commit>` with the filename's identifier. Extract the ZIP, enter its `relay` directory and run:

```bash
python3 -m relay
python3 -m relay.web
```

The first command completes with an offline, unaccepted synthetic handoff. The second stays running; open http://127.0.0.1:8765 and follow docs/judge-walkthrough.md. Stop with Ctrl+C. No inference calls occur in default mode. Do not expose this development server publicly. Live mode requires private provider configuration and authorized credits as described in README.md.

Before submission, regenerate the archive from the final audited commit, verify a clean extraction, and publish the exact final artifact through owner approval. Keep that build available through December 15, 2026. Record the final public URL and checksum in the submission; the local artifact is not yet a publicly accessible submission deliverable.
