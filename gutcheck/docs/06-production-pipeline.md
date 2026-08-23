# 06 · Production pipeline

How one episode goes from a written script to a finished 1080×1920 mp4.

Everything here runs through the Higgsfield MCP tools available in this session. Model
choices are fixed — substituting a model breaks look consistency across episodes, which
is the one thing this channel cannot afford.

## Fixed stack

| Job | Tool | Model | Fixed params |
|---|---|---|---|
| Style key + all art assets | `generate_image_batch` | `seedream_v5_pro` | `resolution:"1k"` |
| Animated dialogue blocks | `generate_video_batch` | `gemini_omni` | `duration:10`, `resolution:"720p"`, `aspect_ratio:"9:16"` |
| Narrator voice (Route B only) | `generate_audio_batch` | `text2speech_v2` | `variant:"elevenlabs"`, one locked `voice_id` + `voice_type` |
| Waiting | `jobs_wait` | — | groups of ≤12 |
| Reviewing results | `show_generation_by_ids` | — | one call, exact ids, ≤60 |
| Assembly / encode | `sandbox_exec` | — | ffmpeg inside the sandbox |
| Delivery | `media_upload` → PUT → `media_confirm` | — | upload with `--upload-file`, never `--data-binary` |

Batch caps that are real and will bite you: **≤12 requests per batch call**, **≤12 jobs
per `jobs_wait` group**, **≤7 `image_references` per video call**.

---

## Phase 0 — Once per channel, never again

You do this on the first episode and then reuse the job ids forever.

### 0a. The style key

One `generate_image_batch` call, one request, `seedream_v5_pro`, `resolution:"1k"`,
`aspect_ratio:"9:16"`. Prompt is `prompts/style-key.txt`.

Attach a house style card as the `image_references` donor so the render does not drift.
Resolve the card id with `resolve_explainer_preset` and pass the returned `media_id`:

- **Pastel Flat 2D** — `d0708b4f-a134-40f7-9884-9ad830904e71` (closest to our look, start here)
- **2D Illustrator** — `5a1ae304-c541-4f11-9784-595e0f2c3d2b` (legacy card; flatter, harder outlines — try if Pastel comes back too soft)

> **Do not use frames from the reference video as style donors.** Feeding another
> creator's actual frames in to clone their art is a different thing from writing your own
> formula in the same genre, and it is not a line worth crossing for a channel you intend
> to monetize. The formula in `03-style-bible.md` was written from scratch to sit in the
> same visual family. Use that.

Keep the returned `job_id`. It is the look anchor for every asset that follows.

### 0b. The cast and location sheets

One `generate_image_batch` call, up to 12 requests, `seedream_v5_pro`, `resolution:"1k"`.
Pass the style key `job_id` as `medias` (role `image`) on every request, and paste the
style formula byte-identical into every prompt.

| Index | Asset | Aspect | Prompt file |
|---|---|---|---|
| 1 | Gut (stomach) | 2:3 | `prompts/characters/gut.txt` |
| 2 | Pipes (esophagus) | 2:3 | `prompts/characters/pipes.txt` |
| 3 | HQ (brain) | 2:3 | `prompts/characters/hq.txt` |
| 4 | Liv (liver) | 2:3 | `prompts/characters/liv.txt` |
| 5 | Loops (small intestine) | 2:3 | `prompts/characters/loops.txt` |
| 6 | Rusty (colon) | 2:3 | `prompts/characters/rusty.txt` |
| 7 | Yuvi (uvula) | 2:3 | `prompts/characters/yuvi.txt` |
| 8 | Buzz (bladder) | 2:3 | `prompts/characters/buzz.txt` |
| 9 | Pancho (pancreas) | 2:3 | `prompts/characters/pancho.txt` |
| 10 | Stomach cavity | 9:16 | `prompts/locations/stomach.txt` |
| 11 | Esophagus tube | 9:16 | `prompts/locations/esophagus.txt` |
| 12 | Brain room | 9:16 | `prompts/locations/brain_room.txt` |

Second batch for the remaining locations and the standing props:

| Index | Asset | Aspect | Prompt file |
|---|---|---|---|
| 13 | Mouth gate | 9:16 | `prompts/locations/mouth_gate.txt` |
| 14 | Basement | 9:16 | `prompts/locations/basement.txt` |
| 15 | Green gag-reflex button | 1:1 | `prompts/props/gag_button.txt` |
| 16 | HQ's phone | 1:1 | `prompts/props/phone.txt` |
| 17 | The security monitor | 1:1 | `prompts/props/monitor.txt` |

Wait each batch with `jobs_wait` (groups of ≤12), then one `show_generation_by_ids` with
the exact ids. Record every `(name, job_id)` in `prompts/ASSET_IDS.md` — that file is the
channel's memory. Losing it means regenerating the whole cast and accepting drift.

**Check the sheets before moving on.** A character whose design you accept here is the
design you are stuck with for every future episode.

---

## Phase 1 — Per episode: write and validate

1. Write the episode as JSON in `episodes/epNN-slug.json` (schema in
   `episodes/SCHEMA.md`, twelve worked examples already in the folder).
2. Run the gate:
   ```
   python3 pipeline/validate_episode.py episodes/epNN-slug.json
   ```
   It checks block count, word budget, speaker count, turn count, the ≤8-word cold open,
   the through-line's presence in all six blocks, the kicker length, banned filler, cross-
   block phrase repeats and the profanity ceiling. **Exit code 1 means do not generate.**
   Rewrite the reported lines; never widen the band to make the gate pass.

---

## Phase 2 — Per episode: build the block prompts

```
python3 pipeline/build_payloads.py episodes/epNN-slug.json --assets prompts/ASSET_IDS.md
```

Emits `build/epNN/video_batch.json` — a ready `generate_video_batch` payload with six
indexed requests, and `build/epNN/blocks/blockNN.txt` for eyeballing.

Each block prompt is the template in `prompts/block-dialogue.txt`, filled in. Its shape:

```
Style: {STYLE FORMULA verbatim}; simple limited animation on twos — the visual style is
EXACTLY as in the reference images, same rendering, same surface treatment.
PALETTE LOCK: {palette lock verbatim}
A single 10-second scene of FOUR hard-cut shots. Do NOT open on a reference image or show
a sheet. Motion starts on frame 1, no opening freeze.
REFERENCES: @Image1 = LOCATION (...). @Image2 = GUT (...). @Image3 = PIPES (...).
@Image4 = PROP (...).
DIALOGUE — only these two characters speak, these exact words, nothing else:
  PIPES: "..."
  GUT: "..."
  PIPES: "..."
SHOT 1 — 0.0s to 2.5s — MEDIUM, eye level: {beat}.
HARD CUT.
SHOT 2 — 2.5s to 5.0s — CLOSE, low angle: {beat}.
HARD CUT.
SHOT 3 — 5.0s to 7.5s — MEDIUM, high angle: {beat}.
HARD CUT.
SHOT 4 — 7.5s to 10.0s — CLOSE on eyes: {payoff beat}.
AUDIO: the two characters speaking their lines natively, plus {2-3 diegetic SFX}. No
narration, no music, no extra voices, no improvised words.
NEGATIVE: opening on a reference image, static first frame, leading freeze, dissolves,
fades, new or foreign colors, recolored characters, style drift, extra characters,
cloned characters, on-screen text, captions, photorealism, 3D render, watermark.
```

Notes that matter:

- **Four cuts, not five.** The standard block grammar is five ~2 s cuts, but dialogue
  needs room — four 2.5 s shots gives each turn a frame to land on. This is the one
  deliberate deviation from the house grammar and it is worth it for a two-hander.
- **Only two named characters may speak per block.** Naming a third is how you get
  garbled overlapping audio.
- **Quote the lines exactly** and forbid improvisation explicitly. The model will
  otherwise paraphrase.
- **≤7 image references.** Location + two characters + prop = 4. You have headroom; do
  not spend it on decoration.

---

## Phase 3 — Generate the blocks

Submit `build/epNN/video_batch.json` through `generate_video_batch` — six indexed
requests in one call. Then `jobs_wait` on all six.

Two failure modes you will hit, both routine:

- **`submission_failed` with a `preset_recommendation`.** Resubmit only that index with
  `declined_preset_id` set to `preset_recommendation.preset_id`. Do not change anything else.
- **`nsfw`.** This format triggers false positives — the prompts describe internal organs.
  Resubmit the same index with a new seed up to three times, then reword: drop anatomical
  nouns in favor of the character names, avoid tight close-ups on wet surfaces, calm the
  pose. Never drop a block and ship a five-block episode.

When all six are `completed`, one `show_generation_by_ids` with the exact ids. Then
**watch block 1 against the character sheets.** Block 1 is generated with the least
context and drifts most; a Gut that came back the wrong shade is a regenerate, now, before
you assemble anything.

Also count the cuts per block:

```
ffprobe -v error -select_streams v:0 -show_entries frame=pkt_pts_time -of csv=p=0 \
  -f lavfi "movie=blockNN.mp4,select=gt(scene\,0.15)" | wc -l
```

Use the `0.15` threshold, not `0.3` — flat vector art changes too few pixels between
similar compositions and the default threshold under-reports. Treat a low count as a
suspicion to eyeball, not a verdict.

---

## Phase 4 — Route A vs Route B

**Route A — native dialogue (default).** The clips already contain the performed
dialogue with lip movement. Extract each clip's full audio, normalize to −16 LUFS, and
use it as that block's audio track. Never re-time it, never centre it, never stretch it —
the lips are locked to it.

Trade-off: a character's voice can shift between blocks, because each 10-second clip is
performed independently. Mitigation is visual, not audio: identical designs, identical
palette, identical framing language. Viewers forgive timbre drift far more readily than
they forgive a character changing shape.

**Route B — one narrator (fallback).** If a block fails Route A twice, or if you want
guaranteed voice consistency across a whole season, regenerate that block with
`characters only emote and gesture, they do NOT talk` in the prompt and put the lines
through `generate_audio_batch` (`text2speech_v2`, `variant:"elevenlabs"`) with a single
locked `voice_id` + `voice_type` performing every part. Write the pair into a file and
read it from the file before every audio call — resolving a voice by name mid-run is how
you end up with a different timbre in every block.

Route B costs the lip movement and gains total consistency. Mixing routes inside one
episode is fine; mixing them inside one block is not.

---

## Phase 5 — Assemble

```
bash pipeline/assemble_episode.sh --episode epNN-slug --blocks build/epNN/blocks
```

What it does, in order:

1. Probes the source fps and uses it (never hardcodes 30).
2. Concatenates the six 10-second blocks.
3. Normalizes audio to −16 LUFS.
4. Burns the static top caption plate from the episode JSON's `caption` field.
5. Scales to 1080×1920 and encodes H.264 High / yuv420p / AAC 128k, `+faststart`.
6. Asserts the output is within 0.5 s of `blocks × 10` and decodes end to end.

The caption plate is a **static title**, authored by you and burned here. It is not a
speech caption. If you ever add word-level speech captions, that is a separate pass with
timing derived from the audio — never hand-timed off the script.

---

## Phase 6 — Deliver

Upload from inside the sandbox:

```
media_upload → curl -f -X PUT --upload-file final.mp4 '<upload_url>' → media_confirm
```

Use `--upload-file`. `--data-binary @file` against a recycled sandbox silently uploads
nothing and still returns 200. Hand out the URL that `media_confirm` returned — not the
presigned upload URL, which is a different host and will 404.

---

## Cost and time per episode, roughly

| Item | Count |
|---|---|
| Image generations | 0 after the first episode (assets are reused) |
| Video generations | 6 (plus retries; budget 8) |
| Audio generations | 0 on Route A, 6 on Route B |
| Wall clock | 20–40 minutes, mostly waiting on the six clips |

The first episode carries the whole channel's asset cost. Episodes 2 through 100 are six
clips and an ffmpeg run.

---

## Failure playbook

| Symptom | Cause | Fix |
|---|---|---|
| Character looks different in one block | reference sheets not attached, or attached in the wrong order | Re-attach as location → characters → props, regenerate that block only |
| Block reads as a slideshow | shots running 3–5 s | Respell the cuts shot by shot with explicit timings, regenerate once |
| Dialogue is paraphrased | the "exact words, nothing else" clause got softened | Restore the clause verbatim, quote each turn on its own line |
| Third voice appears | a third character was named in the prompt | Remove them from `REFERENCES` too, not just from `DIALOGUE` |
| Audio and lips desync | the clip's native audio was re-timed | Never touch dialogue audio timing. Regenerate instead. |
| Colors drift green/blue | palette lock missing or paraphrased | Paste it byte-identical |
| Blocks won't submit | >12 in one batch, or >7 image refs | Split the batch; trim props first, never the location or a speaking character |
