#!/usr/bin/env bash
set -euo pipefail

root="${1:-.}"
port="${ZENN_PREVIEW_PORT:-8010}"
tmp="${RUNNER_TEMP:-/tmp}/zenn-render-$$"
mkdir -p "$tmp"
log="$tmp/preview.log"
catalog="$tmp/articles.json"

(
  cd "$root"
  npx --yes zenn-cli@latest preview --no-watch --port "$port" >"$log" 2>&1 &
  server_pid=$!
  trap 'kill "$server_pid" 2>/dev/null || true; rm -rf "$tmp"' EXIT

  for _ in {1..10}; do
    if curl --fail --silent --max-time 2 \
      "http://127.0.0.1:${port}/api/articles?sort=system" >"$catalog"; then
      break
    fi
    kill -0 "$server_pid" 2>/dev/null || { cat "$log"; exit 1; }
    sleep 1
  done
  test -s "$catalog" || { cat "$log"; exit 1; }

  python - "$catalog" "$port" <<'PY'
import json
import sys
from pathlib import Path
from urllib.request import urlopen

articles = json.loads(Path(sys.argv[1]).read_text())["articles"]
port = sys.argv[2]
errors = []
for article in articles:
    slug = article["slug"]
    with urlopen(f"http://127.0.0.1:{port}/api/articles/{slug}", timeout=5) as response:
        body = json.load(response)["article"].get("bodyHtml") or ""
    if "data-body-error" in body:
        errors.append(f"{slug}: renderer emitted data-body-error")
if errors:
    raise SystemExit("\n".join(errors))
print(f"ZENN_RENDER_PASS: rendered {len(articles)} articles")
PY
)
