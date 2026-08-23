#!/usr/bin/env python3
"""Gate an episode script before you spend a single generation credit.

Usage:
    python3 pipeline/validate_episode.py episodes/ep01-chipotle-bowl.json
    python3 pipeline/validate_episode.py episodes/*.json

Exit code 0 = shootable. Exit code 1 = rewrite the reported lines.

Every band here comes from docs/05-script-formula.md. Do not widen a band to make the
gate pass; the bands are what stop a block from reading as a slideshow or getting its
last turn truncated by the model.
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROLES = ["hook", "refusal", "arrival", "escalation", "backfire", "payoff"]

WORDS_MIN, WORDS_MAX = 22, 26
TURNS_MIN, TURNS_MAX = 3, 4
MAX_SPEAKERS_PER_BLOCK = 2
MAX_TURN_WORDS = 12
MAX_COLD_OPEN_WORDS = 8
MAX_KICKER_WORDS = 6
MAX_REFS_PER_BLOCK = 7
SHOTS_PER_BLOCK = 4
MAX_CONSECUTIVE_SAME_LOCATION = 2

FILLER = {"basically", "literally", "actually", "um", "uh", "kinda", "sorta"}
FILLER_PHRASES = ["you know", "i mean", "sort of", "kind of"]

# PG-13 ceiling: at most one of these in a whole episode.
MILD_PROFANITY = {"hell", "damn", "damned", "crap"}
# Never.
HARD_PROFANITY = {
    "fuck", "fucking", "fucked", "shit", "shitty", "bitch", "bastard",
    "asshole", "dick", "piss", "cunt", "motherfucker",
}

# Stated as fact by a character, these read as health claims rather than jokes.
CLAIM_PATTERNS = [
    r"\bstudies show\b", r"\bproven to\b", r"\bcauses\s+\w+\b",
    r"\bdoctors say\b", r"\bscientifically\b", r"\bgives you\b",
]

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "is", "are", "was", "were", "be", "been",
    "to", "of", "in", "on", "it", "its", "this", "that", "i", "you", "we", "they",
    "he", "she", "me", "my", "your", "our", "their", "for", "with", "at", "so",
    "no", "not", "do", "does", "did", "dont", "cant", "im", "its", "what", "who",
    "how", "why", "up", "out", "here", "there", "now", "just", "got", "get", "all",
}


def words(text):
    return re.findall(r"[a-z0-9']+", text.lower())


class Report:
    def __init__(self, path):
        self.path = path
        self.errors = []
        self.warnings = []

    def err(self, where, msg):
        self.errors.append(f"{where}: {msg}")

    def warn(self, where, msg):
        self.warnings.append(f"{where}: {msg}")

    def print(self):
        name = Path(self.path).name
        if self.errors:
            print(f"\n✗ {name} — {len(self.errors)} error(s)")
            for e in self.errors:
                print(f"    {e}")
        else:
            print(f"\n✓ {name} — shootable")
        for w in self.warnings:
            print(f"    ! {w}")
        return not self.errors


def check_structure(ep, r):
    for field in ("id", "slug", "food", "caption", "title", "through_line", "blocks", "kicker"):
        if field not in ep:
            r.err("episode", f"missing required field '{field}'")
    blocks = ep.get("blocks", [])
    if len(blocks) != len(ROLES):
        r.err("episode", f"has {len(blocks)} blocks, needs exactly {len(ROLES)}")
    for i, b in enumerate(blocks, start=1):
        if b.get("n") != i:
            r.err(f"block {i}", f"'n' is {b.get('n')}, expected {i}")
        if b.get("role") != ROLES[i - 1]:
            r.err(f"block {i}", f"role is '{b.get('role')}', expected '{ROLES[i-1]}'")


def check_caption(ep, r):
    caption = ep.get("caption", "")
    if not caption.endswith(":"):
        r.err("caption", "must end with a colon — it is a lead-in, not a sentence")
    if len(caption) > 42:
        r.err("caption", f"{len(caption)} chars; shorten the food name so it fits one line (≤42)")
    food = ep.get("food", "").lower()
    if food and food not in caption.lower():
        r.warn("caption", f"does not contain the food string '{food}'")


def check_through_line(ep, r):
    tl = ep.get("through_line", {})
    prog = tl.get("progression", [])
    if len(prog) != len(ROLES):
        r.err("through_line", f"progression has {len(prog)} states, needs {len(ROLES)}")
    if not tl.get("name"):
        r.err("through_line", "missing 'name'")
    if not tl.get("prop_prompt"):
        r.err("through_line", "missing 'prop_prompt' — the guest food needs its own generated prop")
    for i, b in enumerate(ep.get("blocks", []), start=1):
        if not b.get("through_line_state"):
            r.err(f"block {i}", "missing 'through_line_state'")


def check_block_dialogue(ep, r):
    for b in ep.get("blocks", []):
        n = b.get("n")
        where = f"block {n}"
        turns = b.get("turns", [])

        if not TURNS_MIN <= len(turns) <= TURNS_MAX:
            r.err(where, f"{len(turns)} turns; needs {TURNS_MIN}–{TURNS_MAX}")

        speakers = [t.get("speaker") for t in turns]
        distinct = list(dict.fromkeys(speakers))
        if len(distinct) > MAX_SPEAKERS_PER_BLOCK:
            r.err(where, f"{len(distinct)} speakers ({', '.join(distinct)}); max is {MAX_SPEAKERS_PER_BLOCK}")
        for a, b2 in zip(speakers, speakers[1:]):
            if a == b2:
                r.err(where, f"'{a}' speaks twice in a row — turns must alternate")

        total = 0
        for t in turns:
            w = words(t.get("line", ""))
            total += len(w)
            if len(w) > MAX_TURN_WORDS:
                r.err(where, f"{t.get('speaker')} has a {len(w)}-word turn (max {MAX_TURN_WORDS}): \"{t.get('line')}\"")
        if not WORDS_MIN <= total <= WORDS_MAX:
            r.err(where, f"{total} words; needs {WORDS_MIN}–{WORDS_MAX}")

        if "gut" not in distinct:
            r.warn(where, "Gut is not in this block — Gut is the through-line character")

        for t in turns:
            line = t.get("line", "").lower()
            lw = words(line)
            for f in FILLER:
                if f in lw:
                    r.err(where, f"filler word '{f}' in: \"{t.get('line')}\"")
            for p in FILLER_PHRASES:
                if p in line:
                    r.err(where, f"filler phrase '{p}' in: \"{t.get('line')}\"")
            for pat in CLAIM_PATTERNS:
                if re.search(pat, line):
                    r.warn(where, f"reads as a health claim, not a joke: \"{t.get('line')}\"")
            content = [x for x in lw if x not in STOPWORDS]
            for i in range(len(content)):
                for j in range(i + 1, min(i + 4, len(content))):
                    if content[i] == content[j]:
                        r.warn(where, f"'{content[i]}' repeats inside one turn: \"{t.get('line')}\"")


def check_cold_open_and_kicker(ep, r):
    blocks = ep.get("blocks", [])
    if blocks:
        first = blocks[0].get("turns", [{}])[0].get("line", "")
        n = len(words(first))
        if n > MAX_COLD_OPEN_WORDS:
            r.err("block 1", f"cold open is {n} words (max {MAX_COLD_OPEN_WORDS}): \"{first}\"")

        b1_text = " ".join(t.get("line", "") for t in blocks[0].get("turns", [])).lower()
        keywords = [k.lower() for k in ep.get("food_keywords", [])]
        if keywords and not any(k in b1_text for k in keywords):
            r.err("block 1", f"the food is never named — expected one of {keywords}")

    kicker = ep.get("kicker", "")
    kw = len(words(kicker))
    if kw > MAX_KICKER_WORDS:
        r.err("kicker", f"{kw} words (max {MAX_KICKER_WORDS}): \"{kicker}\"")
    if "!" in kicker:
        r.err("kicker", "contains '!' — the kicker is flat, that's the whole joke")
    if blocks:
        last_lines = [t.get("line", "") for t in blocks[-1].get("turns", [])]
        if kicker and kicker not in last_lines:
            r.err("kicker", "is not the last spoken line of block 6")
        elif kicker and last_lines and kicker != last_lines[-1]:
            r.err("kicker", "appears in block 6 but is not the final turn")


def check_profanity(ep, r):
    mild_hits = []
    for b in ep.get("blocks", []):
        for t in b.get("turns", []):
            for w in words(t.get("line", "")):
                if w in HARD_PROFANITY:
                    r.err(f"block {b.get('n')}", f"hard profanity '{w}' — see the swap table in docs/02")
                if w in MILD_PROFANITY:
                    mild_hits.append((b.get("n"), w))
    if len(mild_hits) > 1:
        spots = ", ".join(f"block {n} '{w}'" for n, w in mild_hits)
        r.err("episode", f"{len(mild_hits)} mild-profanity hits, ceiling is 1 ({spots})")


def check_repeats(ep, r):
    seen = {}
    for b in ep.get("blocks", []):
        text = " ".join(t.get("line", "") for t in b.get("turns", []))
        w = words(text)
        for i in range(len(w) - 4):
            phrase = " ".join(w[i:i + 5])
            if phrase in seen and seen[phrase] != b.get("n"):
                r.err(f"block {b.get('n')}", f"repeats a 5-word phrase from block {seen[phrase]}: \"{phrase}\"")
            seen.setdefault(phrase, b.get("n"))


def check_staging(ep, r):
    locations = []
    for b in ep.get("blocks", []):
        n = b.get("n")
        where = f"block {n}"
        shots = b.get("shots", [])
        if len(shots) != SHOTS_PER_BLOCK:
            r.err(where, f"{len(shots)} shots; needs exactly {SHOTS_PER_BLOCK} (2.5s each)")
        if not b.get("sfx"):
            r.err(where, "missing 'sfx' — every block needs one physical event with a sound")
        loc = b.get("location")
        if not loc:
            r.err(where, "missing 'location'")
        locations.append(loc)

        refs = 1 + len(b.get("characters", [])) + len(b.get("props", []))
        if refs > MAX_REFS_PER_BLOCK:
            r.err(where, f"{refs} image references; the model rejects more than {MAX_REFS_PER_BLOCK}")

        speakers = {t.get("speaker") for t in b.get("turns", [])}
        cast = set(b.get("characters", []))
        missing = speakers - cast
        if missing:
            r.err(where, f"speaks {sorted(missing)} but does not attach them as characters")
        silent = cast - speakers
        if len(silent) > 1:
            r.warn(where, f"{sorted(silent)} are on screen but silent — trim to keep refs low")

    run = 1
    for a, b2 in zip(locations, locations[1:]):
        run = run + 1 if a == b2 else 1
        if run > MAX_CONSECUTIVE_SAME_LOCATION:
            r.err("staging", f"'{b2}' runs {run} consecutive blocks; max {MAX_CONSECUTIVE_SAME_LOCATION}")

    counts = Counter(x for x in locations if x)
    if len(counts) < 2:
        r.err("staging", "the whole episode is in one location — rotate at least two")


def validate(path):
    r = Report(path)
    try:
        ep = json.loads(Path(path).read_text())
    except json.JSONDecodeError as e:
        r.err("json", str(e))
        return r
    check_structure(ep, r)
    check_caption(ep, r)
    check_through_line(ep, r)
    check_block_dialogue(ep, r)
    check_cold_open_and_kicker(ep, r)
    check_profanity(ep, r)
    check_repeats(ep, r)
    check_staging(ep, r)
    return r


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    ok = True
    for path in argv[1:]:
        ok &= validate(path).print()
    print()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
