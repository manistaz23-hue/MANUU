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

## Word budget — the number that actually matters

A 10-second block with two speakers trading turns needs **22–26 spoken words total**.

Why that band:
- Conversational American delivery runs ~2.6–2.9 words per second.
- Two speakers taking three or four turns burns ~1.2 s in turn-taking gaps.
- 24 words ÷ 2.7 wps ≈ 8.9 s of speech + 1.1 s of gaps = a full 10 s block.

| Words in a block | Result |
|---|---|
| under 20 | dead air; the block reads as a slideshow |
| 22–26 | **correct** |
| 27–30 | rushed, the model swallows syllables |
| over 30 | the model truncates the last turn entirely |

Enforce it with `pipeline/validate_episode.py` before you spend a single credit.

Sub-budgets:
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
- [ ] Every block 22–26 words, ≤2 speakers, 3–4 turns
- [ ] Block 1's first line ≤8 words, and names the food by the end of block 1
- [ ] Every block is a disagreement
- [ ] Through-line object named and in all 6 blocks, escalating monotonically
- [ ] One physical event per block
- [ ] Kicker ≤6 words, flat, no exclamation
- [ ] No banned filler, no repeated 5-word phrase across blocks
- [ ] Strongest word in the episode is "hell" or "damn", used at most once
- [ ] No health claim stated as fact by a reliable-sounding character
- [ ] `python3 pipeline/validate_episode.py episodes/epNN-*.json` exits 0
