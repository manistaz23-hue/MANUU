#!/usr/bin/env python3
"""Probe a media file for fps or duration.

    python3 pipeline/probe.py fps      block01.mp4
    python3 pipeline/probe.py duration final.mp4

Uses ffprobe when it is installed. Falls back to parsing `ffmpeg -i` when it is not —
some minimal ffmpeg builds ship the encoder without the probe tool, and the assembler
should not fall over because of that.
"""

import re
import shutil
import subprocess
import sys


def _run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def _from_ffprobe(what, path):
    if not shutil.which("ffprobe"):
        return None
    if what == "fps":
        out = _run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                    "-show_entries", "stream=r_frame_rate", "-of", "csv=p=0", path])
        raw = out.stdout.strip()
        if "/" in raw:
            n, d = raw.split("/")
            return round(int(n) / int(d), 3)
        return float(raw) if raw else None
    out = _run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "csv=p=0", path])
    return float(out.stdout.strip()) if out.stdout.strip() else None


def _from_ffmpeg(what, path):
    if not shutil.which("ffmpeg"):
        return None
    err = _run(["ffmpeg", "-hide_banner", "-i", path]).stderr
    if what == "fps":
        m = re.search(r"(\d+(?:\.\d+)?)\s+fps", err)
        return round(float(m.group(1)), 3) if m else None
    # Duration from the header is rounded to 1/100s; good enough for the ±0.5s gate,
    # but decode to the last packet when we need to be sure the file is whole.
    out = _run(["ffmpeg", "-v", "error", "-i", path, "-f", "null", "-"])
    m = re.search(r"time=(\d+):(\d+):(\d+\.\d+)", out.stderr)
    if m:
        h, mi, s = m.groups()
        return int(h) * 3600 + int(mi) * 60 + float(s)
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", err)
    if m:
        h, mi, s = m.groups()
        return int(h) * 3600 + int(mi) * 60 + float(s)
    return None


def main(argv):
    if len(argv) != 3 or argv[1] not in ("fps", "duration"):
        print(__doc__)
        return 2
    what, path = argv[1], argv[2]
    value = _from_ffprobe(what, path)
    if value is None:
        value = _from_ffmpeg(what, path)
    if value is None:
        print(f"could not read {what} from {path}", file=sys.stderr)
        return 1
    print(value)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
