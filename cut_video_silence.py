"""
Video Silence Cutter — removes dead air from dialogue video, frame-accurately
Run:  python cut_video_silence.py input.mp4 [-o output.mp4]
Requirements: pip install numpy imageio-ffmpeg

Detects silence from the audio track, then chooses each splice point to
minimise VISUAL discontinuity, so jump cuts on a locked-off shot are hard
to see. Long pauses are trimmed but preserved as dramatic beats rather than
flattened, and pre-existing hard cuts in the source are never spliced across.
"""

import argparse
import json
import os
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

# ── Tuning ──────────────────────────────────────────────────────────────────
TH_DB = -50.0        # silence threshold
AFRAME = 0.020       # audio analysis frame
GUARD = 0.080        # room tone kept either side of speech
MIN_SIL = 0.30       # gaps shorter than this are never touched
TARGET_PAUSE = 0.30  # ordinary gaps tighten to this
BEAT_LIMIT = 1.50    # gaps longer than this are treated as deliberate beats...
BEAT_PAUSE = 0.80    # ...and only tightened to here, keeping the dramatic hold
MIN_REMOVE = 0.15    # never make a cut that saves less than this (not worth the jump)
SCENE_DIFF = 5.0     # inter-frame diff marking a pre-existing hard cut


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"ffmpeg failed:\n{r.stderr[-2000:]}")
    return r


def probe_fps(path):
    r = subprocess.run([FFMPEG, "-hide_banner", "-i", path],
                       capture_output=True, text=True)
    for tok in r.stderr.split():
        pass
    import re
    m = re.search(r"(\d+(?:\.\d+)?) fps", r.stderr)
    if not m:
        sys.exit("could not determine frame rate")
    return float(m.group(1))


def extract(path, tmp, fps):
    """Pull the audio track and a bank of tiny grayscale frames."""
    wav = os.path.join(tmp, "a.wav")
    gray = os.path.join(tmp, "v.gray")
    run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-i", path,
         "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2", wav])
    W, H = 96, 54
    run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-i", path,
         "-vf", f"fps={fps},scale={W}:{H},format=gray", "-f", "rawvideo", gray])
    with wave.open(wav) as w:
        sr = w.getframerate()
        a = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2")
        a = a.reshape(-1, w.getnchannels()).astype(np.float64) / 32768.0
    d = np.fromfile(gray, dtype=np.uint8)
    n = len(d) // (W * H)
    return a.mean(axis=1), sr, d[: n * W * H].reshape(n, H, W).astype(np.float32)


def keep_mask(mono, sr, nframes, fps):
    """Per-video-frame speech flag, dilated by GUARD."""
    fl = int(AFRAME * sr)
    nf = len(mono) // fl
    rms = np.sqrt((mono[: nf * fl].reshape(nf, fl) ** 2).mean(axis=1))
    sp = 20 * np.log10(np.maximum(rms, 1e-9)) >= TH_DB
    keep = sp.copy()
    for s in range(1, int(round(GUARD / AFRAME)) + 1):
        keep[s:] |= sp[:-s]
        keep[:-s] |= sp[s:]
    t = (np.arange(nframes) + 0.5) / fps
    return keep[np.clip((t / AFRAME).astype(int), 0, len(keep) - 1)]


def spans(mask, n):
    d = np.diff(mask.astype(np.int8))
    starts = list(np.where(d == 1)[0] + 1)
    ends = list(np.where(d == -1)[0] + 1)
    if mask[0]:
        starts.insert(0, 0)
    if mask[-1]:
        ends.append(n)
    return list(zip(starts, ends))


def build_plan(mono, sr, vf, fps):
    nfr = len(vf)
    segs = spans(keep_mask(mono, sr, nfr, fps), nfr)
    if not segs:
        sys.exit("no speech detected")

    motion = np.abs(np.diff(vf, axis=0)).mean(axis=(1, 2))
    scene = [int(i) for i in np.where(motion > SCENE_DIFF)[0]]

    kept, cuts = [], []
    cur = segs[0][0]
    for k in range(1, len(segs)):
        gs, ge = segs[k - 1][1], segs[k][0]
        gap = ge - gs
        if gap / fps < MIN_SIL:
            continue
        target = BEAT_PAUSE if gap / fps > BEAT_LIMIT else TARGET_PAUSE
        tgt = int(round(target * fps))
        if gap <= tgt:
            continue

        lo, hi = gs, ge                      # keep any pre-existing cut intact
        for b in scene:
            if gs < b < ge:
                if (b - gs) >= (ge - b):
                    hi = b
                else:
                    lo = b
        need = min(gap - tgt, max(0, (hi - lo) - 1))
        if need / fps < MIN_REMOVE:
            continue

        best = None                          # splice where the picture matches best
        for o in range(lo, hi - need + 1):
            sc = float(np.abs(vf[max(o - 1, 0)] - vf[min(o + need, nfr - 1)]).mean())
            if best is None or sc < best[0]:
                best = (sc, o)
        sc, o = best
        kept.append((cur, o))
        cur = o + need
        cuts.append(dict(gap_s=gs / fps, gap_e=ge / fps, gap=gap / fps,
                         removed=need / fps, cut_at=o / fps, vdiff=sc,
                         beat=gap / fps > BEAT_LIMIT))
    kept.append((cur, segs[-1][1]))
    return [(s, e) for s, e in kept if e > s], cuts, nfr, scene


def cut_audio(src_wav, dst_wav, kept, fps):
    """Cut audio at exactly the video frame times, sample-accurate, crossfaded.

    aselect would snap splices to the codec's frame grid (~32ms each), which
    accumulates into visible lip-sync drift, so the audio is rebuilt here.
    """
    with wave.open(src_wav) as w:
        sr, ch, sw = w.getframerate(), w.getnchannels(), w.getsampwidth()
        a = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2")
        a = a.reshape(-1, ch).astype(np.float64) / 32768.0

    xf = int(0.012 * sr)
    pieces = []
    for s, e in kept:
        pieces.append((int(round(s / fps * sr)), int(round(e / fps * sr))))

    out = a[pieces[0][0]:pieces[0][1]]
    for k in range(1, len(pieces)):
        bs, be = pieces[k]
        p = a[bs:be]
        m = min(xf, len(out), bs)
        if m < 8:
            out = np.concatenate([out, p])
            continue
        # Blend the outgoing tail against the discarded room tone immediately
        # before the resume point. Overlapping the kept pieces instead would
        # shorten the audio by m samples per join and drift it ahead of picture.
        t = np.linspace(0, np.pi / 2, m)[:, None]
        tail = out[-m:] * np.cos(t) ** 2 + a[bs - m:bs] * np.sin(t) ** 2
        out = np.concatenate([out[:-m], tail, p])
    with wave.open(dst_wav, "wb") as w:
        w.setnchannels(ch); w.setsampwidth(sw); w.setframerate(sr)
        w.writeframes((np.clip(out, -1, 1) * 32767).astype("<i2").tobytes())


def render(src, out, kept, fps, tmp):
    sel = "+".join(f"between(n,{s},{e - 1})" for s, e in kept)
    vid = os.path.join(tmp, "v.mp4")
    acut = os.path.join(tmp, "acut.wav")
    # -r pins the output rate; without it the muxer picks 25fps and duplicates frames
    run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-i", src,
         "-an", "-vf", f"select='{sel}',setpts=N/{fps}/TB", "-r", str(fps),
         "-fps_mode", "cfr", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-pix_fmt", "yuv420p", vid])
    cut_audio(os.path.join(tmp, "a.wav"), acut, kept, fps)
    run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-i", vid, "-i", acut,
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", "-shortest", out])


def main():
    ap = argparse.ArgumentParser(description="Cut silent sections out of a video")
    ap.add_argument("input")
    ap.add_argument("-o", "--output")
    args = ap.parse_args()
    out = args.output or args.input.rsplit(".", 1)[0] + "_cut.mp4"

    with tempfile.TemporaryDirectory() as tmp:
        fps = probe_fps(args.input)
        mono, sr, vf = extract(args.input, tmp, fps)
        kept, cuts, nfr, scene = build_plan(mono, sr, vf, fps)
        render(args.input, out, kept, fps, tmp)

    total = sum(c["removed"] for c in cuts)
    okept = sum(e - s for s, e in kept)
    print(f"pre-existing hard cuts in source : {[round(s / fps, 2) for s in scene]}")
    print(f"cuts made                        : {len(cuts)}")
    print(f"dead air removed                 : {total:.2f}s")
    print(f"duration  {nfr / fps:.2f}s -> {okept / fps:.2f}s "
          f"(-{100 * (1 - okept / nfr):.1f}%)")
    print("\n  gap             removed  splice@   visual diff")
    for c in cuts:
        tag = "  <- beat, kept long" if c["beat"] else ""
        print(f"  {c['gap_s']:6.2f}-{c['gap_e']:6.2f}   {c['removed']:.2f}s  "
              f"{c['cut_at']:6.2f}s   {c['vdiff']:5.2f}{tag}")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
