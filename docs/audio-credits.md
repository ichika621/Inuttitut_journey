# Audio — sources, licensing & cultural note

## What this is

**All music, ambience, and sound effects are synthesised at runtime** by
`js/audio.js` using the Web Audio API. There are **no audio files**, and nothing
is sampled, recorded, or streamed. Consequences:

- **Royalty-free / self-contained** — the whole soundtrack is generated from
  oscillators and filtered noise; nothing to license, works from `file://`.
- **No sacred or ceremonial recordings** — a cultural-care requirement. Because
  the audio is pure synthesis, it categorically contains no drum-dance, throat-
  singing, or any other recorded Inuit cultural sound. It is a neutral,
  placeholder score.

## Tracks (all procedural)

BGM (looping, a drone + a 4-bar arpeggio/pad motif per mood):

| Track | Mood | Where |
|---|---|---|
| `home` | warm, small | snow house / village |
| `land` | open, walking pace | tundra travel |
| `sea` | deep, slow swells | sea edge & underwater |
| `legend` | wide, wondrous | spirits, sky, big beats |
| `battle` | tense, driving | all battles |
| `reprise` | full, triumphant | the ending |
| `victory_jingle` | short sting | after a win (one-shot) |

Ambient beds (looping filtered noise, some with a slow LFO): `windlow`,
`tundra`, `sea`, `underwater`, `dogs`, `sky`.

SFX (one-shots): `text_blip`, `word_learned`, `correct`, `wrong`, `enemy_hit`,
`enemy_defeated`, `levelup`, `menu_click`, `page_turn`, `raven_caw`,
`heartbeat`, `sunrise_swell`, `victory_jingle`.

The scene data (`data/story.json`) carries the `bgm`/`amb` per scene and inline
`sfx` cues per beat; the engine plays them. A 🔊 toggle in the top bar mutes/
unmutes (the AudioContext is created on the first user gesture, per browser
autoplay policy).

## If you replace this with real music

Any real soundtrack must be **royalty-free or properly licensed, and documented
here**, and — like the art and tales — **must not use sacred or ceremonial
recordings**. Commission or license audio with the guidance of the Nunatsiavut
Government / Torngâsok Cultural Centre before publishing.
