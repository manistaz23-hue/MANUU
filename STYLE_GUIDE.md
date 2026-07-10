# Zack-D-Style Real Stories — Channel Style Guide

The format: **short vertical videos (45–60s) in a soft, stylized 3D-animation look,
narrated calmly, each one telling a TRUE weird story that actually happened.**

## The formula (why Zack D. Films works)

1. **Hook in the first line** — state the impossible thing immediately.
   "In 1978, a scientist put his head inside a running particle accelerator… and survived."
   No intro, no branding, no "in this video".
2. **One story per video.** Never two. Never a list.
3. **Calm, matter-of-fact narration.** The weirdness carries the emotion; the voice never does.
4. **Simple words, short sentences.** Write for a 12-year-old listening at 1x while walking.
5. **Escalate block by block.** Each ~10s beat adds one new fact that raises the stakes.
6. **End on the payoff twist** — the single most unbelievable detail, saved for last.
   (Bugorski: the paralyzed half of his face never aged.)
7. **Visuals are stylized 3D, never real footage.** Smooth rounded characters, matte
   clay-like surfaces, muted palette, soft cinematic light. Non-photoreal — clearly animated.
8. **TRUE stories only.** Every fact verified against at least two sources before scripting.
   No invented quotes, no invented numbers. Keep a Sources list in every script.

## Production settings (fixed per video)

| Setting  | Value |
|---|---|
| Length   | 60s = 6 blocks × 10s (Higgsfield explainer workflow) |
| Aspect   | 9:16 vertical, 720×1280 |
| Style key| One `nano_banana_pro` image, attached to every clip |
| Clips    | `gemini_omni`, 10s, 720p, style key as image reference |
| Voice    | `seed_audio`, same deep calm male preset on every block |
| Assembly | `explainer_video` tool, blocks in order, no subtitles |

## STYLE descriptor (paste into every prompt)

> soft stylized 3D animation, smooth rounded simplified characters, matte clay-like
> surfaces, muted natural palette (desaturated teal, warm beige, slate gray, one deep
> red accent), soft cinematic key light with cool ambient fill, shallow depth of field,
> slight film grain, non-photorealistic, stylized animation, not a photo, no live-action

## Narration rules (per 10s block)

- ~20–24 words per block ≈ 8–9 seconds of speech.
- Plain spoken text only. No stage directions, no parentheticals.
- Spell numbers out: "nineteen seventy-eight", "two hundred thousand".
- Block 1 = hook. Block 6 = payoff twist.

## Ethics line

Real people are involved. Stick to documented facts, avoid mockery, avoid gore
close-ups, and prefer stories where the subject survived or history has settled.
