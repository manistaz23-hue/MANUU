#!/usr/bin/env bash
# Assemble one episode from its six generated 10-second blocks.
#
#   bash pipeline/assemble_episode.sh --episode episodes/ep01-chipotle-bowl.json \
#        --blocks build/ep01-chipotle-bowl/clips
#
# Expects blocks named block01.mp4 … block06.mp4 in --blocks.
# Route B: add --voices <dir> holding voice01.wav … voice06.wav; the clips' own audio
# is dropped and the narration is used instead.
#
# Produces out/<id>-<slug>.mp4 — 1080x1920, source fps, H.264 High / yuv420p / AAC 128k,
# audio normalized to -16 LUFS, with the episode's static top caption burned in.

set -euo pipefail

EPISODE=""; BLOCKS=""; VOICES=""; OUTDIR="out"; FONT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --episode) EPISODE="$2"; shift 2 ;;
    --blocks)  BLOCKS="$2";  shift 2 ;;
    --voices)  VOICES="$2";  shift 2 ;;
    --out)     OUTDIR="$2";  shift 2 ;;
    --font)    FONT="$2";    shift 2 ;;
    -h|--help) sed -n '2,14p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

[[ -n "$EPISODE" ]] || { echo "--episode is required" >&2; exit 2; }
[[ -n "$BLOCKS"  ]] || { echo "--blocks is required"  >&2; exit 2; }
[[ -f "$EPISODE" ]] || { echo "no such episode file: $EPISODE" >&2; exit 1; }

for bin in ffmpeg python3; do
  command -v "$bin" >/dev/null || { echo "missing required binary: $bin" >&2; exit 1; }
done
PROBE="$(dirname "$0")/probe.py"

read -r EP_ID EP_SLUG N_BLOCKS <<<"$(python3 -c '
import json,sys
e=json.load(open(sys.argv[1]))
print(e["id"], e["slug"], len(e["blocks"]))' "$EPISODE")"

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# The caption goes through a textfile so colons and apostrophes need no escaping.
python3 -c '
import json,sys
json.dump(None, open("/dev/null","w"))
e=json.load(open(sys.argv[1]))
open(sys.argv[2],"w").write(e["caption"])' "$EPISODE" "$WORK/caption.txt"
CAPTION="$(cat "$WORK/caption.txt")"

# ---- locate the blocks --------------------------------------------------------
declare -a CLIPS=()
for i in $(seq 1 "$N_BLOCKS"); do
  f="$BLOCKS/block$(printf '%02d' "$i").mp4"
  [[ -f "$f" ]] || { echo "missing block: $f" >&2; exit 1; }
  CLIPS+=("$f")
done

# ---- fps comes from the source, never hardcoded -------------------------------
FPS="$(python3 "$PROBE" fps "${CLIPS[0]}")"
echo "  source fps: $FPS"

# ---- pick a font --------------------------------------------------------------
if [[ -z "$FONT" ]]; then
  for candidate in \
    /usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf \
    /usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf \
    /System/Library/Fonts/Supplemental/Arial\ Black.ttf \
    /Library/Fonts/Arial\ Black.ttf ; do
    [[ -f "$candidate" ]] && { FONT="$candidate"; break; }
  done
fi
if [[ -z "$FONT" ]] && command -v fc-match >/dev/null; then
  FONT="$(fc-match -f '%{file}' 'sans:bold' || true)"
fi
[[ -n "$FONT" && -f "$FONT" ]] || {
  echo "no bold font found; pass --font /path/to/a-bold.ttf" >&2; exit 1; }
echo "  caption font: $FONT"

# ---- normalize every block to a common grid before concat ---------------------
# Re-encoding here is deliberate: the blocks come back from generation with slightly
# different timebases, and a stream-copy concat of those produces drift.
: > "$WORK/concat.txt"
idx=0
for clip in "${CLIPS[@]}"; do
  idx=$((idx+1))
  norm="$WORK/norm$(printf '%02d' $idx).mp4"
  if [[ -n "$VOICES" ]]; then
    voice="$VOICES/voice$(printf '%02d' $idx).wav"
    [[ -f "$voice" ]] || { echo "missing voice track: $voice" >&2; exit 1; }
    # The block stays its full length and the take is CENTRED inside it — never the
    # other way round. Trimming video to fit a short take is the "2:00 became 1:35"
    # bug, and stretching the take to fit is worse. If a take is too long for its
    # block, rewrite the line and regenerate it; do not fix it here.
    VDUR="$(python3 "$PROBE" duration "$clip")"
    ADUR="$(python3 "$PROBE" duration "$voice")"
    DELAY_MS="$(python3 -c "
v, a = float('$VDUR'), float('$ADUR')
if a > v: raise SystemExit(f'  FAIL voice$(printf '%02d' $idx).wav is {a:.2f}s, longer than its {v:.2f}s block — rewrite the line')
print(int(max(0.0, (v - a) / 2) * 1000))")"
    echo "    block $(printf '%02d' $idx): ${ADUR}s of voice centred in ${VDUR}s"
    ffmpeg -nostdin -v error -y -i "$clip" -i "$voice" \
      -filter_complex "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=${FPS},setsar=1[v];[1:a]adelay=${DELAY_MS}|${DELAY_MS},apad[a]" \
      -map "[v]" -map "[a]" -t "$VDUR" \
      -c:v libx264 -profile:v high -pix_fmt yuv420p -crf 20 \
      -c:a aac -b:a 128k -ar 44100 -ac 2 "$norm"
  else
    ffmpeg -nostdin -v error -y -i "$clip" \
      -filter_complex "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=${FPS},setsar=1[v]" \
      -map "[v]" -map 0:a? -c:v libx264 -profile:v high -pix_fmt yuv420p -crf 20 \
      -c:a aac -b:a 128k -ar 44100 -ac 2 "$norm"
  fi
  echo "file '$norm'" >> "$WORK/concat.txt"
done

ffmpeg -nostdin -v error -y -f concat -safe 0 -i "$WORK/concat.txt" \
  -c copy "$WORK/joined.mp4"

# ---- burn the static caption plate and normalize loudness ---------------------
# This is a TITLE PLATE, not a speech caption: one line, authored, unchanging.
# Speech captions, if you ever add them, are a separate pass timed from the audio.
#
# Preferred path is a pre-rendered transparent PNG overlaid on the video: identical
# typography on every machine, and it works on ffmpeg builds compiled without
# libfreetype (where drawtext simply does not exist). Falls back to drawtext when
# Pillow is not installed.
mkdir -p "$OUTDIR"
OUT="$OUTDIR/${EP_ID}-${EP_SLUG}.mp4"

CAPTION_PNG=""
if python3 -c "import PIL" 2>/dev/null; then
  CAPTION_PNG="$WORK/caption.png"
  python3 "$(dirname "$0")/make_caption.py" "$CAPTION" "$CAPTION_PNG" \
    --width 1080 --height 1920 --font "$FONT"
elif ! ffmpeg -hide_banner -filters 2>/dev/null | grep -q " drawtext "; then
  echo "  this ffmpeg has no drawtext filter and Pillow is not installed." >&2
  echo "  install one of them:  pip install pillow" >&2
  exit 1
fi

if [[ -n "$CAPTION_PNG" ]]; then
  ffmpeg -nostdin -v error -y -i "$WORK/joined.mp4" -i "$CAPTION_PNG" \
    -filter_complex "[0:v][1:v]overlay=0:0:format=auto[v]" \
    -map "[v]" -map 0:a? \
    -af "loudnorm=I=-16:TP=-1.5:LRA=11" \
    -c:v libx264 -profile:v high -pix_fmt yuv420p -crf 20 -r "$FPS" \
    -c:a aac -b:a 128k -ar 44100 -ac 2 -movflags +faststart "$OUT"
else
  ffmpeg -nostdin -v error -y -i "$WORK/joined.mp4" \
    -vf "drawtext=fontfile='${FONT}':textfile='${WORK}/caption.txt':fontcolor=white:fontsize=44:x=(w-text_w)/2:y=h*0.07:shadowcolor=black@0.6:shadowx=2:shadowy=2" \
    -af "loudnorm=I=-16:TP=-1.5:LRA=11" \
    -c:v libx264 -profile:v high -pix_fmt yuv420p -crf 20 -r "$FPS" \
    -c:a aac -b:a 128k -ar 44100 -ac 2 -movflags +faststart "$OUT"
fi

# ---- gates --------------------------------------------------------------------
DUR="$(python3 "$PROBE" duration "$OUT")"
python3 - "$DUR" "$N_BLOCKS" <<'PY'
import sys
dur, n = float(sys.argv[1]), int(sys.argv[2])
target = n * 10
if abs(dur - target) > 0.5:
    sys.exit(f"  FAIL duration {dur:.2f}s, expected {target}s (+/- 0.5)")
print(f"  duration {dur:.2f}s / {target}s target — ok")
PY

ffmpeg -nostdin -v error -i "$OUT" -f null - \
  && echo "  full decode — ok"

echo
echo "  $OUT"
echo "  caption: $CAPTION"
