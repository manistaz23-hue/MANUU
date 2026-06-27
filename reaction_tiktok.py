"""
AI Reaction TikTok — Fully Automated Pipeline
=============================================
Generates a TikTok-ready reaction video where an AI avatar reacts
to funny comments/replies with AI voiceover.

Requirements:
    pip install requests
    apt install ffmpeg  (or brew install ffmpeg)

Usage:
    export HIGGSFIELD_API_KEY=your_key_here
    python reaction_tiktok.py

Output:
    reaction_output/REACTION_FINAL.mp4  (9:16 vertical, TikTok ready)
"""

import os
import time
import json
import textwrap
import subprocess
import requests

# ─── Config ──────────────────────────────────────────────────────────────────

API_KEY   = os.environ.get("HIGGSFIELD_API_KEY", "")
API_BASE  = "https://api.higgsfield.ai/v1"
OUT_DIR   = "reaction_output"

# Avatar to use — from your Higgsfield Marketing Studio library.
# Run list_avatars() below to see your options.
AVATAR_ID = "bba3087a-ad14-42c2-b51b-7c22b632abf4"   # Sofia (preset)

# Voice — preset voice_id from Higgsfield voices list.
# Leo (male): 73a45c18-0c56-4642-a61e-f6b303f8ded1
# Gia (female): 530df032-c311-483b-a750-cb3c9e1bcdfd
VOICE_ID  = "73a45c18-0c56-4642-a61e-f6b303f8ded1"

# ─── Reactions ───────────────────────────────────────────────────────────────
# Each entry: the comment shown on screen + the AI's spoken reaction.
# Keep reactions punchy — 1-3 sentences max for 5-8 second clips.

REACTIONS = [
    {
        "comment": "@user123: I accidentally told my boss I loved him when ending a phone call",
        "reaction": "Wait wait wait— Sir. SIR. How are you still employed? "
                    "Did you at least hang up fast enough? I need an update.",
    },
    {
        "comment": "@pizzalover99: My therapist just followed me on TikTok",
        "reaction": "Your therapist is now going to WATCH you do this. "
                    "The betrayal. The breach of the therapeutic relationship. "
                    "Block them. Block them immediately.",
    },
    {
        "comment": "@ngl_chaos: I've been pronouncing 'quinoa' wrong for 7 years and nobody told me",
        "reaction": "Your friends watched you say 'kwin-oh-ah' for SEVEN YEARS "
                    "and just let it happen. Those aren't friends. Those are documentary filmmakers.",
    },
    {
        "comment": "@sleepybean: My cat sat on my laptop and sent my boss a 400-page blank document",
        "reaction": "Your cat submitted a report. "
                    "Four hundred pages of nothing. "
                    "Honestly? More professional than half the emails I've seen.",
    },
    {
        "comment": "@disaster_mode: I tried to Google 'how to adult' and got a WikiHow article",
        "reaction": "The fact that WikiHow has an article called 'How to Adult' "
                    "and you needed it... same. We're all in this together.",
    },
]

# ─── Helpers ─────────────────────────────────────────────────────────────────

os.makedirs(OUT_DIR, exist_ok=True)
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}


def api_post(path: str, body: dict) -> dict:
    r = requests.post(f"{API_BASE}{path}", headers=HEADERS, json=body, timeout=30)
    r.raise_for_status()
    return r.json()


def api_get(path: str) -> dict:
    r = requests.get(f"{API_BASE}{path}", headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()


def wait_for_job(job_id: str, label: str, poll: int = 5, timeout: int = 300) -> str:
    """Poll a Higgsfield job until done. Returns the result URL."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        data = api_get(f"/jobs/{job_id}")
        status = data.get("status", "")
        if status == "completed":
            # result_url lives in different keys depending on type
            url = (
                data.get("result_url")
                or data.get("results", [{}])[0].get("url")
                or data.get("output_url")
            )
            if url:
                print(f"    ✓ {label}")
                return url
        elif status == "failed":
            raise RuntimeError(f"Job {job_id} failed: {data}")
        print(f"    … {label} ({status})")
        time.sleep(poll)
    raise TimeoutError(f"Job {job_id} timed out after {timeout}s")


def download(url: str, path: str):
    if os.path.exists(path):
        print(f"    [skip] {os.path.basename(path)}")
        return
    r = requests.get(url, stream=True, timeout=120)
    r.raise_for_status()
    with open(path, "wb") as f:
        for chunk in r.iter_content(256 * 1024):
            f.write(chunk)


def generate_tts(text: str, idx: int) -> str:
    """Generate TTS audio and return local path."""
    path = os.path.join(OUT_DIR, f"audio_{idx:02d}.mp3")
    if os.path.exists(path):
        print(f"    [skip] audio_{idx:02d}.mp3")
        return path

    print(f"  → Generating TTS for reaction {idx+1}…")
    resp = api_post("/audio/generate", {
        "model": "text2speech_v2_elevenlabs",
        "prompt": text,
        "voice_id": VOICE_ID,
        "voice_type": "preset",
    })
    job_id = resp["results"][0]["id"]
    url = wait_for_job(job_id, f"TTS audio {idx+1}")
    download(url, path)
    return path


def generate_avatar_video(idx: int) -> str:
    """Generate a silent talking-head avatar video and return local path."""
    path = os.path.join(OUT_DIR, f"avatar_{idx:02d}.mp4")
    if os.path.exists(path):
        print(f"    [skip] avatar_{idx:02d}.mp4")
        return path

    print(f"  → Generating avatar video for reaction {idx+1}…")

    # Generate Marketing Studio "Direct-to-Camera" silent clip with the avatar.
    # We merge TTS audio in burn_comment_overlay via ffmpeg.
    resp = api_post("/video/generate", {
        "model": "marketing_studio_video",
        "mode": "ugc_direct_to_camera",
        "aspect_ratio": "9:16",
        "avatar_ids": [AVATAR_ID],
        "generate_audio": False,
        "prompt": (
            "Person reacting to funny comments, expressive and natural, "
            "looking at camera, casual TikTok reaction style"
        ),
    })
    job_id = resp["results"][0]["id"]
    url = wait_for_job(job_id, f"avatar video {idx+1}", poll=10, timeout=600)
    download(url, path)
    return path


def burn_comment_overlay(video_path: str, audio_path: str, comment: str, idx: int) -> str:
    """Merge TTS audio + burn comment text overlay onto the avatar video."""
    out_path = os.path.join(OUT_DIR, f"clip_{idx:02d}.mp4")
    if os.path.exists(out_path):
        print(f"    [skip] clip_{idx:02d}.mp4")
        return out_path

    # Wrap long comments for display
    lines = textwrap.wrap(comment, width=38)
    escaped = r"\n".join(l.replace("'", r"\'").replace(":", r"\:") for l in lines)

    # White text with black shadow + dark banner behind it
    vf = (
        f"drawbox=x=0:y=20:w=iw:h=160:color=black@0.65:t=fill,"
        f"drawtext=text='{escaped}'"
        f":fontcolor=white:fontsize=34:x=(w-text_w)/2:y=38"
        f":shadowcolor=black:shadowx=2:shadowy=2"
        f":font=DejaVuSans-Bold"
    )

    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-i", video_path,          # video (silent)
         "-i", audio_path,          # TTS audio
         "-map", "0:v",
         "-map", "1:a",
         "-vf", vf,
         "-c:v", "libx264", "-c:a", "aac",
         "-shortest",               # trim to audio length
         out_path],
        check=True,
    )
    print(f"    ✓ clip_{idx:02d}.mp4 (overlay + audio)")
    return out_path


def compile_final(clip_paths: list[str]) -> str:
    """Concatenate all clips into the final TikTok video."""
    concat_file = os.path.join(OUT_DIR, "concat.txt")
    with open(concat_file, "w") as f:
        for p in clip_paths:
            f.write(f"file '{os.path.abspath(p)}'\n")

    out = os.path.join(OUT_DIR, "REACTION_FINAL.mp4")
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", concat_file,
         "-c", "copy", out],
        check=True,
    )
    return out


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    if not API_KEY:
        print("ERROR: Set HIGGSFIELD_API_KEY environment variable first.")
        print("  export HIGGSFIELD_API_KEY=your_key_here")
        return

    print(f"\n{'='*50}")
    print("  AI Reaction TikTok — Pipeline Start")
    print(f"{'='*50}")
    print(f"  Reactions to process : {len(REACTIONS)}")
    print(f"  Avatar               : {AVATAR_ID}")
    print(f"  Voice                : {VOICE_ID}")
    print(f"  Output dir           : {OUT_DIR}/\n")

    clip_paths = []

    for i, item in enumerate(REACTIONS):
        print(f"\n[{i+1}/{len(REACTIONS)}] {item['comment'][:60]}…")

        # Step 1: TTS
        audio_path = generate_tts(item["reaction"], i)

        # Step 2: Avatar video (silent — audio merged in step 3)
        avatar_path = generate_avatar_video(i)

        # Step 3: Burn comment text overlay + merge TTS audio
        clip_path = burn_comment_overlay(avatar_path, audio_path, item["comment"], i)
        clip_paths.append(clip_path)

    # Step 4: Compile
    print(f"\n{'='*50}")
    print("  Compiling final video…")
    final = compile_final(clip_paths)

    size_mb = os.path.getsize(final) // (1024 * 1024)
    print(f"\n✅  Done!")
    print(f"   Output : {final}")
    print(f"   Size   : {size_mb} MB")
    print(f"   Clips  : {len(clip_paths)} reactions")
    print(f"\n  Upload to TikTok as-is (9:16 vertical, ready to post)")


if __name__ == "__main__":
    main()
