#!/usr/bin/env python3
"""Turn a validated episode into ready-to-submit generation payloads.

Usage:
    python3 pipeline/build_payloads.py episodes/ep01-chipotle-bowl.json
    python3 pipeline/build_payloads.py episodes/ep01-chipotle-bowl.json --route B

Writes to build/<id>-<slug>/:
    video_batch.json   the generate_video_batch payload — 6 indexed requests
    guest_asset.json   the one-request generate_image_batch payload for this episode's food
    audio_batch.json   Route B only — the generate_audio_batch payload
    blocks/blockNN.txt the same prompts as plain text, for reading before you spend

Asset job ids come from prompts/ASSET_IDS.md. Any id still marked TODO is emitted as a
TODO placeholder and counted in the summary — the payload is not submittable until every
one is filled in.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Short descriptions used in the prompt's REFERENCES line. Long enough to identify,
# short enough not to fight the style formula (which owns the look).
CAST = {
    "gut":    ("GUT",   "the coral bean-shaped stomach with the liquid line",
               "a warm, loud, weary voice"),
    "pipes":  ("PIPES", "the long vertical pink esophagus tube",
               "a higher, faster, nervous voice"),
    "hq":     ("HQ",    "the standing pink brain holding a phone",
               "a flat, bored, managerial voice"),
    "liv":    ("LIV",   "the dark reddish-brown wedge-shaped liver",
               "a dry, gravelly, sarcastic voice"),
    "loops":  ("LOOPS", "the coiled pink small intestine with several pairs of eyes",
               "a fast, bright, over-caffeinated voice"),
    "rusty":  ("RUSTY", "the dark coiled colon in low amber light",
               "a low, slow, unbothered voice"),
    "yuvi":   ("YUVI",  "the red teardrop uvula hanging between the teeth",
               "a light, smug, unhurried voice"),
    "buzz":   ("BUZZ",  "the small round pale-pink bladder with a sweat drop",
               "a high, tight, breathless voice"),
    "pancho": ("PANCHO", "the small tan pancreas with rolled sleeves",
               "a clipped, competent, increasingly ragged voice"),
}

LOCATIONS = {
    "esophagus":  "the inside of the esophagus, a vertical pink tube receding into dark brown",
    "stomach":    "the stomach cavity, curved pink walls with liquid pooled at the bottom",
    "brain_room": "the control room inside the skull, dark red veined walls, a green wall button",
    "mouth_gate": "the inside of the mouth looking out past two rows of white teeth",
    "basement":   "the dark coiled colon tunnel in low amber light",
}

STANDING_PROPS = {
    "gag_button": "the large round lime-green gag-reflex button",
    "phone":      "HQ's small blue-screened cartoon phone",
    "monitor":    "the small wall-mounted monitor screen",
}

GUEST_VOICE = "a cheerful, unbothered voice"

SHOT_SLOTS = ["0.0s to 2.5s", "2.5s to 5.0s", "5.0s to 7.5s", "7.5s to 10.0s"]


def read_text(rel):
    return (ROOT / rel).read_text().strip()


def parse_asset_ids():
    """Pull `key -> job_id` out of the markdown tables in prompts/ASSET_IDS.md."""
    path = ROOT / "prompts" / "ASSET_IDS.md"
    ids = {}
    if not path.exists():
        return ids
    for line in path.read_text().splitlines():
        cells = [c.strip().strip("`") for c in line.split("|")]
        cells = [c for c in cells if c]
        if len(cells) >= 4 and re.fullmatch(r"[a-z0-9_]+", cells[0]):
            ids[cells[0]] = cells[-1]
    return ids


def resolve(key, ep, ids, guest_keys):
    """Return (display_name, description, job_id) for any key used by a block."""
    if key in CAST:
        name, desc, _ = CAST[key]
        return name, desc, ids.get(key, "TODO")
    if key in LOCATIONS:
        return key.upper(), LOCATIONS[key], ids.get(key, "TODO")
    if key in STANDING_PROPS:
        return key.upper(), STANDING_PROPS[key], ids.get(key, "TODO")
    guest_keys.add(key)
    return (key.upper().replace("_", " "),
            ep["through_line"]["prop_prompt"],
            ids.get(f"{ep['id']}_guest", "TODO"))


def voice_of(key):
    if key in CAST:
        return CAST[key][2]
    return GUEST_VOICE


def build_block_prompt(ep, block, ids, guest_keys, route):
    style = read_text("prompts/_STYLE.txt").rstrip(".")
    palette = read_text("prompts/_PALETTE.txt")

    refs = []
    loc_name, loc_desc, loc_id = resolve(block["location"], ep, ids, guest_keys)
    refs.append((f"LOCATION ({loc_desc})", loc_id))
    for c in block["characters"]:
        name, desc, jid = resolve(c, ep, ids, guest_keys)
        refs.append((f"{name} ({desc})", jid))
    for p in block["props"]:
        name, desc, jid = resolve(p, ep, ids, guest_keys)
        refs.append((f"{name} ({desc})", jid))

    ref_line = " ".join(
        f"@Image{i} = {label}." for i, (label, _) in enumerate(refs, start=1)
    )

    shots = []
    for i, (slot, shot) in enumerate(zip(SHOT_SLOTS, block["shots"]), start=1):
        shots.append(f"SHOT {i} — {slot} — {shot}.")
        if i < len(SHOT_SLOTS):
            shots.append("HARD CUT.")
    shots_text = "\n".join(shots)

    speakers = list(dict.fromkeys(t["speaker"] for t in block["turns"]))
    speaker_names = [resolve(s, ep, ids, guest_keys)[0] for s in speakers]

    if route == "A":
        dialogue = "\n".join(
            f'  {resolve(t["speaker"], ep, ids, guest_keys)[0]}: "{t["line"]}"'
            for t in block["turns"]
        )
        dialogue_block = (
            "DIALOGUE — ONLY these two characters speak, ONLY these exact words, in this "
            "exact order, nothing added, nothing paraphrased, no improvised words:\n"
            + dialogue
        )
        voices = " and ".join(
            f"{resolve(s, ep, ids, guest_keys)[0]} in {voice_of(s)}" for s in speakers
        )
        audio = (
            f"AUDIO: the two named characters speaking their lines natively — {voices} — "
            f"plus {block['sfx']}. No narration, no music, no extra voices, no improvised "
            "words, no laugh track."
        )
        talking_clause = (
            "Only the two named characters are visible and only their mouths move."
        )
        negative_tail = "a third speaking voice, "
    else:
        dialogue_block = (
            "Characters only emote and gesture — they do NOT talk, their mouths stay "
            "closed, no lip movement of any kind. The voice is added separately in post."
        )
        audio = f"AUDIO: {block['sfx']} only — no voice, no narration, no music."
        talking_clause = "Only the two named characters are visible."
        negative_tail = "characters talking, lip-sync, "

    prompt = f"""Style: {style} — the visual style is EXACTLY as in the reference images, same rendering, same surface treatment.
{palette}
A single 10-second scene of FOUR hard-cut shots. Do NOT open the video on any reference image and do NOT show a sheet or swatch — stage everything fresh, matching characters, cavity, colors and background to their references. Motion starts on frame 1, no opening freeze.

REFERENCES (look, identity, palette): {ref_line}

{dialogue_block}

{shots_text}

Four hard cuts at 2.5s, 5.0s and 7.5s, no dissolves, no fades. Simple limited animation on twos, continuous motion within each shot, never freezes. {talking_clause} The final shot eases into a stable, still, micro-moving final frame.

{audio}

NEGATIVE: opening on a reference image, a sheet or swatch, a static first frame, leading freeze, dissolves, fades, new or foreign colors, colored or gradient backgrounds not in the references, recolored characters, style drift, extra characters, extra people, cloned characters, {negative_tail}on-screen text, captions, subtitles, photorealism, 3D render, watermark."""

    return prompt, [jid for _, jid in refs], speaker_names


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("episode")
    ap.add_argument("--route", choices=["A", "B"], default="A",
                    help="A = native dialogue in the clip (default). B = silent clips + one narrator.")
    ap.add_argument("--voice-id", default="TODO", help="Route B only")
    ap.add_argument("--voice-type", default="preset", help="Route B only")
    args = ap.parse_args(argv)

    ep = json.loads(Path(args.episode).read_text())
    ids = parse_asset_ids()
    guest_keys = set()

    outdir = ROOT / "build" / f"{ep['id']}-{ep['slug']}"
    (outdir / "blocks").mkdir(parents=True, exist_ok=True)

    requests, todos = [], 0
    for block in ep["blocks"]:
        prompt, ref_ids, speakers = build_block_prompt(ep, block, ids, guest_keys, args.route)
        todos += ref_ids.count("TODO")
        if len(ref_ids) > 7:
            print(f"  ! block {block['n']}: {len(ref_ids)} refs, the model rejects more than 7")
        (outdir / "blocks" / f"block{block['n']:02d}.txt").write_text(prompt + "\n")
        requests.append({
            "index": block["n"],
            "params": {
                "model": "gemini_omni",
                "prompt": prompt,
                "duration": 10,
                "resolution": "720p",
                "aspect_ratio": "9:16",
                "medias": [{"role": "image_references", "value": j} for j in ref_ids],
            },
        })

    (outdir / "video_batch.json").write_text(
        json.dumps({"requests": requests}, indent=2, ensure_ascii=False) + "\n")

    style = read_text("prompts/_STYLE.txt")
    guest_prompt = (
        f"A single isolated prop centered on a plain flat solid-color background, in THIS "
        f"EXACT style: {style}\n\nObject: {ep['through_line']['prop_prompt']}. Rendered in "
        f"{ep['accent_color']}, the one accent color reserved for this episode's food.\n\n"
        "No hands, no scene, no other objects, no characters. No text, no watermark, no labels."
    )
    (outdir / "guest_asset.json").write_text(json.dumps({"requests": [{
        "index": 1,
        "params": {
            "model": "seedream_v5_pro",
            "prompt": guest_prompt,
            "resolution": "1k",
            "aspect_ratio": "1:1",
            "medias": [{"role": "image", "value": ids.get("style_key", "TODO")}],
        },
    }]}, indent=2, ensure_ascii=False) + "\n")

    if args.route == "B":
        audio_requests = []
        for block in ep["blocks"]:
            line = " ".join(
                f'{resolve(t["speaker"], ep, ids, guest_keys)[0]} says, "{t["line"]}"'
                for t in block["turns"])
            audio_requests.append({"index": block["n"], "params": {
                "model": "text2speech_v2", "variant": "elevenlabs",
                "voice_id": args.voice_id, "voice_type": args.voice_type,
                "prompt": line,
            }})
        (outdir / "audio_batch.json").write_text(
            json.dumps({"requests": audio_requests}, indent=2, ensure_ascii=False) + "\n")

    print(f"\n{ep['id']} · {ep['title']}")
    print(f"  route      {args.route}")
    print(f"  blocks     {len(requests)}  ({len(requests) * 10}s)")
    print(f"  guest keys {sorted(guest_keys)}")
    print(f"  written to build/{ep['id']}-{ep['slug']}/")
    if todos:
        print(f"\n  ! {todos} reference(s) still say TODO.")
        print("  ! Fill prompts/ASSET_IDS.md before submitting — a TODO ref will fail.")
        return 1
    print("\n  all references resolved — payload is submittable")
    return 0


if __name__ == "__main__":
    sys.exit(main())
