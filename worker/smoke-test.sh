#!/usr/bin/env bash
# Smoke test for the frontend Worker: runs it under `wrangler dev` (the real
# local runtime and asset handler, no fake bindings) against the built export
# in frontend/out, and checks the mount.
# Usage: (cd frontend && pnpm run build:static) && bash worker/smoke-test.sh
set -euo pipefail
cd "$(dirname "$0")"
[ -f ../frontend/out/index.html ] || { echo "frontend/out is missing; build it first"; exit 1; }
PORT="${PORT:-8798}"
BASE="http://127.0.0.1:${PORT}"
M="/image-annotation"
LOG="$(mktemp)"

bunx wrangler@4 dev --port "$PORT" --ip 127.0.0.1 >"$LOG" 2>&1 &
PID=$!
trap 'kill "$PID" 2>/dev/null || true; rm -f "$LOG"' EXIT

for _ in $(seq 1 90); do
  curl -s -o /dev/null "$BASE/" && break
  sleep 1
done
curl -s -o /dev/null "$BASE/" || { echo "wrangler dev did not start"; cat "$LOG"; exit 1; }

failures=0
check() { # description expected actual
  if [ "$2" = "$3" ]; then echo "ok   $1"; else echo "FAIL $1 (expected '$2', got '$3')"; failures=$((failures + 1)); fi
}
status() { curl -s -o /dev/null -w '%{http_code}' "$BASE$1"; }
location() { curl -s -o /dev/null -w '%{redirect_url}' "$BASE$1"; }

page="$(curl -s "$BASE$M/")"
check "$M/ serves the page" 200 "$(status "$M/")"
check "page references assets under the mount" yes "$(grep -q "\"$M/_next/" <<<"$page" && echo yes || echo no)"
chunk="$(grep -o "$M/_next/static/chunks/[^\"]*\.js" <<<"$page" | head -1)"
check "a _next chunk from the page is served" 200 "$(status "$chunk")"
check "image-list.json is served" 200 "$(status "$M/image-list.json")"
first_image="$(curl -s "$BASE$M/image-list.json" | grep -o '"[^"]*"' | sed -n 2p | tr -d '"')"
check "a thumbnail is served" 200 "$(status "$M/thumbnails/${first_image}.jpg")"
check "an annotation file is served" 200 "$(status "$M/annotations/nsd/${first_image}_annotations.json")"
check "bare $M redirects" 308 "$(status "$M?x=1")"
check "bare $M keeps the query" "$BASE$M/?x=1" "$(location "$M?x=1")"
check "$M/index.html redirect stays under the mount" "$BASE$M/" "$(location "$M/index.html")"
check "the build helper script is not published" 404 "$(status "$M/copy-static-assets.sh")"
check "path outside the mount is 404" 404 "$(status /hedit/)"

if [ "$failures" -gt 0 ]; then
  echo "$failures check(s) failed"
  exit 1
fi
echo "All frontend Worker checks passed"
