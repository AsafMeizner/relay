#!/usr/bin/env bash
# Run from any directory. Offline synthetic rehearsal only; not a final entry.
set -euo pipefail
project_dir="$(cd "$(dirname "$0")/.." && pwd)"
output_dir="${1:-/workspace/relay-demo-rehearsal}"
mkdir -p "$output_dir"
cd "$project_dir"
# Refuse an occupied port: recording existing state can misrepresent the demo.
python3 - <<'PY'
import socket
with socket.socket() as sock:
    try:
        sock.bind(('127.0.0.1', 8765))
    except OSError:
        raise SystemExit('Port 8765 is occupied. Stop the existing demo server before recording.')
PY
python3 -m relay.web > "$output_dir/server.log" 2>&1 &
server_pid=$!
trap 'kill "$server_pid" 2>/dev/null || true' EXIT
python3 - <<'PY'
import time
import urllib.request
for attempt in range(50):
    try:
        with urllib.request.urlopen('http://127.0.0.1:8765/', timeout=1) as response:
            if response.status == 200:
                break
    except OSError:
        time.sleep(0.1)
else:
    raise SystemExit('Demo server did not become ready; inspect server.log.')
PY
cd demo
PYTHONPATH=/workspace/.skills/demo-video python3 -m demo_video make storyboard.yaml --out "$output_dir"
