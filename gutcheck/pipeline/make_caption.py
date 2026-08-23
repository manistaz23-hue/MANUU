#!/usr/bin/env python3
"""Render the episode's static top caption plate as a transparent PNG.

    python3 pipeline/make_caption.py "Eating a Chipotle bowl right now:" caption.png \
        --width 1080 --height 1920 --font /path/to/Bold.ttf

The plate is a title, not a subtitle: one authored line that never changes and never
moves. Rendering it here rather than with ffmpeg's drawtext gives identical typography
on every machine and works on ffmpeg builds compiled without libfreetype.

If the text is too wide for the frame the font size steps down until it fits — but a
caption that needs stepping down is a caption whose food name is too long. Shorten the
food, not the type.
"""

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Pillow is required for the PNG caption path: pip install pillow")

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Black.ttf",
    "/Library/Fonts/Arial Black.ttf",
    "C:/Windows/Fonts/ariblk.ttf",
]


def pick_font(explicit):
    if explicit:
        if not Path(explicit).is_file():
            sys.exit(f"no such font: {explicit}")
        return explicit
    for c in FONT_CANDIDATES:
        if Path(c).is_file():
            return c
    sys.exit("no bold font found; pass --font /path/to/a-bold.ttf")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("text")
    ap.add_argument("out")
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--height", type=int, default=1920)
    ap.add_argument("--font", default=None)
    ap.add_argument("--size", type=int, default=44)
    ap.add_argument("--y-fraction", type=float, default=0.07)
    args = ap.parse_args()

    font_path = pick_font(args.font)
    margin = int(args.width * 0.06)
    size = args.size

    while size > 20:
        font = ImageFont.truetype(font_path, size)
        probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        w = probe.textbbox((0, 0), args.text, font=font)[2]
        if w <= args.width - 2 * margin:
            break
        size -= 2
    else:
        font = ImageFont.truetype(font_path, size)

    if size != args.size:
        print(f"  ! caption stepped down to {size}px to fit — consider a shorter food name",
              file=sys.stderr)

    img = Image.new("RGBA", (args.width, args.height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), args.text, font=font)
    x = (args.width - (bbox[2] - bbox[0])) // 2 - bbox[0]
    y = int(args.height * args.y_fraction)

    # Hard drop shadow at 60% black — no glow, no box. See docs/03-style-bible.md.
    draw.text((x + 2, y + 2), args.text, font=font, fill=(0, 0, 0, 153))
    draw.text((x, y), args.text, font=font, fill=(255, 255, 255, 255))

    img.save(args.out)
    print(args.out)


if __name__ == "__main__":
    main()
