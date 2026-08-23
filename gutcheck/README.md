# Gut Check

A faceless AI video channel: a cast of cartoon organs arguing about what an American
just ate.

Modeled on the 71-second organ-comedy short in `docs/01-reference-teardown.md`, rebuilt
as something one person can ship three times a week — one locked cast, one locked look,
one script formula, twelve written episodes and a bank of twenty more.

```
Eating a Chipotle bowl right now:

  PIPES:  Incoming delivery. Real big one.
  GUT:    How big are we talking?
  PIPES:  Foil. Double wrapped. It's a burrito bowl.
  GUT:    With the guac? She paid extra again?
```

## The format in one table

| | |
|---|---|
| Length | 60 s — six 10-second blocks |
| Frame | 1080×1920, 9:16, 24 fps |
| Cast | 9 recurring organs + 1 guest food per episode |
| Per block | 4 hard cuts, 2 speakers, 3–4 turns, 5.5–8.6s of speech |
| Structure | hook → refusal → it's already here → call HQ → the plan fails → payoff |
| On-screen text | one static caption plate, top-center, unchanged for the whole video |
| Music | none — it kills comic timing in a two-hander |
| Per-episode cost after setup | 6 video generations and an ffmpeg run |

## Quickstart

**Once, for the whole channel** — generate the cast, the locations and the standing
props, then record their job ids in `prompts/ASSET_IDS.md`. Full call-by-call
instructions in `docs/06-production-pipeline.md` § Phase 0. That file is the channel's
memory; if it is lost, so is visual continuity.

**Per episode:**

```bash
# 1. gate the script before spending anything
python3 pipeline/validate_episode.py episodes/ep01-chipotle-bowl.json

# 2. record the dialogue FIRST — the performance sets the timing, and a line that
#    does not fit costs one audio job to fix here vs. six video jobs to fix later
#    (see docs/06 Phase 1b)

# 3. build the generation payloads
python3 pipeline/build_payloads.py episodes/ep01-chipotle-bowl.json
#    -> build/ep01-chipotle-bowl/video_batch.json   (6 indexed gemini_omni requests)
#    -> build/ep01-chipotle-bowl/guest_asset.json   (this episode's food, 1 image)
#    -> build/ep01-chipotle-bowl/blocks/*.txt       (the same prompts, readable)

# 4. submit the batch, wait for all six, download them as block01.mp4 … block06.mp4

# 5. assemble
bash pipeline/assemble_episode.sh \
     --episode episodes/ep01-chipotle-bowl.json \
     --blocks  build/ep01-chipotle-bowl/clips
#    -> out/ep01-chipotle-bowl.mp4
```

Route B (one narrator instead of in-clip dialogue):

```bash
python3 pipeline/build_payloads.py episodes/ep01-chipotle-bowl.json --route B \
        --voice-id <id> --voice-type preset
bash pipeline/assemble_episode.sh --episode episodes/ep01-chipotle-bowl.json \
     --blocks build/ep01-chipotle-bowl/clips --voices build/ep01-chipotle-bowl/voices
```

## Repo map

```
docs/
  01-reference-teardown.md   beat-by-beat analysis of the source video; every number below comes from here
  02-americanization.md      topic engine, voice register, profanity swap table, compliance guardrails
  03-style-bible.md          the locked style formula, palette lock, frame spec, camera rules, caption spec
  04-character-bible.md      the nine organs — job, temperament, voice, tics, and when each may appear
  05-script-formula.md       the six-block spine, word budgets, the escalation ladder, the quality gate
  06-production-pipeline.md  exact tool calls phase by phase, both routes, and the failure playbook
  07-publishing.md           titles, hashtags, cadence, retention structure, monetization, 20 more ideas

prompts/
  _STYLE.txt                 THE style formula — pasted byte-identical into every prompt
  _PALETTE.txt               the palette lock line
  style-key.txt              the one-time look anchor
  characters/*.txt           nine character sheets
  locations/*.txt            five locations
  props/*.txt                three standing props
  block-dialogue.txt         Route A block template (characters speak on camera)
  block-narration.txt        Route B block template (mouths closed, voice added in post)
  ASSET_IDS.md               the channel's memory — job ids for everything above

episodes/
  SCHEMA.md                  the episode JSON schema and every enforced band
  ep01..ep12*.json           twelve written episodes, all passing the gate

pipeline/
  validate_episode.py        the gate — run before spending credits
  build_payloads.py          episode JSON -> submittable generation payloads
  assemble_episode.sh        blocks -> finished 1080x1920 mp4 with the caption burned in
  make_caption.py            renders the static caption plate as a transparent PNG
  probe.py                   fps/duration, via ffprobe or via ffmpeg when ffprobe is absent
```

## Requirements

- `ffmpeg` (the assembler needs `overlay`; `drawtext` is used only as a fallback)
- `python3`
- `pillow` — `pip install pillow`, for the caption plate
- Access to the image/video/audio generation tools listed in `docs/06-production-pipeline.md`

`ffprobe` is used when present and worked around when it is not.

## The rules that actually matter

Everything else in `docs/` is elaboration on these six:

1. **The style formula is pasted byte-identical into every prompt.** It is the entire
   consistency mechanism. Paraphrasing it once is how a channel starts looking like a pile
   of unrelated AI clips.
2. **The cast never changes; the food does.** That is the difference between one viral
   video and a channel.
3. **Two speakers per block, never three.** The reference never breaks this and it is why
   every exchange lands.
4. **Budget in seconds, not words — and record the audio first.** The cast does not
   speak at one rate: measured over 31 takes, GUT runs 3.28 words/sec and YUVI 1.65, so
   the same 24-word block is 7.6s in one pairing and 11.3s in another. A 10s block holds
   5.5–8.6s of speech. `voices.json` carries the measured rates; re-measure on any recast.
5. **PG-13 ceiling.** The reference's profanity is a limited-ads flag on YouTube and a
   reach cap on TikTok. Keep the cadence, swap the words — table in `docs/02`.
6. **The last frame of the video is the last frame of the joke.** No end card, no outro,
   no "follow for more."

## Known limits, stated plainly

- **Voice timbre can drift between blocks on Route A.** Each 10-second clip is performed
  independently, so a character may not sound identical across six of them. Route B trades
  the on-camera lip movement for total voice consistency. Mixing routes across blocks is
  fine; mixing them inside one block is not.
- **The reference's art is not used as a style donor.** The formula in `docs/03` was
  written from scratch to sit in the same visual family. Feeding another creator's actual
  frames in to clone their look is a different thing, and not one worth doing on a channel
  you intend to monetize.
- **Only ep01's audio exists so far.** The other eleven episodes were written to the old word band and now fail the recalibrated seconds gate; they need a trim pass, which is deliberately held until the ep01 voice casting is approved (recasting a voice changes the rates and would invalidate the trims).
- **No episode has been rendered to video yet.** Every script passes the gate and every
  payload builds, but the visual side is unproven until the first cast sheet comes back.
  Budget the first episode as the one that also designs the channel.
