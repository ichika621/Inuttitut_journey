# Art assets — sources, licensing & cultural note

## What this is

All images in `assets/` are **original flat-illustration placeholder art**,
generated programmatically by `scripts/make_assets.py` (plain geometric SVG
shapes). They are:

- **Original / self-authored** — no third-party art, no clip-art, no traced or
  copied imagery.
- **CC0 / public domain** — you may use, modify, or replace them freely.
- **Not photographs** — there are **no photographs of real people**, and in
  particular no images of identifiable Inuit individuals.
- **Not sacred or ceremonial** — the characters are simple, generic stylised
  figures (hooded parkas, neutral faces). No tattoos, ceremonial regalia,
  drums-as-ritual-objects, or spirit iconography drawn from real practice.
  Enemy figures ("The Long Dark", "The Ice-Storm", "The Cold Hunger", "The
  Hoarding Shaman") are **abstract game devices**, not depictions of beings from
  the folktales.

## This is a swappable asset layer

Every word, character, and background is referenced by an **image path** in the
data (`image` on each dictionary record; `characters`/`backgrounds` in
`data/chapters.json`). Real artwork can be dropped in at the same paths without
touching code:

```
assets/
  words/<slug>.svg     100×100 word icons  (e.g. seal.svg, moon.svg)
  words/_placeholder.svg   shared fallback icon for un-illustrated words
  chars/<slug>.svg     240×300 character portraits & enemy sprites
  bg/<slug>.svg        1200×675 scene backgrounds
```

## Cultural review — required before publishing

This placeholder art is deliberately minimal so it can be **replaced by real
artwork — ideally commissioned from Inuit / Nunatsiavut artists** — before any
public release. Before publishing, the visuals (like the tales) should be
reviewed with the **Nunatsiavut Government** and the **Torngâsok Cultural
Centre / Illusuak Cultural Centre**. Do not ship these placeholders as if they
were authentic Labrador Inuit artwork.

## Regenerating

```
python scripts/make_assets.py
```
Writes every SVG under `assets/`. Palette and shapes live in that one script.
