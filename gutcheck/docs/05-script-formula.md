# 05 · The script formula

Every episode is six 10-second blocks. Sixty seconds, six blocks, one argument.

## The six-block spine

| Block | Role | What happens | Who speaks |
|---|---|---|---|
| 1 | **HOOK** | Pipes announces an incoming delivery. Gut asks what it is. The food is named before 0:09. | Pipes + Gut |
| 2 | **REFUSAL** | Gut hears what it is and refuses in the loudest possible terms. Orders it sent back. | Gut + Pipes |
| 3 | **IT'S ALREADY HERE** | Too late. The food lands. The food talks. | Gut + GUEST |
| 4 | **CALL HQ** | Gut escalates to HQ. HQ looks it up on the phone and delivers a fact that is either wrong, too late, or both. | Gut + HQ |
| 5 | **THE PLAN FAILS** | A countermeasure is attempted — the gag reflex, insulin, a shutdown — and a third organ derails it. | Gut + one of (HQ, Yuvi, Buzz, Pancho, Liv) |
| 6 | **PAYOFF** | The human is still eating. Gut goes flat. The kicker lands, usually from Rusty or from Gut's own deadpan. | Gut + (Rusty or nobody) |

Blocks 3 and 5 are where episodes differ from each other. Blocks 1, 2 and 6 are almost
formulaic on purpose — that repetition is what makes it a format viewers recognize on
the third video.

## Speech budget — the number that actually matters

**Budget in seconds, not words.** This was learned the expensive way: the first draft of
this channel used a 22–26 word band per block, derived from an assumed 2.7 words/sec.
Then ep01 was actually recorded, and the assumption fell apart.

Measured across 31 real takes:

| Voice | Character | Median words/sec |
|---|---|---|
| PTO Meme Voice | GUT | 3.28 |
| Benji | PIPES | 2.68 |
| Barrett | RUSTY | 2.93 |
| Cody | guest food | 2.63 |
| Emmett | HQ | 2.00 |
| Romy | YUVI | 1.65 |

That is a 2× spread. The same 24-word block runs 7.6 seconds in a GUT/PIPES pairing and
11.3 seconds in a GUT/YUVI pairing — one fits comfortably and one does not fit at all.
A word count cannot tell those apart, so it is the wrong unit.

**The budget, per 10-second block:**

| Speech in the block | Result |
|---|---|
| under 5.5s | dead air |
| 5.5 – 8.6s | **correct** — turn gaps land around 0.28s |
| 8.6 – 9.4s | fits, but gaps squeeze under 0.2s and it sounds crammed |
| over 9.4s | does not fit; the assembler will flag it |

Rates live in `voices.json` and `pipeline/validate_episode.py` gates against them.
**Re-measure and update that file whenever a voice is recast** — a stale rate silently
lets an over-long block through.

Two more things the recording taught us, both now in the estimator:

- **Sentence breaks cost real time.** "No. No. No." measured 2.88 seconds for three
  words. The pauses are the runtime. Each sentence break inside a turn is charged 0.35s.
- **Estimates carry about ±0.9s of line-to-line noise.** GUT came back anywhere between
  1.8 and 4.7 words/sec depending on the line. So once a block has actually been
  recorded, its `measured_speech` goes into the episode file and the gate uses that
  instead — measurement beats estimate, always.

Rough word counts still apply as a sanity band (16–28 per block), but they are a
smell test, not the gate.

Sub-budgets, unchanged:
- **Turns per block:** 3 or 4. Never 2 (too static), never 5 (too dense).
- **Longest single turn:** 12 words. If a line is longer, it is exposition — cut it.
- **Shortest turn:** 1 word is legal and often the funniest ("Lettuce?").
- **Block 1's first line:** 8 words or fewer. Cold open, no throat-clearing.

## Line-writing rules

1. **Every line is a disagreement.** If a character agrees with the previous line, the
   exchange is dead. Rewrite one of the two.
2. **The food's name lands in block 1.** A viewer who watches only three seconds must
   know what the video is about. The top caption backs this up.
3. **No exposition about anatomy.** Nobody explains what a pancreas does. If the joke
   needs the audience to know, the top caption tells them.
4. **No filler.** "You know", "I mean", "basically", "like", "um" are banned. They eat
   the word budget and read as AI padding.
5. **No content word repeated within six words** unless it is a deliberate triple
   ("no, no, no"), which is allowed once per episode.
6. **No phrase of five or more words repeats between two blocks.**
7. **Every block has one physical event** — something falls, slams, spills, buzzes, or
   gets pressed. Dialogue over a static frame is what makes AI comedy feel cheap.
8. **The kicker is short and flat.** Six words or fewer, no exclamation mark. The whole
   video escalates; the last line does not.

## The escalation ladder

Each block must be worse than the one before it in a way you can point at:

```
block 1  food is announced
block 2  food is refused              <- verbal escalation
block 3  food arrives anyway          <- physical escalation
block 4  authority is called, fails   <- institutional escalation
block 5  countermeasure backfires     <- tactical escalation
block 6  the human is STILL EATING    <- the reveal that none of it mattered
```

If two blocks could be swapped without loss, the episode is not escalating. Rewrite.

## The through-line object

Every episode has one physical object that appears in all six blocks and gets visibly
worse. In the reference it is the lettuce: one leaf → a handful → a flood → a leaf with a
face → a stomach full → the security monitor showing more coming.

Pick it in advance and name it in the episode file. It is also generated once as a prop
asset so it never redesigns itself mid-video.

| Block | Through-line state (example: burrito) |
|---|---|
| 1 | a distant foil-wrapped shape descending |
| 2 | close on it, comically large |
| 3 | it lands, unwraps, has a face |
| 4 | it has settled and expanded |
| 5 | a second one arrives |
| 6 | the monitor shows a third being ordered |

## Title and caption

The top caption and the post title are the same sentence:

```
Eating {FOOD} right now:
```

Write the food the way an American would say it out loud, not the way a menu spells it:
"a Chipotle bowl", "gas station taquitos", "five scoops of pre-workout", "a Costco hot
dog." Specific beats generic every time — "salad" is fine, "the sad desk salad at a work
lunch" is better.

## Quality gate before production

An episode is ready to shoot when all of these are true:

- [ ] Exactly 6 blocks
- [ ] Every block 5.5–8.6s of estimated speech, ≤2 speakers, 3–4 turns
- [ ] Block 1's first line ≤8 words, and names the food by the end of block 1
- [ ] Every block is a disagreement
- [ ] Through-line object named and in all 6 blocks, escalating monotonically
- [ ] One physical event per block
- [ ] Kicker ≤6 words, flat, no exclamation
- [ ] No banned filler, no repeated 5-word phrase across blocks
- [ ] Strongest word in the episode is "hell" or "damn", used at most once
- [ ] No health claim stated as fact by a reliable-sounding character
- [ ] `python3 pipeline/validate_episode.py episodes/epNN-*.json` exits 0
