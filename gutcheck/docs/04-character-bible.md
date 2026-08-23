# 04 · Character bible

The cast never changes. The food changes. That is the channel.

Nine recurring characters plus one guest per episode. Each has a job, a temperament, a
speech tic and a rule about when it may appear. The rules matter more than the designs —
a character that shows up for no reason is what makes a format feel random.

---

## GUT — the stomach
**Job:** shift manager. Runs the floor, takes every delivery personally.
**Temperament:** permanently at the end of a twelve-hour shift. Explodes fast, deflates
faster, ends every episode flat and defeated.
**Voice:** warm, loud, Southern-adjacent; drops to a dead monotone for the kicker.
**Tics:** "Absolutely not." · "Send it back." · repeats a word three times when panicking
("no, no, no").
**Appears:** every episode. Gut is the protagonist and the audience surrogate.
**Design:** bean-shaped coral organ, huge eyes, thick brows, small red mouth, visible
liquid line at the bottom that rises as the episode gets worse.

## PIPES — the esophagus
**Job:** delivery driver. Brings whatever HQ sends down. Has no authority and knows it.
**Temperament:** nervous, apologetic, conflict-avoidant, secretly enjoys the drama.
**Voice:** higher, faster, slightly whiny.
**Tics:** "I just work here." · "Don't shoot the messenger." · announces deliveries like
a dispatcher ("incoming, incoming").
**Appears:** every episode, almost always in block 1. Pipes opens the show.
**Design:** long vertical pink tube, eyes and brows set near the top, body flexes and
kinks when stressed.

## HQ — the brain
**Job:** middle management. Has a phone. Googles everything. Is always ninety seconds too
late to be useful.
**Temperament:** unbothered until it is far too late, then furious at everyone but itself.
**Voice:** flat, managerial, slightly bored; the only character who ever sounds calm.
**Tics:** "Let me look it up." · "That's above my pay grade." · reads phone results aloud
in a monotone.
**Appears:** most episodes, usually block 4. HQ arrives when Gut escalates.
**Design:** pink lobed brain with tiny arms and legs, standing upright in a dark red
veiny room, holding a small blue phone. A large round green button is mounted on the wall
behind it — the gag reflex.

## LIV — the liver
**Job:** night shift. Processes everything nobody else will touch.
**Temperament:** bitter, unionized, keeps receipts. Enters like someone being woken up.
**Voice:** dry, gravelly, sarcastic.
**Tics:** "Oh, so *now* y'all remember me." · "Put it on my tab." · sighs before speaking.
**Appears:** alcohol, energy drinks, pre-workout, anything at 2am. Never for vegetables.
**Design:** large dark reddish-brown wedge, heavy-lidded eyes, one permanently raised brow.

## LOOPS — the small intestine
**Job:** logistics. Absorbs everything, sorts nothing, enthusiastic about all of it.
**Temperament:** chaotic optimist. The only character having a good time.
**Voice:** fast, bright, over-caffeinated.
**Tics:** "I can work with this!" · "Ooh, what's THIS one?" · talks over Gut.
**Appears:** when food actually gets through. Loops is the "it's happening anyway" beat.
**Design:** long coiled pink tube filling the frame, several pairs of eyes along the coil.

## RUSTY — the colon
**Job:** last stop. Speaks approximately twice per episode, both times ominously.
**Temperament:** calm the way a weather warning is calm.
**Voice:** low, slow, unbothered.
**Tics:** "See y'all in twenty minutes." · "Noted." · never raises volume, ever.
**Appears:** payoff block only, and only in about half of episodes. **Overusing Rusty
kills Rusty.** Cap: no more than every other episode.
**Design:** dark coiled tunnel in low amber light, two calm eyes emerging from shadow.

## YUVI — the uvula
**Job:** none. Hangs by the front door. Does not work here.
**Temperament:** completely unbothered, invested in irrelevant details, vain.
**Voice:** light, smug, unhurried.
**Tics:** "It's *YOU-vyoo-la*, first of all." · corrects pronunciation mid-crisis ·
winks.
**Appears:** as a one-beat derail in block 5 when the plot needs a comic interruption.
Never carries a scene.
**Design:** red teardrop hanging in the center of a mouth interior, framed by white teeth.

## BUZZ — the bladder
**Job:** capacity management. Always at 3%.
**Temperament:** panicked, urgent, ignored by everyone.
**Voice:** high, tight, breathless.
**Tics:** "We're at capacity!" · "Nobody's listening to me." · counts down.
**Appears:** coffee, beer, soda refills, energy drinks.
**Design:** small round pale-pink balloon organ, wide eyes, sweat drop.

## PANCHO — the pancreas
**Job:** insulin. Physically throws it.
**Temperament:** starts professional, ends destroyed.
**Voice:** clipped, competent, then increasingly ragged.
**Tics:** "Insulin, going out." · "I'm cooked." · counts doses ("that's four").
**Appears:** sugar, soda, desserts, state fair food.
**Design:** small tan elongated organ with rolled sleeves, throwing small blue capsules.

---

## THE GUEST — the food
Every episode has exactly one guest: the thing that was just eaten, with a face and a
voice. It appears in block 3, speaks two to four lines total, and is unrepentant.

**Rules:**
- The guest is always **cheerful**, never menacing. The comedy is that it does not
  understand it is a problem.
- It has one distinguishing trait taken from the real food (a taquito is greasy and proud
  of it; a burrito is enormous and apologetic about nothing; an energy drink talks fast).
- It gets a dumb name that Gut mispronounces or gets wrong. The reference does this
  perfectly with "Romaine".
- It never leaves. Every attempt to remove it fails. This is the format's fixed point.
- It is rendered in the episode's accent color and is **the only thing in frame that
  color** (see the palette lock in `03-style-bible.md`).

---

## Casting rules per block

- **Two speakers per 10-second block, maximum.** Never three. The reference never does
  three and it is why every exchange lands.
- **Gut is in every block.** Gut is the through-line; the other characters rotate around it.
- **A new character enters only when the previous pairing is exhausted** — usually after
  two blocks.
- **The guest food speaks only after it has been seen falling.** Show it, then let it talk.
- **Never let two characters agree.** Every exchange is a disagreement, or it gets cut.

## Voice casting (production)

Two viable routes, covered in `06-production-pipeline.md`:

- **Route A (native dialogue):** the video model performs the lines itself, in-frame, with
  lip movement. Best match to the reference. Trade-off: a character's timbre can drift
  between blocks. Mitigate by keeping the visual identity rock solid — the eye carries
  what the ear cannot.
- **Route B (single narrator):** one locked voice performs all parts as an off-screen
  narrator, characters emote with mouths closed. Perfectly consistent, less like the
  reference, and much cheaper to fix when a line is wrong.

Start on Route A. Fall back to Route B for any block that fails twice.
