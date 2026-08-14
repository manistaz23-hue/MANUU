"""
Audio Silence Cleaner — removes dead air from conversation / voiceover tracks
Run:  python clean_audio_silence.py input.wav [-o output.wav]
Requirements: pip install numpy      (stdlib `wave` handles the I/O)

Tightens long pauses instead of deleting them outright, so dialogue keeps a
natural rhythm. Cuts are always made inside room tone and crossfaded, so no
clicks and no clipped word onsets.
"""

import argparse
import sys
import wave

import numpy as np

# ── Tuning ──────────────────────────────────────────────────────────────────
TH_DB = -50.0        # silence threshold; sits between speech (~-30dB) and floor (~-65dB)
FRAME = 0.020        # analysis frame length, seconds
GUARD = 0.080        # room tone kept either side of speech, protects onsets/tails
MIN_SIL = 0.30       # gaps shorter than this are left completely untouched
TARGET_PAUSE = 0.28  # long gaps are tightened down to this natural beat
HEAD = 0.10          # room tone left at the very start
TAIL = 0.30          # room tone left at the very end
XFADE = 0.012        # crossfade length at each splice
DUCK_DB = -14.0      # gentle hush applied to the room tone that is kept


def read_wav(path):
    with wave.open(path) as w:
        params = (w.getframerate(), w.getnchannels(), w.getsampwidth())
        raw = w.readframes(w.getnframes())
    sr, ch, sw = params
    if sw != 2:
        raise ValueError(f"only 16-bit PCM supported, got {sw * 8}-bit")
    a = np.frombuffer(raw, dtype="<i2").reshape(-1, ch).astype(np.float64) / 32768.0
    return a, sr, ch, sw


def write_wav(path, a, sr, ch, sw):
    with wave.open(path, "wb") as w:
        w.setnchannels(ch)
        w.setsampwidth(sw)
        w.setframerate(sr)
        w.writeframes((np.clip(a, -1.0, 1.0) * 32767).astype("<i2").tobytes())


def speech_mask(mono, sr):
    """Per-sample boolean mask of speech, dilated by GUARD on both sides."""
    fl = int(FRAME * sr)
    nf = len(mono) // fl
    rms = np.sqrt((mono[: nf * fl].reshape(nf, fl) ** 2).mean(axis=1))
    speech = 20 * np.log10(np.maximum(rms, 1e-9)) >= TH_DB

    keep = speech.copy()
    for s in range(1, int(round(GUARD / FRAME)) + 1):
        keep[s:] |= speech[:-s]    # extend backwards, protects word onsets
        keep[:-s] |= speech[s:]    # extend forwards, protects word tails

    mask = np.repeat(keep, fl)
    return np.concatenate([mask, np.zeros(len(mono) - len(mask), bool)])


def duck_room_tone(a, keep, sr):
    """Attenuate non-speech with smooth ramps, so it hushes rather than gates."""
    gain = np.where(keep, 1.0, 10 ** (DUCK_DB / 20.0))
    k = int(0.040 * sr) | 1
    ker = np.ones(k) / k
    smooth = np.convolve(np.pad(gain, (k // 2, k // 2), mode="edge"), ker, mode="valid")
    return a * smooth[: len(a), None]


def crossfade_join(pieces, xf):
    """Concatenate with equal-power crossfades; junctions all sit in room tone."""
    pieces = [p for p in pieces if len(p)]
    out = pieces[0]
    for p in pieces[1:]:
        m = min(xf, len(out), len(p))
        if m < 8:
            out = np.concatenate([out, p])
            continue
        t = np.linspace(0, np.pi / 2, m)[:, None]
        joined = out[-m:] * np.cos(t) ** 2 + p[:m] * np.sin(t) ** 2
        out = np.concatenate([out[:-m], joined, p[m:]])
    return out


def segments(keep):
    """Contiguous speech spans as (start, end) sample indices."""
    d = np.diff(keep.astype(np.int8))
    starts = list(np.where(d == 1)[0] + 1)
    ends = list(np.where(d == -1)[0] + 1)
    if keep[0]:
        starts.insert(0, 0)
    if keep[-1]:
        ends.append(len(keep))
    return list(zip(starts, ends))


def clean(path, out_path):
    a, sr, ch, sw = read_wav(path)
    n = len(a)
    keep = speech_mask(a.mean(axis=1), sr)
    segs = segments(keep)
    if not segs:
        raise ValueError("no speech found above the silence threshold")

    a = duck_room_tone(a, keep, sr)
    hd, tl = int(HEAD * sr), int(TAIL * sr)
    tp, xf = int(TARGET_PAUSE * sr), int(XFADE * sr)

    pieces = [a[max(0, segs[0][0] - hd) : segs[0][1]]]
    cuts = []
    for i in range(1, len(segs)):
        gs, ge = segs[i - 1][1], segs[i][0]
        gap = ge - gs
        if gap / sr < MIN_SIL:
            pieces.append(a[gs:ge])                  # short pause, keep verbatim
        else:
            take = min(tp, gap)                      # tighten, keeping middle
            mid = gs + (gap - take) // 2
            pieces.append(a[mid : mid + take])
            cuts.append((gs / sr, ge / sr, gap / sr, (gap - take) / sr))
        pieces.append(a[segs[i][0] : segs[i][1]])
    pieces.append(a[segs[-1][1] : min(n, segs[-1][1] + tl)])

    out = crossfade_join(pieces, xf)
    fi, fo = int(0.015 * sr), int(0.25 * sr)
    out[:fi] *= np.linspace(0, 1, fi)[:, None]
    out[-fo:] *= np.linspace(1, 0, fo)[:, None]

    write_wav(out_path, out, sr, ch, sw)

    print(f"speech segments   : {len(segs)}")
    print(f"gaps tightened    : {len(cuts)}")
    print(f"dead air removed  : {sum(c[3] for c in cuts):.2f}s")
    print(f"duration          : {n / sr:.2f}s -> {len(out) / sr:.2f}s "
          f"(-{100 * (1 - len(out) / n):.1f}%)")
    for s, e, gap, rm in cuts:
        print(f"    {s:6.2f}-{e:6.2f} ({gap:.2f}s)  -{rm:.2f}s")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Remove dead air from a 16-bit WAV")
    ap.add_argument("input")
    ap.add_argument("-o", "--output", help="defaults to <input>_cleaned.wav")
    ap.add_argument("--pause", type=float, default=TARGET_PAUSE,
                    help=f"seconds of pause left where a long gap was (default {TARGET_PAUSE})")
    ap.add_argument("--min-sil", type=float, default=MIN_SIL,
                    help=f"gaps shorter than this are left alone (default {MIN_SIL})")
    ap.add_argument("--guard", type=float, default=GUARD,
                    help=f"room tone kept either side of speech (default {GUARD})")
    ap.add_argument("--back-to-back", action="store_true",
                    help="tightest usable spacing: 0.14s total silence between phrases")
    ap.add_argument("--threshold", type=float, default=TH_DB,
                    help=f"silence threshold in dBFS (default {TH_DB})")
    args = ap.parse_args()

    if args.back_to_back:
        # Total silence between phrases is guard + pause + guard, so the guard
        # has to come down too or 0.28s survives every cut.
        args.guard, args.pause, args.min_sil = 0.040, 0.060, 0.160
    if args.pause >= args.min_sil:
        # a target at or above the threshold can never shorten anything
        sys.exit(f"--pause ({args.pause}) must be below --min-sil ({args.min_sil})")
    TARGET_PAUSE, MIN_SIL, TH_DB, GUARD = (args.pause, args.min_sil,
                                           args.threshold, args.guard)
    print(f"spacing: {GUARD:.3f}s guard + {TARGET_PAUSE:.3f}s pause + {GUARD:.3f}s guard "
          f"= {2 * GUARD + TARGET_PAUSE:.3f}s between phrases")

    out = args.output or args.input.rsplit(".", 1)[0] + "_cleaned.wav"
    clean(args.input, out)
