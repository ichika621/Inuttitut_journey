# Inuttut Journey — a Labrador Inuit language-learning visual-novel RPG

A browser-based, character-driven **visual-novel RPG** for learning **Inuttut** —
the language of the **Labrador Inuit (Nunatsiavut)** — for English speakers. You
play the first-person protagonist of a Labrador folktale: illustrated story
beats, **visual-novel conversations** where characters' faces change line to line
and Inuttut words are taught inline, and turn-based **word battles** that test
them — all over a fully-synthesised soundtrack.

> **This is Inuttut (Labrador Inuit), _not_ Inuktitut.** Spelling follows the
> source dictionary's exact Roman orthography, including the mid-word capital `K`
> (a uvular consonant) and circumflex vowels (`â ê î ô û`). Every taught word was
> validated against the dictionary before use; nothing is invented, translated,
> or borrowed from another dialect.
>
> **Vocabulary is NOUNS ONLY.** Everything taught, collected, and tested is a
> concrete noun (people, animals, objects, places, natural features), filtered
> into `data/nouns.json`. Verbs, actions, adjectives, and phrases are never
> surfaced as learnable words — characters just speak them naturally in English.
> Act 1 uses the very simplest nouns.

## Quick start

Open `index.html` in any modern browser — no build step, no server required.
Data loads from `data/dictionary.js` / `data/story.js` (so it runs from
`file://`), art from `assets/`, and audio is generated in-browser. Sound starts
on your first click (browser autoplay policy); toggle it with 🔊 in the top bar.
Served over HTTP it loads the canonical `data/*.json` instead.

## The loop

```
MAP  →  ACT (a folktale, 4–5 scenes)  →  MAP …
          │
          ├─ Story beat     first-person inner-voice narration over a background
          ├─ Conversation   character portrait whose EXPRESSION changes each line;
          │  (LEARN)         Inuttut words glow inline — tap to learn (chime) →
          │                  filed to your illustrated Field Guide
          ├─ Battle          enemy sprite with damage-STAGES + HP bars vs your HP;
          │  (TEST)          picture-choice / word MC / matching / noun-ordering.
          │                  Right = attack; wrong = take damage; miss → it returns
          └─ Culture Card    collected at the end of each act
```

Whenever a character speaks, **that speaker's face is shown** in the pose named by
the line (`assets/chars/<speaker>/<expr>.svg`); when two characters share a scene
the **active speaker is foregrounded and the other dims and steps back**;
inner-voice narration shows no portrait. See `scripts/build_story.py`'s printout
for the exact `(character, expression)` list the script requires.

Progression: **XP and player levels**, a visual **act trail** on the map, **spaced
repetition** (missed words return in later battles), an illustrated **Field
Guide**, and collected **Culture Cards**.

## What's in here

```
index.html                     the single-page app
css/styles.css                 styles: map, visual-novel, battles, picture-dictionary
js/app.js                      engine: beat-player (VN), battles, SRS, XP, audio hooks
js/audio.js                    procedural Web-Audio soundtrack (BGM/SFX/ambient)
data/dictionary.json           parsed dictionary (4577 entries)   ← canonical data
data/nouns.json                NOUNS-ONLY subset (2983) + simplicity score
data/story.json                the 4-act / 17-scene beat graph + embedded noun vocab
data/*.js                      file://-friendly wrappers (window.DICTIONARY / .NOUNS / .STORY)
assets/words/*.svg             word icons (picture-based learning)
assets/chars/<name>/<expr>.svg character expression sheets + enemy damage-stages
assets/bg/*.svg                scene backgrounds
assets/CREDITS.md              art sources, CC0 licence, cultural-review note
docs/audio-credits.md          audio: procedural, royalty-free, no sacred recordings
docs/folktale-research.md      Labrador folktale research + sources + caveats
scripts/extract_pdf.py         PDF → text (PyMuPDF)
scripts/parse_dictionary.py    text → dictionary.json
scripts/tag_dictionary.py      adds theme + difficulty + image path to every record
scripts/build_nouns.py         filters to NOUNS ONLY + simplicity score → nouns.json
scripts/make_assets.py         word icons + base sprites/backgrounds
scripts/make_story_assets.py   expression sheets + story backgrounds + enemy stages
scripts/build_story.py         builds story.json (validates every word is a noun in the PDF)
scripts/make_wrappers.py       regenerates the data/*.js wrappers
English-Inuttut Dictionary.pdf the one and only vocabulary source
```

## Step 1 — Parsing the dictionary

The PDF (`www.labradorvirtualmuseum.ca/english-inuttut.htm`, 191 print-pages) is
extracted with PyMuPDF and parsed by `scripts/parse_dictionary.py`.

**Entry grammar:** `English gloss [separator] [pos] InuttutForm[; | .]`, where the
separator is an em dash `—`, or the pos marker itself (`Airplane  v. Tingijok.`),
or nothing when a long gloss wraps and the form lands alone on the next line.
Additional forms on following lines (starting with a dash or pos marker) become
the `inuttut` array; inline `v.`/`n.` → `pos`; a trailing `?` → `uncertain:true`.
Orthography is preserved exactly (capital `K`, circumflex vowels); page
headers/footers, date stamps, `N/191` numbers, and `A ‑ a`…`Z ‑ z` dividers are
stripped.

**Result: 4577 entries — exactly the total the PDF itself declares.**

### Data schema (`data/dictionary.json`)

```json
{ "id": 2446, "english": "Moon", "inuttut": ["TakKik"], "pos": null,
  "uncertain": false, "theme": "land_nature", "difficulty": 1,
  "image": "assets/words/moon.svg" }
```

### Spot-check (15 entries verified against the PDF)

| English | Inuttut | pos | note |
|---|---|---|---|
| Abdomen | AKiak | | capital-K preserved |
| Accordion | Nilliajok, Tasijuajok | | multi-form |
| Airplane | Tingijok | v. | pos before form, no dash |
| Amphibians | Nunatsuillo imak suillo | | multi-word form |
| Angry | Kongak, Ninngaumak, Ningak | v. | 3 forms |
| Apple, a loan word… | Âppale | | circumflex preserved |
| Arctic hare (Lepus…) | Ukalik | | scientific name kept |
| Answer | kiuk, Akik | n. | lowercase form preserved |
| Alpine bistort (…) | Sapangalalannguak | | `uncertain:true` (trailing `?`) |
| Moon | TakKik | | mid-word capital K |
| Sun | SiKinik | | |
| Loon (Gavia immer) | Tollik | | |
| Polar bear (Ursus…) | Nanuk | | |
| Zipper | Sejok | v. | last entry (id 4577) |
| Zero, has nothing | SunaKangituk | | |

## Step 2 — Themes, difficulty & image slugs (`scripts/tag_dictionary.py`)

Every record is auto-tagged by keyword-matching the English gloss: a **theme**
(`greetings, family, body, animals, food, clothing, weather, land_nature,
hunting_tools, actions, misc`), a **difficulty 1–4** (1 short high-frequency; 2
concrete nouns; 3 nature/tools/actions; 4 phrases/multi-word), and an **image
path** (a curated map assigns ~75 core words a hand-drawn icon; the rest use a
placeholder). Distribution: themes — misc 3038, animals 321, actions 319, body
215, land_nature 160, hunting_tools 133, weather 131, family 82, food 80,
clothing 71, greetings 27; difficulty — 267 / 2471 / 998 / 841.

## Step 3 — Nouns-only filter (`scripts/build_nouns.py`)

The hard constraint: everything taught, collected, and tested must be a **noun**.
`build_nouns.py` filters `dictionary.json` into `data/nouns.json`:

- **Include** entries marked `n.`, plus pos-less entries whose gloss _head_ (the
  part before any descriptive comma) is a short concrete thing.
- **Exclude** every `v.` entry, every action/command gloss (`to …`, "come here",
  "wait"), full sentences (pronouns / long clauses), and adjectives/states.
- This matters: several plausible seed words are **verb-marked in the dictionary**
  and were rejected — `Sky (Kilak)`, `Rain (Silaluk)`, `Knife (Savik)`, and
  `Net (Nuluak)` are all `v.`, so the noun `Kalugiak` (spear) / `IKiak` (hook) are
  used instead. `Raven` is taught as `Tulugak` (dict gloss "Crow (Common raven)").

**2983 nouns pass the filter** (453 explicit `n.`, 2530 concrete pos-less; 0 verbs
leak through). Each gets `"noun": true`, a **simplicity** score (single, short,
concrete, everyday = simpler), and a noun difficulty 1–4 so Act 1 draws the
simplest. `build_story.py` re-checks every taught word against `nouns.json` and
**aborts if any non-noun sneaks in**. Battle distractors are drawn only from
`nouns.json`, so every wrong option is also a real noun.

**The 27 nouns taught, by act** (all verified nouns, each shown with its entry #
in-game):

- **Act 1 (simplest):** `Illuvigak` snow house · `Unnuak` night · `Kannik` snow ·
  `SiKinik` sun · `Ullugiak` star · `Inngutak` grandchild · `TakKik` moon ·
  `Nuvujak` cloud · `Ujagak` rock · `Kamutik` sled
- **Act 2 (animals/body):** `Tulugak` raven · `Tuttuk` caribou · `Minnigiak` fish ·
  `Ijik` eye · `NiaKuk` head · `Siutik` ear · `Nanuk` polar bear · `kamik` boot ·
  `Kingak` nose
- **Act 3 (sea/tools):** `Tagiuk` sea · `Imak` water · `Umiak` boat · `Puijik` seal ·
  `Kalugiak` spear · `IKiak` hook
- **Act 4 (sky/spring):** `Upinngak` spring · `Atitsiak` a good name (+ sky-noun
  review)

The Act 4 "phrase" battle is a **noun-ordering** round (tap the noun labels in the
order the English names them) — a recall exercise on independent nouns, not verb
conjugation and not a constructed sentence.

## Step 3b — The story (4 acts, 17 scenes, `data/story.json`)

Each scene is an ordered list of **beats**: `narr` (inner-voice narration),
`line` (a character line — swaps that character to a named **expression** and
teaches any backticked Inuttut words), `choice` (reply buttons), and `battle`.
Each scene carries a background, a BGM track, and an ambient bed; beats carry
inline SFX cues.

| Act | Tale | Scenes | Battle (enemy · damage-stages) | Source · community |
|---|---|---|---|---|
| 1 Home & Family | The Sun & the Moon (opening) | 4 | The Sleeping Team · dog wakes | Hawkes 1916 · Nunatsiavut |
| 2 The Land & the Animals | The Blind Boy and the Loon | 4 | Nanuk · bear calms & leaves | pan-Inuit *(weak Labrador — flagged)* |
| 3 The Sea & the Spirits | The Woman Beneath the Sea | 4 | The Sea Mother's Grief · anger→release | Hawkes 1916 · **not** "Sedna" |
| 4 The Sky & the Legends | The Sun & the Moon / aurora | 5 | The Long Night · Sun turns (build-phrase) | Hawkes 1916 p.156 |

Full research, source URLs, and attribution-strength notes are in
`docs/folktale-research.md`. **Enemies are game devices, not figures from the
tales.**

## Step 4 — Conversations, expressions & battles

**Conversations** render as a visual novel. **The active speaker's face is always
shown**, in the expression the line names, and swaps when the speaker changes;
when two characters are in a scene the **speaker is foregrounded while the other
dims and steps back**; inner-voice narration shows no portrait. The English line
is spoken naturally; the **noun** in it glows inline — tap to open its illustrated
card (Inuttut, English, pos, dictionary #) and file it to the Field Guide with a
chime. Every character's expression set covers each pose the script asks of it
(verified: 0 missing `(speaker, expression)` assets).

**Battles** are turn-based with an enemy sprite that changes through **damage-
stages** as HP drops (the sleeping dogs rise; Nanuk calms and turns away; the Sea
Mother's face softens anger → sorrow → calm → release; the Sun turns from grief →
longing → warmth). Question types: **pick-the-picture**, noun MC, matching, and a
**noun-ordering** round. Correct answers attack (shake/flash + floating damage +
"You wield _word_!"); wrong answers cost HP and re-queue the noun (spaced
repetition). All options and answers are nouns.

**Noun-ordering caveat:** the Act 4 "order" round places noun labels in a named
sequence ("night · moon · star"). These are independent noun labels for recall —
**not a constructed sentence**, so no grammar is asserted; the round is annotated
accordingly in `story.json`.

## Step 4d — Art & audio

- **Art** — 8 characters with **expression sheets**, enemy **damage-stage**
  sprites, ~22 backgrounds, and ~75 word icons. All original flat-illustration
  SVG, **CC0**; no photos of real people, no sacred/ceremonial imagery; a
  swappable asset layer (image paths in the data) for real, ideally Inuit-made,
  artwork. See `assets/CREDITS.md`.
- **Audio** — every track and effect is **synthesised at runtime** (`js/audio.js`,
  Web Audio) — no files, nothing sampled. This makes the soundtrack royalty-free
  and, by construction, free of any sacred/ceremonial recordings. Tracks: `home,
  land, sea, legend, battle, reprise, victory` + ambient beds + a full SFX
  library, driven by the per-scene/per-beat cues in `story.json`. See
  `docs/audio-credits.md`.

## Step 5 — Tech

Single-page app, mobile-first, no backend, no dependencies — plain HTML/CSS/JS.
Data is loaded client-side (`data/*.json`, with a `file://` wrapper fallback);
art is SVG via `<img>`; audio is procedural. **No pronunciation audio is faked** —
the game shows exact spelling only and notes recordings exist at the source site.

## Attribution & cultural care

Vocabulary © the **Labrador Virtual Museum — English-Inuttut Dictionary**
(<https://www.labradorvirtualmuseum.ca/english-inuttut.htm>) — credit it in any
use. The folktales are the **living cultural heritage of the Labrador Inuit**;
attribution and each tale's Labrador-attribution strength are shown in-game.
**Before publishing, the tales, retellings, framing, _art, and audio_ should be
reviewed — and ideally co-developed — with the Nunatsiavut Government and the
Torngâsok Cultural Centre / Illusuak Cultural Centre**, following "nothing about
us without us." Flag especially the shamanic material (Act 3) and the softened
mistreatment themes.

## Reproducing the pipeline

```bash
python scripts/extract_pdf.py "English-Inuttut Dictionary.pdf" scratch/raw_full.txt
python scripts/parse_dictionary.py scratch/raw_full.txt data/dictionary.json   # 4577
python scripts/tag_dictionary.py            # theme + difficulty + image (in place)
python scripts/build_nouns.py               # nouns-only filter → data/nouns.json (2983)
python scripts/make_assets.py               # word icons + base sprites/backgrounds
python scripts/make_story_assets.py         # expression sheets + story backgrounds
python scripts/build_story.py               # validates every taught word is a noun → data/story.json
python scripts/make_wrappers.py             # regenerate data/*.js wrappers
# then bump the ?v= cache tokens in index.html if you re-served an old build
```
Requires `pip install pymupdf` for the extraction step only.
