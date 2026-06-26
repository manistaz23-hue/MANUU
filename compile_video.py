"""
Hidden Camera YouTube Video — Auto Compiler
Run this on your local machine:  python compile_video.py
Requirements: pip install moviepy requests
"""

import os
import requests
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips

OUTPUT_DIR = "hidden_cam_video"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Video clips in scene order ──────────────────────────────────────────────
VIDEO_CLIPS = [
    ("01_intro_title",       "https://d8j0ntlcm91z4.cloudfront.net/user_3EP9SP2r5iXI2tpVbHS353E2m5O/hf_20260626_210705_4be7b2d1-4f7d-43ea-8a88-5dfb7e9ad9df.mp4"),
    ("02_intro_airbnb",      "https://d8j0ntlcm91z4.cloudfront.net/user_3EP9SP2r5iXI2tpVbHS353E2m5O/hf_20260626_210708_a1d1c9a1-0e86-46af-a377-90afaa498d8e.mp4"),
    ("03_alarm_clock",       "https://d8j0ntlcm91z4.cloudfront.net/user_3EP9SP2r5iXI2tpVbHS353E2m5O/hf_20260626_210712_66c5310b-84dc-4995-b160-11d2bd52a300.mp4"),
    ("04_usb_charger",       "https://d8j0ntlcm91z4.cloudfront.net/user_3EP9SP2r5iXI2tpVbHS353E2m5O/hf_20260626_210716_32eb182d-cb9e-4fae-b801-2a1514fbeee7.mp4"),
    ("05_wall_clock",        "https://d8j0ntlcm91z4.cloudfront.net/user_3EP9SP2r5iXI2tpVbHS353E2m5O/hf_20260626_210720_e28fcdae-01f4-452d-bbd6-04b21c0c17b3.mp4"),
    ("06_smartwatch",        "https://d8j0ntlcm91z4.cloudfront.net/user_3EP9SP2r5iXI2tpVbHS353E2m5O/hf_20260626_210839_4cdf3003-9e13-40f7-9b56-0c6208178463.mp4"),
    ("07_picture_frame",     "https://d8j0ntlcm91z4.cloudfront.net/user_3EP9SP2r5iXI2tpVbHS353E2m5O/hf_20260626_210828_d3bb8d41-8680-42f4-b7e1-92b42751c452.mp4"),
    ("08_tv_remote",         "https://d8j0ntlcm91z4.cloudfront.net/user_3EP9SP2r5iXI2tpVbHS353E2m5O/hf_20260626_210725_7b919936-fa22-4ef4-bd7b-99a7f82e7aa0.mp4"),
    ("09_smoke_detector",    "https://d8j0ntlcm91z4.cloudfront.net/user_3EP9SP2r5iXI2tpVbHS353E2m5O/hf_20260626_210728_a40daec5-5251-4022-8c32-abf243684ee9.mp4"),
    ("10_tissue_box",        "https://d8j0ntlcm91z4.cloudfront.net/user_3EP9SP2r5iXI2tpVbHS353E2m5O/hf_20260626_210730_cb5124a3-c1d8-45a9-a5f3-0ddc8449c680.mp4"),
    ("11_wifi_router",       "https://d8j0ntlcm91z4.cloudfront.net/user_3EP9SP2r5iXI2tpVbHS353E2m5O/hf_20260626_210836_0ec938c3-49a8-4d73-a77c-6465dfa10d60.mp4"),
    ("12_flower_pot",        "https://d8j0ntlcm91z4.cloudfront.net/user_3EP9SP2r5iXI2tpVbHS353E2m5O/hf_20260626_210748_c6135ff0-0aff-484f-9090-4c6a4efc78fc.mp4"),
    ("13_motion_sensor",     "https://d8j0ntlcm91z4.cloudfront.net/user_3EP9SP2r5iXI2tpVbHS353E2m5O/hf_20260626_210745_d72a17de-e18b-4ca0-a017-fbf3b5411996.mp4"),
    ("14_air_freshener",     "https://d8j0ntlcm91z4.cloudfront.net/user_3EP9SP2r5iXI2tpVbHS353E2m5O/hf_20260626_210733_4e6d96ed-366b-4a39-9d8b-9cd1d9874150.mp4"),
    ("15_shampoo_bottle",    "https://d8j0ntlcm91z4.cloudfront.net/user_3EP9SP2r5iXI2tpVbHS353E2m5O/hf_20260626_210847_7c9635ab-fb14-40eb-9de8-7f556e0ebbb6.mp4"),
    ("16_bathroom_detector", "https://d8j0ntlcm91z4.cloudfront.net/user_3EP9SP2r5iXI2tpVbHS353E2m5O/hf_20260626_210849_9470b9b0-b1cb-4bbb-b0bc-09f6380839b0.mp4"),
    ("17_spy_glasses",       "https://d8j0ntlcm91z4.cloudfront.net/user_3EP9SP2r5iXI2tpVbHS353E2m5O/hf_20260626_210754_0ef84519-3b65-4833-9366-b72397f1bcb5.mp4"),
    ("18_spy_pen",           "https://d8j0ntlcm91z4.cloudfront.net/user_3EP9SP2r5iXI2tpVbHS353E2m5O/hf_20260626_210756_fbe73caa-ebb4-4525-990b-582dd7f1ba8c.mp4"),
    ("19_teddy_bear",        "https://d8j0ntlcm91z4.cloudfront.net/user_3EP9SP2r5iXI2tpVbHS353E2m5O/hf_20260626_210751_034e2c3c-2bf1-4e7b-9aee-a33e6e338738.mp4"),
    ("20_detect_flashlight", "https://d8j0ntlcm91z4.cloudfront.net/user_3EP9SP2r5iXI2tpVbHS353E2m5O/hf_20260626_210801_7abc6499-e2d0-446f-a25d-c97c07f62194.mp4"),
    ("21_detect_rf",         "https://d8j0ntlcm91z4.cloudfront.net/user_3EP9SP2r5iXI2tpVbHS353E2m5O/hf_20260626_210804_8687b739-966c-4b69-b0a6-7b823335a5aa.mp4"),
    ("22_detect_app",        "https://d8j0ntlcm91z4.cloudfront.net/user_3EP9SP2r5iXI2tpVbHS353E2m5O/hf_20260626_210807_aa747d9b-e14f-4c1d-8dff-e8326eb83c2c.mp4"),
    ("23_splitscreen",       "https://d8j0ntlcm91z4.cloudfront.net/user_3EP9SP2r5iXI2tpVbHS353E2m5O/hf_20260626_210811_74153612-4d8c-4d77-8768-56a310316832.mp4"),
    ("24_checklist",         "https://d8j0ntlcm91z4.cloudfront.net/user_3EP9SP2r5iXI2tpVbHS353E2m5O/hf_20260626_210817_84e07e73-6ea6-4857-afe4-bab3e348c8cc.mp4"),
    ("25_outro",             "https://d8j0ntlcm91z4.cloudfront.net/user_3EP9SP2r5iXI2tpVbHS353E2m5O/hf_20260626_210814_f0ba6e75-c152-4dcf-be18-e01eefda4086.mp4"),
]

AUDIO_FILES = [
    ("voiceover_full", "https://d8j0ntlcm91z4.cloudfront.net/user_3EP9SP2r5iXI2tpVbHS353E2m5O/hf_20260626_224346_988b8b15-4de3-4fc7-bae9-bdcbaf89d8e4.mp3"),
]


def download(url, path):
    if os.path.exists(path):
        print(f"  [skip] {os.path.basename(path)} already downloaded")
        return
    print(f"  ↓ {os.path.basename(path)}...")
    r = requests.get(url, stream=True, timeout=120)
    r.raise_for_status()
    with open(path, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 256):
            f.write(chunk)
    print(f"    ✓ {os.path.getsize(path) // 1024} KB")


def main():
    # 1. Download everything
    print("\n=== Downloading video clips ===")
    video_paths = []
    for name, url in VIDEO_CLIPS:
        path = os.path.join(OUTPUT_DIR, f"{name}.mp4")
        download(url, path)
        video_paths.append(path)

    print("\n=== Downloading audio ===")
    audio_paths = []
    for name, url in AUDIO_FILES:
        path = os.path.join(OUTPUT_DIR, f"{name}.mp3")
        download(url, path)
        audio_paths.append(path)

    # 2. Concatenate all video clips (silent)
    print("\n=== Concatenating video clips ===")
    clips = [VideoFileClip(p).without_audio() for p in video_paths]
    combined_video = concatenate_videoclips(clips, method="compose")
    print(f"  Total video duration: {combined_video.duration:.1f}s")

    # 3. Load audio
    print("\n=== Loading voiceover audio ===")
    audio_parts = [AudioFileClip(p) for p in audio_paths]
    combined_audio = audio_parts[0]
    print(f"  Audio duration: {combined_audio.duration:.1f}s")

    # 4. Attach audio to video (audio drives the length; video loops/pads if needed)
    print("\n=== Merging audio into video ===")
    # If audio is longer than video, loop last clip to fill
    if combined_audio.duration > combined_video.duration:
        extra = combined_audio.duration - combined_video.duration
        last_clip = VideoFileClip(video_paths[-1]).without_audio()
        loops_needed = int(extra / last_clip.duration) + 1
        padding = [last_clip] * loops_needed
        combined_video = concatenate_videoclips(clips + padding, method="compose")

    final = combined_video.with_audio(combined_audio)

    # 5. Export
    output_path = os.path.join(OUTPUT_DIR, "HIDDEN_CAMERAS_FINAL.mp4")
    print(f"\n=== Exporting → {output_path} ===")
    final.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=24,
        preset="fast",
        threads=4,
    )

    print(f"\n✅ Done! Final video saved to: {output_path}")
    print(f"   Duration: {final.duration:.1f}s  |  Size: {os.path.getsize(output_path) // (1024*1024)} MB")

    # Cleanup clips from memory
    for c in clips:
        c.close()
    for a in audio_parts:
        a.close()


if __name__ == "__main__":
    main()
