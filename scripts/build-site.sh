#!/usr/bin/env bash
# Build the public site: the marketing page at / and the demo app at /demo/, in site-dist/.
# The demo is built with relative paths, so the site works on any static host and any domain.
# Cloudflare Pages: build command `bash scripts/build-site.sh`, output directory `site-dist`,
# environment variable NODE_VERSION=22.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
out="$root/site-dist"

rm -rf "$out"
mkdir -p "$out"

npm --prefix "$root/web" ci
VITE_SITE_URL=../ VITE_WHATIF_ENABLED=false npm --prefix "$root/web" run build -- --base=./
cp -R "$root/web/dist" "$out/demo"

cp "$root/site/index.html" "$root/site/styles.css" "$root/site/favicon.svg" "$out/"
cp -R "$root/site/images" "$out/images"

echo "Built $out"
