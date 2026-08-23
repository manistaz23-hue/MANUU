# 03 · Style bible

One look, locked, for every episode forever. Consistency across episodes is what makes a
feed of clips read as a channel instead of a pile of AI videos.

## THE STYLE FORMULA (paste byte-identical into every image and video prompt)

This block is the entire consistency mechanism. Do not paraphrase it, do not "improve" it
per episode, do not translate it. Copy it exactly, every time, into every prompt.

```
flat 2D vector cartoon with uniform medium-weight rounded black outlines, soft airbrushed
radial gradients filling every shape, oversized glossy white cartoon eyes with black
pupils and thick expressive black eyebrows, small simple mouths, bodies built from smooth
rounded organic blobs with one soft highlight each. Warm anatomical palette of salmon
pink, coral and dusty rose against a dark chocolate-brown vignetted gradient background,
one lime-green accent reserved for food, no texture, no brush strokes, no photographic
detail, crisp clean edges, simple limited animation on twos.
```

97 words. Non-photorealistic, which the generation stack requires.

## PALETTE LOCK

Write this line into every prompt directly under the style formula:

```
PALETTE LOCK: use ONLY these colors — outline #1A1A1A, flesh #F2A891, flesh shadow
#E8836B, deep tissue #C25B52, cavity #7A2E2A, background gradient #3B2622 to #1E1412,
eye white #FFFFFF, food accent #8CC63F. No new or foreign colors, no colored or painted
backgrounds that are not in the references, no recolored characters.
```

The lime `#8CC63F` is the signature accent and it is **reserved for whatever the human
just ate**. Nothing else in frame is ever green. When a chocolate donut is the subject,
the accent shifts to that episode's food color and *nothing else in frame uses it* — the
rule is "one color belongs to the food", not "the food is green."

## Frame and format

| Property | Locked value |
|---|---|
| Aspect | 9:16 |
| Delivery resolution | 1080×1920 |
| Generation resolution | 720p, upscaled at assembly |
| Frame rate | 24 fps (matches the reference; also cheapest) |
| Duration | 60 s standard, 70 s max, 40 s minimum |
| Audio | AAC, 128 kb/s, mono is fine, −16 LUFS |

## Camera

Deliberately boring, because the comedy is in the writing:

- **Locked-off or micro-drift only.** No dolly, no orbit, no parallax, no "cinematic"
  anything. One camera behavior per shot, stated once.
- **Two framings exist:** MEDIUM (character fills ~60% of frame height) and CLOSE (eyes
  and eyebrows fill the frame). A third, WIDE, is used only for the cavity establishing
  shot at the top of a new location.
- **Cut on the line, not in the middle of it.** Every cut lands on a speaker change.
- **The reaction shot is the joke.** Budget one silent 1.5 s reaction per 10 s block —
  a character looking at the camera saying nothing is the highest-value frame in this
  format.

## The four locations

Every episode is staged in some subset of these. They are generated once and reused
forever (see `prompts/locations/`).

| Location | Description | Owner |
|---|---|---|
| `esophagus` | A vertical pink tube receding upward into darkness, dark brown gradient behind | Pipes |
| `stomach` | A curved bean-shaped cavity, pink walls, pooled liquid at the bottom | Gut |
| `brain_room` | A dark red veiny chamber with a pink lobed brain standing in it, a wall-mounted green button, a hanging monitor | HQ |
| `mouth_gate` | Interior of a mouth looking out past white teeth, uvula hanging center | Yuvi |
| `basement` | A dark coiled tunnel, low amber light, ominous | Rusty |

Coverage angle rule: never open two consecutive blocks on the same framing of the same
location. If block 3 and block 4 are both in the stomach, block 4 opens on a close, not
the establishing wide.

## The top caption (the format's signature element)

A single static text plate, top-center, present from frame 1 to the last frame, never
animated, never changed mid-video.

| Property | Value |
|---|---|
| Copy | `Eating {FOOD} right now:` — always this construction |
| Position | top-center, y = 7% of frame height |
| Font | a heavy grotesque (Arial Black / Archivo Black / Inter ExtraBold) |
| Size | ~44 px at 1080 wide |
| Color | white `#FFFFFF` |
| Shadow | 2 px hard drop shadow at 60% black, no glow, no box |
| Wrap | one line; if the food name is long, shorten the food name, not the font |

**This is a title plate, not a subtitle.** It is authored by you, burned at assembly, and
has nothing to do with speech captions. If you ever add speech captions, those are a
separate pass with a different tool and word-level timing from the audio — never hand-timed.

House variants of the construction, in order of preference:

1. `Eating {FOOD} right now:` — the default, matches the reference
2. `{TIME} and she just ate {FOOD}:` — for the sad-realism vein
3. `POV: you just sent down {FOOD}:` — use sparingly, it is the most worn-out construction

## Do-not list

- No lens flares, depth of field, film grain, bloom, or any photographic effect
- No 3D shading or specular highlights beyond the single soft blob highlight
- No text anywhere in frame except the top caption plate
- No music bed under dialogue. The reference has none and it is right — music kills
  comic timing in a two-hander.
- No trending-audio overlay. This format's audio IS the content.
- No watermarks, no channel bug, no end card. The kicker is the last frame.
