# HEYGEN SCRIPT — "STAY UGLY, STAY ALIVE" (Unhinged Survival Hacks Anthem)

Comment-section commentary music video with a hanging avatar.
Each scene below maps to a comment card PNG in `comment_cards/out/`.

## Setup (do once)

**Avatar (upload as Photo Avatar / Avatar IV).** Generate or draw this image first:

> Cute cartoon mascot girl with huge expressive eyes, bold pink-and-black outfit,
> hanging from the TOP of the frame gripping a rope with both hands, body dangling,
> legs swinging loose, mischievous grin, plain solid background, face fully visible
> and front-facing, 9:16 vertical

- **Voice:** young female, sassy, fast, expressive. Speed 1.1x.
- **Format:** 9:16, 1080x1920. Auto-captions ON (word-by-word pop style).
- **Music bed:** upbeat girly pop/hyperpop instrumental at ~20% volume.
- **Overlay per scene:** the matching card PNG pops in when the line starts.

## Scenes

| # | Card | Mood | Spoken script |
|---|------|------|---------------|
| 1 | card_01 | drops into frame, wide-eyed grin | Ladies... the comment section just wrote a whole survival anthem. Rule number ONE: be as DISGUSTING as you can be. You can wash it all off later... alive. |
| 2 | card_02 | urgent, leaning in | Don't scream HELP — nobody's coming. Scream FIRE!... and watch the whole block come running. |
| 3 | card_03 | deadly serious | Or scream MOM. I'm dead serious. Every mother in a MILE goes absolutely furious. |
| 4 | card_04 | shaking head | Never yell "leave me alone" — folks think it's a lovers' spat. Yell "I DON'T KNOW YOU!"... strangers ACTIVATE for that. |
| 5 | card_05 | goes limp, dangling | If he tries to grab you? DROP. Go limp. Lay down. It takes BOTH his hands to move you... and your mouth still makes sound. |
| 6 | card_06 | full chaos, feral | Be as disgusting as you can BE! Spit. Slobber. BARK. Sing gibberish off-key. You can wash it ALL off later... alive. Stay ugly, stay loud, stay weird — SURVIVE. |
| 7 | card_07 | smug, innocent shrug | Keep a bat in the car — but pack the glove and ball. Premeditated? No officer... I had PRACTICE, that's all. |
| 8 | card_08 | stage-whisper, then shout | Talk to your cat like a roommate — LOUD: "I'M HOME BABE, DON'T WAIT UP!" Now every neighbor's certain... somebody BIG lives up. |
| 9 | card_09 | sly | Decoy wallet, five fake bucks — here, TAKE it. And my tip money rides in a to-go box... "just leftovers." They HATE it. |
| 10 | card_10 | wink, finger over lips | Secret fund he'll NEVER find. And your name? To strangers, honey... lie, lie, LIE. |
| 11 | card_11 | calm, sincere (slow down) | And from a REAL nine-one-one operator... write this down. Don't know where you are? Mile markers. Exit signs. Store names... THAT'S how you get found. |
| 12 | card_12 | relieved hug gesture | Stranger creeping? Find the nearest auntie: "MOM! This guy's bothering me!"... Congratulations. You've been adopted. |
| 13 | card_13 | peak feral, swinging | One more time! Be as disgusting as you can BE — you can wash it all off later... ALIVE. And trust your gut, it's a SUPERPOWER. If it feels off?... It IS off. |
| 14 | card_14 | sweet smile, yanked up out of frame | Drop YOUR most unhinged survival hack in the comments... and you might just make part two. Stay sexy. Stay feral. Stay ALIVE. |

Runtime ~1:50. For a 60s Shorts/TikTok cut use scenes 1-6 + 14.
If the HeyGen voice supports break tags, replace "..." with `<break time="0.4s" />`.
For a true sung version: generate the song separately with these lines as lyrics,
then use HeyGen's upload-audio option instead of TTS.

## Regenerating the cards

```
NODE_PATH=/opt/node22/lib/node_modules node comment_cards/render.js
```

Outputs transparent-background overlay cards `out/card_01.png` ... `card_14.png`
plus `out/feed_screenshot.png` (full comment-section screenshot). Edit the CARDS
array in `render.js` to change text, handles, or like counts.
