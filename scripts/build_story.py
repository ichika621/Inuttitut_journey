# -*- coding: utf-8 -*-
"""
Build data/story.json — the full visual-novel production (4 acts, 17 scenes).

REVISION (nouns-only): every TAUGHT / TESTED Inuttut word is now a NOUN, drawn
from data/nouns.json, and Act 1 uses the very simplest ones. Characters still
speak natural English (verbs are fine in spoken lines); only the highlighted
learnable Inuttut items are nouns. See scripts/build_nouns.py for the filter.

Each scene is an ordered list of BEATS:
  narr(text)                    inner-voice narration (English; teaches nothing)
  line(who, expr, text)         a character line; swaps `who` to expression `expr`
                                and teaches any `backticked` Inuttut NOUN in the text
  choice(options)               reply buttons
  battle(...)                   a turn-based noun battle (picture / MC / match / order)

Audio cues (bgm/amb per scene, sfx per beat) are carried in the data. Every
taught word is validated against nouns.json at build time (fails loudly if a
non-noun or missing form sneaks in).
"""
import io, json, re, sys

DICT = "data/dictionary.json"; NOUNS = "data/nouns.json"; OUT = "data/story.json"
data = json.load(io.open(DICT, encoding="utf-8"))
by_id = {e["id"]: e for e in data}
noun_ids = set(n["id"] for n in json.load(io.open(NOUNS, encoding="utf-8")))

# form -> dictionary id, bound to the intended NOUN sense
WORDMAP = {
    # Act 1 — simplest nouns
    "Illuvigak": 3544, "Unnuak": 2559, "Kannik": 3538, "SiKinik": 3836,
    "Inngutak": 1624, "Ullugiak": 3714, "TakKik": 2446, "Nuvujak": 717,
    "Ujagak": 3156, "Kamutik": 3471,
    # Act 2 — animals, body, clothing
    "Tulugak": 861, "Tuttuk": 575, "Minnigiak": 1373, "Ijik": 1267,
    "NiaKuk": 1766, "Siutik": 1154, "Nanuk": 2909, "kamik": 426, "Kingak": 2582,
    # Act 3 — sea & tools
    "Tagiuk": 3268, "Imak": 4338, "Umiak": 403, "Puijik": 3277,
    "Kalugiak": 3641, "IKiak": 1861,
    # Act 4 — spring / a good name
    "Upinngak": 3682, "Atitsiak": 1615,
}
WORDS, BAD, NONNOUN = {}, [], []
def wid(form):
    i = WORDMAP.get(form)
    if not i or i not in by_id:
        BAD.append(form); return None
    if i not in noun_ids:
        NONNOUN.append(form)                    # guardrail: taught word must be a noun
    r = by_id[i]
    WORDS[i] = {"id": r["id"], "english": r["english"], "inuttut": r["inuttut"],
                "pos": r["pos"], "theme": r["theme"], "difficulty": r["difficulty"],
                "uncertain": r["uncertain"], "image": r.get("image"), "noun": True}
    return i

def narr(text, sfx=None):
    b = {"t": "narr", "text": text}
    if sfx: b["sfx"] = sfx
    return b
def line(who, expr, text, sfx="text_blip"):
    ids = []
    for form in re.findall(r"`([^`]+)`", text):
        i = wid(form)
        if i and i not in ids: ids.append(i)
    b = {"t": "line", "who": who, "expr": expr, "text": text}
    if ids: b["words"] = ids
    if sfx: b["sfx"] = sfx
    return b
def choice(*opts): return {"t": "choice", "options": list(opts)}
def battle(name, stages, hp, php, pool, rounds, types, intro, victory, sequences=None):
    b = {"t": "battle", "enemy": name, "stages": stages, "enemyHp": hp, "playerHp": php,
         "pool": [wid(f) for f in pool], "rounds": rounds, "types": types,
         "intro": intro, "victory": victory}
    if sequences:
        for s in sequences:
            s["tokenIds"] = [wid(f) for f in s["tokens"]]
        b["sequences"] = sequences
    return b
def scene(id, title, bg, bgm, amb, beats):
    return {"id": id, "title": title, "bg": bg, "bgm": bgm, "amb": amb, "beats": beats}

# ===========================================================================
# ACT 1 — HOME & FAMILY (simplest nouns)
# ===========================================================================
act1 = {"id": "act1", "title": "Home & Family", "tale": "The long night begins",
    "culture": {"title": "Snow houses, sled dogs & the long polar night",
        "body": ("Through the deep-winter dark, the seal-oil lamp and the snow house held a "
                 "family's whole world; sled-dog teams carried people across the frozen land. A "
                 "child learned the names of these everyday things by lamplight before ever setting out."),
        "source": "Framing after E.W. Hawkes, The Labrador Eskimo (1916).", "community": "Nunatsiavut broadly",
        "reviewNote": "Enemies are game devices, not figures from the tales. Flag for elder review."},
    "scenes": [
    scene("1.1", "Inside the snow house", "snowhouse_interior_lamplight", "home", "windlow", [
        narr("The lamp is the only warm thing left in the world."),
        line("miki", "scared", "The night won't stop. Is the morning gone forever?"),
        narr("My little one presses close. I hold the small hand."),
        line("grandmother", "warm", "Come here, little ones. This is our home — our `Illuvigak`, our snow house.", "word_learned"),
        narr("Grandmother's smile does what the lamp cannot."),
        line("grandmother", "teaching", "This long dark is the `Unnuak`, the night. Name it, and you own it; it does not own you.", "word_learned"),
        line("miki", "scared", "`Unnuak`…"),
        line("grandmother", "tender", "And the `Kannik`, the snow, sits soft over our door.", "word_learned"),
        line("raven", "sly", "Kwaa. A child who learns a word tonight could learn a road tomorrow.", "raven_caw"),
        narr("The raven again. Grandmother does not chase it away.", "page_turn"),
    ]),
    scene("1.2", "Grandmother's charge", "snowhouse_closeup_grandmother", "home", "windlow", [
        line("grandmother", "worried", "The `SiKinik`, the sun, has hidden her face. That is why the dark will not lift.", "word_learned"),
        narr("I have never heard her afraid before."),
        line("grandmother", "tender", "These old bones cannot bring her back. But a child who knows the words can. Will you go, my `Inngutak` — my grandchild?", "word_learned"),
        narr("Fear, and something bigger than fear.", "heartbeat"),
        line("me", "determination", "…Yes. I will go.", "correct"),
        line("grandmother", "proud", "Then follow the `Ullugiak`, the stars, and they will light your road.", "levelup"),
    ]),
    scene("1.3", "The raven's road", "snowhouse_entrance_dark", "home", "windlow", [
        line("raven", "curious", "Kwaa. The `TakKik`, the moon, is out. Its light shows the road.", "raven_caw"),
        narr("A raven for a guide. Grandmother said not to fear the dark, only to speak to it."),
        line("raven", "encouraging", "Past the `Nuvujak`, the clouds, and over each `Ujagak`, each rock, we go.", "word_learned"),
        narr("I take Miki's mitten in my fist and step into the night.", "page_turn"),
    ]),
    scene("1.4", "The sled dogs", "dogline_snow_night", "battle", "dogs", [
        line("raven", "sly", "These `Kamutik` dogs won't run for a stranger. Name each thing true, and a dog rises.", "word_learned"),
        narr("Six pairs of eyes in the dark. I have to get the names right."),
        battle("The Sleeping Team", ["dogteam/asleep", "dogteam/rising", "dogteam/standing"],
               8, 10, ["Illuvigak", "Unnuak", "Kannik", "SiKinik", "Inngutak", "Ullugiak", "TakKik", "Nuvujak", "Ujagak", "Kamutik"],
               7, ["picmc", "mc", "match"],
               "Name each thing of home and sky, and a dog wakes and stands to harness.",
               "Kwaa! The team is yours. The Kamutik lurches forward, and home shrinks behind me."),
    ]),
]}

# ===========================================================================
# ACT 2 — THE LAND & THE ANIMALS
# ===========================================================================
act2 = {"id": "act2", "title": "The Land & the Animals", "tale": "The Blind Boy and the Loon",
    "culture": {"title": "The blind boy and the loon; respect on the land",
        "body": ("Caribou and the animals of the land fed and clothed the people, and stories like "
                 "the blind boy and the loon taught that cruelty returns and that the land must be met "
                 "with respect — you name and know an animal rather than simply take it."),
        "source": "Blind-boy/loon tale is pan-Inuit; land-respect framing after Hawkes 1916.",
        "community": "Pan-Inuit (weak specific-Labrador attribution — flag).",
        "reviewNote": "This tale is NOT strongly documented in Labrador; presented as pan-Inuit. Flag for review."},
    "scenes": [
    scene("2.1", "Onto the tundra", "tundra_stars_wide", "land", "tundra", [
        narr("The sky is all stars, and still no morning."),
        line("raven", "curious", "A `Tulugak` like me — a raven — knows this land well.", "word_learned"),
        line("hunter", "calm", "So. A child in the dark with a raven. The `Tuttuk`, the caribou, cross here.", "word_learned"),
        line("hunter", "focused", "Under the lake ice sleep the `Minnigiak`, the fish. Keep moving.", "word_learned"),
    ]),
    scene("2.2", "The blind boy's story", "frozen_lake_vision", "legend", "tundra", [
        line("hunter", "teaching", "Watch. A boy was left blind — his `Ijik`, his eyes, gave no light.", "word_learned"),
        narr("The ice shows it like a window: the boy, alone, mistreated."),
        line("hunter", "calm", "A loon dived with him; when his `NiaKuk`, his head, broke the water, he could see.", "word_learned"),
        narr("Now his hands shake with the power to take everything back."),
        line("hunter", "stern", "Listen with your `Siutik`, your ears, to the whole lesson: how he answers cruelty.", "word_learned"),
    ]),
    scene("2.3", "The great bear", "ice_ridge_bear", "battle", "tundra", [
        line("raven", "alarmed", "Kwaa! `Nanuk`. The white bear.", "raven_caw"),
        narr("Every part of me wants to run.", "heartbeat"),
        line("hunter", "stern", "You do not fight Nanuk. You know it. Name what it is, true — and it lets you pass."),
        battle("Nanuk", ["bear/aggro", "bear/wary", "bear/calm"],
               12, 12, ["Nanuk", "Tuttuk", "Minnigiak", "Tulugak", "Ijik", "NiaKuk", "Siutik"],
               8, ["picmc", "mc", "match"],
               "Name each animal and thing true — you do not strike the bear, you calm it.",
               "Good. You spoke instead of struck. Nanuk lowers its head and walks away over the ice."),
    ]),
    scene("2.4", "After", "tundra_dawnless_calm", "land", "tundra", [
        line("hunter", "approving", "The land spared you. Pull your `kamik`, your boots, tight now.", "word_learned"),
        line("hunter", "approving", "Cover your `Kingak`, your nose, from the cold, and rest one breath.", "word_learned"),
        narr("I am tired — but taller than when I left.", "levelup"),
    ]),
]}

# ===========================================================================
# ACT 3 — THE SEA & THE SPIRITS
# ===========================================================================
act3 = {"id": "act3", "title": "The Sea & the Spirits", "tale": "The Woman Beneath the Sea",
    "culture": {"title": "The woman beneath the sea; why the sea must be honoured",
        "body": ("The Labrador Inuit knew the sea as the country of a powerful spirit who holds the "
                 "seals and whales. When people take without respect she grieves and the animals "
                 "vanish; care and thanks bring them back. This is the Labrador sea-spirit tradition — "
                 "not the Central-Arctic 'Sedna' tale."),
        "source": "After Hawkes 1916 (Torngâsoak/sea-spirit complex); NOT the 'Sedna' narrative.",
        "community": "Killiniq / northern Labrador; Nunatsiavut broadly.",
        "reviewNote": "Highest sensitivity — spiritual/shamanic material. Strongly review with Nunatsiavut / Torngâsok."},
    "scenes": [
    scene("3.1", "The edge of the world", "ice_edge_black_water", "sea", "sea", [
        narr("The land ends. Before me is only the grey water."),
        line("raven", "still", "This is the `Tagiuk`, the sea. The `Imak`, the water, is her whole country.", "word_learned"),
        line("raven", "still", "No `Umiak`, no boat, can follow where you must go. This road you walk alone.", "word_learned"),
        narr("For the first time the raven cannot come.", "raven_caw"),
    ]),
    scene("3.2", "Down into the water", "descending_green_dark", "sea", "underwater", [
        narr("I hold my breath and let the cold pull me down."),
        line("me", "determination", "I remember the `Puijik`, the seal, and the hunter's `Kalugiak`, his spear.", "word_learned"),
        narr("Grandmother's voice reaches even here: speak to it, do not fear it."),
        narr("The deep opens below me, green then black."),
    ]),
    scene("3.3", "The Sea Mother", "undersea_seamother_hall", "legend", "underwater", [
        line("seamother", "sorrow", "You came down into my grief, little breath. Everyone else only takes."),
        narr("Her hair floats like black weather. The animals are tangled in it, waiting."),
        line("seamother", "anger", "Why should I open my hands to the world above?", "heartbeat"),
        narr("I could beg. I could shout. Instead I offer what I carry."),
        line("me", "determination", "I bring you the `IKiak`, the hook — a gift, not a taking. Thank you.", "word_learned"),
        line("seamother", "sorrow", "…You gave, and asked nothing."),
    ]),
    scene("3.4", "Untangling", "undersea_seamother_close", "battle", "underwater", [
        line("seamother", "sorrow", "Then free me, if you can. My own hands cannot."),
        battle("The Sea Mother's Grief", ["seamother/anger", "seamother/sorrow", "seamother/calm", "seamother/release"],
               14, 12, ["Tagiuk", "Imak", "Umiak", "Puijik", "Kalugiak", "IKiak", "Minnigiak"],
               8, ["picmc", "mc", "match"],
               "Each thing you name true, gently, loosens one strand of her hair.",
               "Go — take the animals back to the world. The seals stream past you toward the light."),
    ]),
]}

# ===========================================================================
# ACT 4 — THE SKY & THE LEGENDS
# ===========================================================================
act4 = {"id": "act4", "title": "The Sky & the Legends", "tale": "The Sun & the Moon",
    "culture": {"title": "The sun & moon; the northern lights as the ancestors",
        "body": ("The sun and moon are told of as kin who cross the sky, and the northern lights were "
                 "often understood as spirits or ancestors at play. To turn the grieving Sun back, only "
                 "kind words will do — the whole journey has been about speaking, and naming, not taking."),
        "source": "Sun/Moon after Hawkes 1916 p.156; aurora framing per Labrador tradition. Verify with community.",
        "community": "Nunatsiavut broadly.",
        "reviewNote": "Softened retelling. Battle 'order' rounds are noun-label sequences, not sentences. Flag for review."},
    "scenes": [
    scene("4.1", "The road of light", "sky_road_stars", "legend", "sky", [
        line("raven", "encouraging", "Kwaa. You came back from the sea. Now — up, into the night.", "raven_caw"),
        narr("The stars become a road under my feet."),
        line("raven", "still", "The Sun and Moon are here. Use every name you carry.", "page_turn"),
    ]),
    scene("4.2", "The Moon-brother", "sky_moon_pale", "legend", "sky", [
        line("moon", "yearning", "I chase my sister across the sky and never reach her. `TakKik` — I am the Moon.", "word_learned"),
        narr("Pale, endless longing. He does not stop me."),
        line("moon", "resignation", "She hid her face from grief. That is your long night. Only kind words will turn her."),
    ]),
    scene("4.3", "The Sun-sister", "sky_sun_hidden", "legend", "sky", [
        line("sun", "grief", "Why should I show my face to a world that let me flee? `SiKinik` stays hidden.", "word_learned"),
        narr("Her light is behind her hands. Below, everything I love waits in the cold."),
        line("raven", "encouraging", "Every name you learned, little one. Now."),
    ]),
    scene("4.4", "Calling the light", "sky_dawn_edge", "battle", "sky", [
        narr("This is the whole journey, gathered into a handful of names."),
        battle("The Long Night", ["sun/grief", "sun/longing", "sun/warm"],
               16, 12, ["SiKinik", "TakKik", "Ullugiak", "Unnuak", "Nuvujak"],
               9, ["picmc", "mc", "match", "order"],
               "Name the lights of the sky, then call them in order — each true name is a rung of light climbed.",
               "…A child climbed all this way, naming what I gave the world? The Sun turns her face, and the dark, for the first time in a hundred sleeps, breaks.",
               sequences=[
                   {"gloss": "the lights of the sky, in order:  night · moon · star", "tokens": ["Unnuak", "TakKik", "Ullugiak"],
                    "note": "A sequence of separate noun labels for recall — not a sentence. Tap them in the order named."},
                   {"gloss": "then:  sun · cloud", "tokens": ["SiKinik", "Nuvujak"],
                    "note": "Two separate noun labels in order — not a grammatical phrase."},
               ]),
    ]),
    scene("4.5", "Home, and a name", "snowhouse_sunrise_spring", "reprise", "windlow", [
        narr("I ride the light home."),
        line("miki", "delighted", "You brought the morning back!", "text_blip"),
        line("grandmother", "proud", "You went into the night and brought back the day.", "text_blip"),
        line("grandmother", "tender", "The ice melts to `Upinngak`, the spring. And your name is now `Atitsiak` — a good name, earned with words.", "levelup"),
        line("raven", "still", "Kwaa. Until the next long night.", "raven_caw"),
        narr("The lamp is no longer the only warm thing in the world.", "sunrise_swell"),
    ]),
]}

acts = [act1, act2, act3, act4]
# resolve sequence tokens
for a in acts:
    for sc in a["scenes"]:
        for b in sc["beats"]:
            if b["t"] == "battle" and b.get("sequences"):
                pass  # tokenIds already resolved in battle()
if BAD: print("UNRESOLVED WORDS:", BAD, file=sys.stderr); sys.exit(1)
if NONNOUN: print("NON-NOUN TAUGHT WORDS (must be nouns):", NONNOUN, file=sys.stderr); sys.exit(1)

characters = {
    "me": {"name": "Me", "dir": "assets/chars/me"},
    "grandmother": {"name": "Anânsiak", "dir": "assets/chars/grandmother"},
    "miki": {"name": "Miki", "dir": "assets/chars/miki"},
    "raven": {"name": "Tulugak", "dir": "assets/chars/raven"},
    "hunter": {"name": "The Hunter", "dir": "assets/chars/hunter"},
    "seamother": {"name": "The Sea Mother", "dir": "assets/chars/seamother"},
    "moon": {"name": "Moon-brother", "dir": "assets/chars/moon"},
    "sun": {"name": "Sun-sister", "dir": "assets/chars/sun"},
}
meta = {
    "source": "Labrador Virtual Museum — English-Inuttut Dictionary",
    "sourceUrl": "https://www.labradorvirtualmuseum.ca/english-inuttut.htm",
    "totalDictionaryEntries": len(data), "acts": len(acts),
    "vocabPolicy": "Taught/tested vocabulary is NOUNS ONLY (see data/nouns.json). Verbs, actions, adjectives, and phrases are never surfaced as learnable words.",
    "culturalCaveat": ("Vocabulary is from the Labrador Virtual Museum English-Inuttut Dictionary. The "
        "folktales are living Labrador Inuit cultural heritage; tales, retellings, framing, art, and audio "
        "should be reviewed with the Nunatsiavut Government and the Torngâsok Cultural Centre / Illusuak "
        "Cultural Centre before publishing. Enemies are game devices, not figures from the tales."),
    "audioNote": ("All music and sound are synthesised at runtime (no recordings) — royalty-free and free "
        "of any sacred/ceremonial audio. Word pronunciation is NOT provided; recordings exist at the source site."),
    "artNote": ("All art is original flat-illustration placeholder (CC0); no photos of real people, no sacred "
        "imagery. Swappable asset layer for real, ideally Inuit-made, artwork."),
}
out = {"meta": meta, "characters": characters, "words": WORDS, "acts": acts}
io.open(OUT, "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))

nsc = sum(len(a["scenes"]) for a in acts)
nba = sum(1 for a in acts for s in a["scenes"] for b in s["beats"] if b["t"] == "battle")
print("acts:", len(acts), "| scenes:", nsc, "| battles:", nba, "| NOUNS taught:", len(WORDS))
# (character, expression) asset list required by the script
pairs = {}
for a in acts:
    for sc in a["scenes"]:
        for b in sc["beats"]:
            if b["t"] == "line":
                pairs.setdefault(b["who"], set()).add(b["expr"])
print("\n(character, expression) pairs the script requires:")
for who in sorted(pairs):
    print("  %-12s %s" % (characters[who]["name"], sorted(pairs[who])))
