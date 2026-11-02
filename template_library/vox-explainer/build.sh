#!/usr/bin/env bash
# vox-explainer — one-command build. Edit content.json, then run:  ./build.sh
#   ./build.sh                      # uses content.json  -> out/final.mp4
#   ./build.sh content.en.json      # another content file
#   TTS=none ./build.sh             # skip narration (visuals + score only)
#   TTS=edge ./build.sh             # fast free TTS instead of local VoxCPM
#   SCORE=false ./build.sh          # no background score
set -e
cd "$(dirname "$0")"
CONTENT="${1:-content.json}"
OUT="${2:-out}"

PY="${PYTHON:-python3}"
if [ -x "../../.venv/bin/python" ]; then PY="../../.venv/bin/python"; fi

echo "[1/2] audio + timing  ($CONTENT)"
$PY build_audio.py "$CONTENT" "$OUT"

echo "[2/2] render video"
node render.mjs "$CONTENT" "$OUT"

echo "done -> $OUT/final.mp4"
