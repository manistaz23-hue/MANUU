# 01 · Reference teardown

Beat-by-beat analysis of the source video (`snaptik_7673275057497459982`) that this
channel is modeled on. Everything downstream in this repo is derived from these numbers.

## Hard specs

| Property | Value |
|---|---|
| Duration | 71.25 s |
| Container | H.264 High, yuv420p, bt709 |
| Frame | 720×1280, 9:16, 24 fps |
| Video bitrate | 292 kb/s (it is flat vector — it compresses to nothing) |
| Audio | HE-AACv2, 44.1 kHz stereo, 64 kb/s |
| Beats | 30 distinct dialogue beats |
| Average beat | 2.37 s |
| Longest beat | 6 s (one) — everything else is 1–4 s |
| Speaking characters | 5 (Esophagus, Stomach, Brain, Uvula, a lettuce leaf) |
| On-screen text | ONE static line, top-center, unchanged for the whole video |
| Music | none |
| Captions | none (no speech subtitles at all) |

## The structure

The video is a **workplace sitcom staged inside a digestive tract**. It is not an
explainer and it is not narration. It is four coworkers on a shift, and the food is an
intruder. That framing is the whole engine — every laugh comes from organs behaving like
underpaid staff, not from anatomy facts.

Beat map (timestamps from the source):

| # | Time | Beat | Function |
|---|---|---|---|
| 1 | 0:00–0:03 | Esophagus warns Stomach a delivery is coming | **Hook** — a two-hander opens cold, no intro |
| 2 | 0:03–0:09 | Stomach asks what it is; Esophagus says "salad… lettuce or something" | **Name the food by 0:09** |
| 3 | 0:09–0:15 | Stomach hears "lettuce", explodes, orders it sent back | **Refusal** — the comic engine |
| 4 | 0:15–0:23 | Esophagus can't stop it; lettuce falls in anyway | **It's already here** |
| 5 | 0:24–0:34 | Stomach escalates to Brain | **Call HQ** |
| 6 | 0:34–0:42 | Brain pulls out a phone to look it up, more lettuce lands mid-search | **HQ is too late** |
| 7 | 0:43–0:47 | A lettuce leaf itself talks back ("we in here now") | **The food gets a voice** |
| 8 | 0:47–0:57 | Stomach demands the gag reflex; Brain reaches for a physical green button | **The plan** |
| 9 | 0:57–1:03 | Uvula interrupts from the mouth, cares about the wrong thing | **Cameo derail** |
| 10 | 1:04–1:06 | Cutaway to a "security monitor" of the human still eating salad | **The plan fails** |
| 11 | 1:07–1:12 | Stomach, exhausted, deadpans the kicker | **Payoff** |

Eleven story beats, thirty shots, seventy seconds. That ratio is the format.

## What actually makes it work

1. **The cold open has no intro.** First line of dialogue is already the plot. No logo,
   no "hey guys", no narrator setup.
2. **The top caption does all the exposition.** `Eating lettuce right now:` sits there
   the entire video. A viewer who scrolls in at 0:40 still understands everything. It is
   also the hook, the title and the SEO in one element.
3. **Two speakers at a time, never more.** The cast is five, but every exchange is a
   two-hander. A new character enters only when the previous pairing has run dry.
4. **The organs have jobs, not organs' functions.** Esophagus is a delivery driver.
   Brain is a manager with a phone. Uvula is the guy near the front door who doesn't
   work there. Anatomy is the setting; office politics is the comedy.
5. **The food fights back.** Around 60% in, the ingested item becomes a character with
   its own voice. This is the single best structural idea in the reference — it turns a
   complaint into a conflict.
6. **The animation is almost nothing.** Eyes move, eyebrows move, a mouth flaps, objects
   fall. The backgrounds are static gradients. Every dollar of production is in the
   writing and the voice performance. This is why the format is viable with AI at all.
7. **The kicker is anatomical doom, delivered flat.** The last line is the darkest one,
   said with no energy. Escalate for 60 seconds, then undercut.

## What we deliberately change

See `02-americanization.md`. The short version:

- The reference is already American — it is Black American comedic voice, AAVE-inflected,
  heavily profane. "Appeal to Americans" therefore does **not** mean translating it. It
  means building a version that (a) runs on American food culture as its topic engine,
  (b) can be posted on a monetizable US account, and (c) is repeatable weekly by one
  person with AI tools.
- The profanity is the one thing that has to move. See the swap table in `02`.
- The subject rotates every episode; the cast never does. That is what turns one viral
  video into a channel.
