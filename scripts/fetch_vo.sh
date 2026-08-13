#!/usr/bin/env bash
# Download the rendered VO for "A Generous Offer" into ./lines, then assemble.
# Run from the repo root on a machine that can reach the Higgsfield CDN.
set -euo pipefail
OUT="${1:-lines}"
mkdir -p "$OUT"
tail -n +4 scripts/generous_offer_vo_jobs.txt | while IFS='|' read -r idx spk job url; do
  printf -v f '%s/%02d.wav' "$OUT" "$idx"
  curl -fsSL -o "$f" "$url" && echo "  $f  <- $spk"
done
echo
echo "fetched $(ls "$OUT" | wc -l) lines into $OUT/"
echo "now run:"
echo "  python assemble_dialogue.py $OUT -m scripts/generous_offer_lines.txt -o assembled/"
