#!/usr/bin/env bash
# Stage the static export for the Worker: frontend/out is copied to
# worker/dist/image-annotation/, so asset paths match the public URLs
# (Next's basePath prefixes the URLs, not the files) and the asset handler
# serves them directly, with no Worker script invoked per request.
# Usage: (cd frontend && pnpm run build:static) && bash worker/stage.sh
set -euo pipefail
cd "$(dirname "$0")"
[ -f ../frontend/out/index.html ] || { echo "frontend/out is missing; build it first"; exit 1; }
rm -rf dist
mkdir -p dist
cp -R ../frontend/out dist/image-annotation
# Build helpers that land in out/ only because they live in public/
printf '%s\n' 'copy-static-assets.sh' > dist/.assetsignore
echo "staged $(find dist/image-annotation -type f | wc -l | tr -d ' ') files in worker/dist/image-annotation"
