#!/bin/bash
# Demo: compile the first AI reaction clip (generated in session)
# Run this locally — downloads the Higgsfield-generated assets and assembles the clip.
# Requirements: ffmpeg, curl

set -e
OUT="reaction_output"
mkdir -p "$OUT"

echo "=== Downloading TTS audio (Leo voice) ==="
curl -L -s "https://d8j0ntlcm91z4.cloudfront.net/user_3EP9SP2r5iXI2tpVbHS353E2m5O/hf_20260627_132649_c1191bc2-5bfb-4552-82bc-42098c514f96.mp3" \
  -o "$OUT/audio_00.mp3" && echo "  ✓ audio_00.mp3"

echo "=== Downloading avatar video (Sofia, Direct-to-Camera) ==="
curl -L -s "https://d8j0ntlcm91z4.cloudfront.net/user_3EP9SP2r5iXI2tpVbHS353E2m5O/hf_20260627_132930_cb0133e6-074f-4e4b-8d59-b52533f7e3e2.mp4" \
  -o "$OUT/avatar_00.mp4" && echo "  ✓ avatar_00.mp4"

echo "=== Burning comment overlay + merging audio ==="
COMMENT="@user123: I accidentally told my boss I loved him when ending a phone call"

ffmpeg -y -loglevel error \
  -i "$OUT/avatar_00.mp4" \
  -i "$OUT/audio_00.mp3" \
  -map 0:v -map 1:a \
  -vf "drawbox=x=0:y=20:w=iw:h=160:color=black@0.65:t=fill,\
drawtext=text='@user123\: I accidentally told my boss':fontcolor=white:fontsize=34:x=(w-text_w)/2:y=38:shadowcolor=black:shadowx=2:shadowy=2:font=DejaVuSans-Bold,\
drawtext=text='I loved him when ending a phone call':fontcolor=white:fontsize=34:x=(w-text_w)/2:y=80:shadowcolor=black:shadowx=2:shadowy=2:font=DejaVuSans-Bold" \
  -c:v libx264 -c:a aac -shortest \
  "$OUT/DEMO_REACTION_clip_00.mp4"

echo ""
echo "✅ Done!"
echo "   Output: $OUT/DEMO_REACTION_clip_00.mp4"
echo "   This is ONE reaction clip. Run reaction_tiktok.py for the full automated pipeline."
