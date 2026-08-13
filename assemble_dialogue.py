"""
Dialogue Assembler — builds line-aligned character tracks from per-line VO files
Run:  python assemble_dialogue.py <lines_dir> -m manifest.txt -o out/
Requirements: pip install numpy imageio-ffmpeg

Takes one audio file per script line and lays them out on a single timeline,
producing a separate track per character plus a combined mix.

Timing is re-derived from the ACTUAL rendered durations rather than trusting
the script's syllable estimate: each clip is trimmed to its real speech bounds,
then spaced using the escalation gap model (short-line pairs get tighter gaps,
and gaps close as the scene tightens). This keeps the pacing intact no matter
how fast or slow the voice model reads a given line.
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile
import wave

import numpy as np

try:
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    FFMPEG = "ffmpeg"

SR = 48000
TRIM_DB = -45.0      # speech floor for trimming clip head/tail padding
TRIM_GUARD = 0.030   # keep 30ms either side of speech when trimming
FADE = 0.008         # micro-fade on each clip edge, prevents ticks
VOW = "aeiouy"


def syllables(text):
    n = 0
    for w in text.split():
        w = re.sub(r"[^a-z']", "", w.lower()).replace("'", "")
        if not w:
            continue
        c, prev = 0, False
        for ch in w:
            v = ch in VOW
            if v and not prev:
                c += 1
            prev = v
        if w.endswith("e") and c > 1 and not w.endswith(("le", "ee", "ye")):
            c -= 1
        n += max(1, c)
    return n


def load(path):
    """Decode anything to mono float at SR."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as t:
        tmp = t.name
    try:
        r = subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
                            "-i", path, "-ac", "1", "-ar", str(SR),
                            "-acodec", "pcm_s16le", tmp], capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"could not decode {path}:\n{r.stderr[-500:]}")
        with wave.open(tmp) as w:
            a = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2")
        return a.astype(np.float64) / 32768.0
    finally:
        os.unlink(tmp)


def trim(x):
    """Strip the silent padding voice models leave on each clip."""
    fl = int(0.020 * SR)
    n = len(x) // fl
    if n < 2:
        return x
    rms = np.sqrt((x[: n * fl].reshape(n, fl) ** 2).mean(axis=1))
    live = np.where(20 * np.log10(np.maximum(rms, 1e-9)) >= TRIM_DB)[0]
    if not len(live):
        return x
    g = int(TRIM_GUARD / 0.020)
    s = max(0, live[0] - g) * fl
    e = min(n, live[-1] + 1 + g) * fl
    y = x[s:e].copy()
    f = int(FADE * SR)
    if len(y) > 2 * f:
        y[:f] *= np.linspace(0, 1, f)
        y[-f:] *= np.linspace(1, 0, f)
    return y


def write(path, tracks):
    """tracks: list of 1-D arrays, written as interleaved channels (or mono)."""
    n = max(len(t) for t in tracks)
    buf = np.zeros((n, len(tracks)))
    for i, t in enumerate(tracks):
        buf[: len(t), i] = t
    buf = np.clip(buf, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(len(tracks))
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((buf * 32767).astype("<i2").tobytes())


def schedule(rows):
    """Place each clip using the escalation gap model. rows: (idx, spk, text, audio)."""
    N = len(rows)

    def gap(i):
        a, b = rows[i][4], rows[i + 1][4]          # syllable counts
        base = 0.14 if (a <= 4 and b <= 4) else (0.20 if (a <= 6 or b <= 6) else 0.26)
        return base * (1.10 - 0.45 * (i / max(1, N - 2)))

    beats = {}
    for i, (_, _, text, _, _) in enumerate(rows):
        t = text.lower()
        if t.startswith("four percent"):
            beats[i - 1] = 0.90                     # the smile drops
        elif t.startswith("fine!"):
            beats[i - 1] = 0.45                     # she cracks
        elif t.startswith("now we"):
            beats[i - 1] = 0.90                     # the silence before the button

    out, t = [], 0.0
    for i, (idx, spk, text, aud, _) in enumerate(rows):
        out.append((t, spk, aud, idx, text))
        t += len(aud) / SR
        if i < N - 1:
            t += gap(i) + beats.get(i, 0.0)
    return out, t


def main():
    ap = argparse.ArgumentParser(description="Assemble per-line VO into character tracks")
    ap.add_argument("lines_dir", help="directory of per-line audio files")
    ap.add_argument("-m", "--manifest", required=True,
                    help="lines file: 'index|SPEAKER|text' per row")
    ap.add_argument("-o", "--out", default="assembled")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    rows = []
    for ln in open(args.manifest):
        ln = ln.strip()
        if not ln:
            continue
        idx, spk, text = ln.split("|", 2)
        idx = int(idx)
        hits = [f for f in sorted(os.listdir(args.lines_dir))
                if f.startswith(f"{idx:02d}") or f.startswith(f"{idx}.")]
        if not hits:
            sys.exit(f"no audio file found for line {idx} in {args.lines_dir}")
        rows.append((idx, spk.upper(), text, trim(load(os.path.join(args.lines_dir, hits[0]))),
                     syllables(text)))

    placed, total = schedule(rows)
    n = int(total * SR) + SR // 2
    speakers = sorted({r[1] for r in rows})
    tracks = {s: np.zeros(n) for s in speakers}

    for start, spk, aud, idx, text in placed:
        i = int(start * SR)
        tracks[spk][i: i + len(aud)] += aud

    for s in speakers:
        write(os.path.join(args.out, f"{s.lower()}.wav"), [tracks[s]])
    mix = sum(tracks.values())
    peak = np.abs(mix).max()
    if peak > 0:
        mix = mix / peak * 0.89                     # -1 dBFS
    write(os.path.join(args.out, "mix.wav"), [mix])
    write(os.path.join(args.out, "split_stereo.wav"),
          [tracks[speakers[0]], tracks[speakers[1]]] if len(speakers) == 2 else [mix])

    print(f"assembled {len(rows)} lines -> {total:.2f}s")
    for s in speakers:
        secs = sum(len(a) / SR for _, sp, a, _, _ in placed if sp == s)
        print(f"  {s:<6} {sum(1 for r in rows if r[1] == s):2d} lines  {secs:5.2f}s speech")
    print(f"\n  wrote {args.out}/: " + ", ".join(
        [f"{s.lower()}.wav" for s in speakers] + ["mix.wav", "split_stereo.wav"]))
    print("\n  timeline:")
    for start, spk, aud, idx, text in placed:
        print(f"   {idx:2d}  {start:6.2f}-{start + len(aud) / SR:6.2f}  "
              f"{spk:<6} {len(aud) / SR:4.2f}s  {text[:46]}")


if __name__ == "__main__":
    main()
