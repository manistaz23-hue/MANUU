# Episode schema

One JSON file per episode: `epNN-slug.json`. Validated by
`pipeline/validate_episode.py`, consumed by `pipeline/build_payloads.py`.

```jsonc
{
  "id": "ep01",                    // epNN, matches the filename
  "slug": "chipotle-bowl",         // kebab-case, matches the filename
  "vein": "fast food and chains",  // one of the four veins in docs/02
  "food": "a Chipotle bowl",       // as spoken; should appear inside `caption`
  "food_keywords": ["bowl", "guac"], // one of these MUST be spoken in block 1
  "caption": "Eating a Chipotle bowl right now:", // the static top plate, ≤42 chars, ends with ':'
  "title": "Eating a Chipotle bowl right now 🫠",  // the post title
  "hashtags": ["#foodtok", "#chipotle"],          // 3–5
  "accent_color": "#8CC63F",       // the ONE color reserved for this episode's food
  "kicker": "See y'all in twenty minutes.",       // ≤6 words, no '!', must be the last turn of block 6

  "through_line": {
    "name": "the foil-wrapped bowl",
    "prop_prompt": "…",            // generates the guest food asset; no brand names
    "progression": ["…", "…", "…", "…", "…", "…"]   // exactly 6, one per block, monotonically worse
  },

  "blocks": [                      // exactly 6
    {
      "n": 1,                      // 1..6, in order
      "role": "hook",              // hook, refusal, arrival, escalation, backfire, payoff — in that order
      "location": "esophagus",     // a key from prompts/locations/
      "characters": ["pipes", "gut"],   // every speaker must be listed here
      "props": ["burrito_bowl"],        // standing props or the episode's guest asset
      "through_line_state": "…",   // where the object is at this point
      "sfx": "…",                  // 2–3 diegetic cues; every block needs one physical event
      "shots": ["…", "…", "…", "…"],    // exactly 4, each "SIZE, angle: beat"
      "turns": [                   // 3–4, alternating, ≤2 distinct speakers, 22–26 words total
        {"speaker": "pipes", "line": "Incoming delivery. Real big one."},
        {"speaker": "gut",   "line": "How big are we talking?"}
      ]
    }
  ]
}
```

## Key namespaces

| Key kind | Where it resolves | Examples |
|---|---|---|
| Standing character | `prompts/characters/*.txt` → `prompts/ASSET_IDS.md` | `gut`, `pipes`, `hq`, `liv`, `loops`, `rusty`, `yuvi`, `buzz`, `pancho` |
| Location | `prompts/locations/*.txt` → `ASSET_IDS.md` | `esophagus`, `stomach`, `brain_room`, `mouth_gate`, `basement` |
| Standing prop | `prompts/props/*.txt` → `ASSET_IDS.md` | `gag_button`, `phone`, `monitor` |
| Guest asset | this episode's `through_line.prop_prompt` | `burrito_bowl`, `taco`, `wing`, `salad` — **any key not in the three lists above resolves to the episode's guest asset** |

The guest often has two keys in one episode — one for the object before it has a face
(`paper_bag` in the props array) and one for the character after it does (`taco` in the
characters array). Both resolve to the same generated asset. That is intentional: it is
one object, and it must not redesign itself when it starts talking.

## Hard bands (enforced by the validator)

| Field | Band |
|---|---|
| blocks | exactly 6, roles in fixed order |
| turns per block | 3–4, alternating speakers |
| distinct speakers per block | ≤2 |
| words per block | 22–26 |
| words in one turn | ≤12 |
| block 1's first line | ≤8 words |
| kicker | ≤6 words, no `!`, must be block 6's last turn |
| shots per block | exactly 4 |
| image refs per block | 1 location + characters + props ≤ 7 |
| consecutive blocks in one location | ≤2 |
| distinct locations per episode | ≥2 |
| mild profanity per episode | ≤1 |
| hard profanity | 0 |
| 5-word phrase shared between two blocks | 0 |

Warnings (repeated words inside a single turn) are usually deliberate comic echoes and
are fine to ship. Errors are not.
