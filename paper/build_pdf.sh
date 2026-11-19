#!/usr/bin/env bash
# Build paper/manuscript.pdf from paper/manuscript.md (pandoc -> HTML -> headless Chromium).
# Set CHROME to a Chrome/Chromium binary if it is not found automatically.
set -euo pipefail
cd "$(dirname "$0")"
CHROME="${CHROME:-$(command -v chromium || command -v chromium-browser || command -v google-chrome || ls /opt/pw-browsers/chromium-*/chrome-linux64/chrome 2>/dev/null | head -1)}"
pandoc manuscript.md --standalone --embed-resources --css manuscript.css \
  --metadata pagetitle="Note 1 manuscript" -o manuscript.html
"$CHROME" --headless --no-sandbox --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$PWD/manuscript.pdf" "file://$PWD/manuscript.html" 2>/dev/null
rm -f manuscript.html
echo "Saved paper/manuscript.pdf"
