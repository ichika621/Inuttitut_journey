# -*- coding: utf-8 -*-
"""
CHANGE 1 — Build data/nouns.json: the NOUNS-ONLY subset of dictionary.json used
for everything taught, collected, and tested in the game.

Filter:
  INCLUDE  entries marked pos == "n.", OR pos-less entries whose English gloss is
           a plain concrete thing (short, no verb/action/adjective/sentence).
  EXCLUDE  every pos == "v."; every action/command gloss ("to …", "come here");
           full sentences (pronouns / long clauses); common adjectives/states.

Each kept record gets "noun": true plus a "simplicity" score (higher = simpler:
single common short concrete everyday word) and a re-derived "difficulty" 1-4 so
Act 1 can use the very simplest first. Fields id/english/inuttut/pos/image/theme
are carried through unchanged.
"""
import io, json, re

INP = "data/dictionary.json"
OUT = "data/nouns.json"

PRONOUNS = re.compile(r"\b(he|she|it|they|you|we|i|his|her|their|him|them|someone|"
                      r"something|oneself|itself|myself|yourself|themselves)\b", re.I)
# common non-noun heads (verbs / adjectives / states) — reject if the gloss IS one
# of these or STARTS with one of these as a standalone word.
NON_NOUN = set("""
eat look wait come go going give return listen hold run walk see hear sleep sing
dance bring take put get make do say tell ask leave stay sit stand fall throw catch
pull push carry cut open close wake feel think know want need find lose meet kill
hunt fish(v) fly swim jump kick hit break burn melt freeze boil cook drink smell
happy sad cold warm hot cool tired sleepy afraid scared angry mad glad good bad big
small large tiny short tall long wide narrow old new young dead alive sick well wet
dry clean dirty hungry thirsty full empty heavy light(adj) fast slow strong weak
soft hard sharp dull bright dark loud quiet ready done same different ill lazy busy
brave shy proud shameful able unable absent present agile alike alive alone
yes no maybe hello goodbye ouch please sorry thanks thank welcome here there
""".split())
# glosses that are clearly actions/commands even as short phrases
ACTION_PAT = re.compile(r"^(to |come |go |give |take |bring |put |let |do not|don't|"
                        r"say |tell |ask |wait|look|listen|hold|run|walk|see |eat|"
                        r"drink|sleep|sing|dance|make |get )", re.I)

def strip_paren(g):
    return re.sub(r"\([^)]*\)", "", g).strip()

def is_noun(rec):
    if rec.get("pos") == "v.":
        return False
    if rec.get("pos") == "n.":
        return True                       # trust the compiler's noun marker
    # pos-less: judge the gloss HEAD (the part before any descriptive comma),
    # so "Seal, animal that lifts it head out of the water" -> head "Seal".
    core = strip_paren(rec["english"]).strip().rstrip(".").strip()
    if not core:
        return False
    head = core.split(",")[0].strip()
    low = head.lower()
    if not low:
        return False
    if ACTION_PAT.match(low):
        return False
    if PRONOUNS.search(low):
        return False
    words = low.split()
    if len(words) > 3:
        return False
    if words[0] in NON_NOUN or low in NON_NOUN:
        return False
    return True

def simplicity(rec):
    core = strip_paren(rec["english"]).strip()
    words = core.split()
    s = 0.0
    s += (4 - min(len(words), 4)) * 4          # single-word gloss is best
    s += max(0, 14 - len(core)) * 0.4          # short gloss
    if "(" in rec["english"]:
        s -= 4                                  # scientific / parenthetical detail
    if rec["theme"] in ("body", "family", "animals", "food", "weather", "land_nature", "clothing", "greetings", "hunting_tools"):
        s += 3
    if rec["theme"] == "misc":
        s -= 2
    if rec["inuttut"] and len(rec["inuttut"][0]) <= 7:
        s += 2
    return round(s, 1)

def main():
    data = json.load(io.open(INP, encoding="utf-8"))
    nouns = []
    for e in data:
        if not is_noun(e):
            continue
        r = dict(e)
        r["noun"] = True
        r["simplicity"] = simplicity(e)
        nouns.append(r)
    # re-derive a noun difficulty 1-4 from simplicity quartiles (simpler = tier 1)
    ss = sorted(n["simplicity"] for n in nouns)
    def q(p):
        return ss[min(len(ss) - 1, int(p * len(ss)))]
    q1, q2, q3 = q(0.75), q(0.5), q(0.25)     # note: high simplicity = easy
    for n in nouns:
        s = n["simplicity"]
        n["difficulty"] = 1 if s >= q1 else 2 if s >= q2 else 3 if s >= q3 else 4
    nouns.sort(key=lambda n: (-n["simplicity"], n["english"]))
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(nouns, ensure_ascii=False, indent=1))
    from collections import Counter
    dc = Counter(n["difficulty"] for n in nouns)
    npos = sum(1 for n in nouns if n["pos"] == "n.")
    print("total dictionary entries:", len(data))
    print("nouns kept:", len(nouns), "(explicit n.:", npos, "| concrete pos-less:", len(nouns) - npos, ")")
    print("noun difficulty tiers:", dict(sorted(dc.items())))
    print("\nsimplest 24 nouns (Act-1 pool candidates):")
    for n in nouns[:24]:
        print("  %-26s %-14s  s=%.1f" % (n["english"][:24], n["inuttut"][0], n["simplicity"]))

if __name__ == "__main__":
    main()
