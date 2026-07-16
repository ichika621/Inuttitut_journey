# -*- coding: utf-8 -*-
"""Generate the game's visual asset layer as original flat-illustration SVGs.

All art here is authored from scratch (simple geometric flat shapes) and is
released CC0 / public domain (see assets/CREDITS.md). It contains NO photographs
of real people and NO sacred or ceremonial imagery. These are placeholders in a
swappable asset layer: real artwork — ideally commissioned from Inuit /
Nunatsiavut artists — can drop in at the same paths later.

Writes:
  assets/words/<slug>.svg   word icons (100x100)
  assets/chars/<slug>.svg   character portraits (240x300)
  assets/bg/<slug>.svg      scene backgrounds (1200x675)
"""
import io, os

ROOT = "assets"
def write(path, svg):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    io.open(full, "w", encoding="utf-8").write(svg)

# ---- palette --------------------------------------------------------------
C = dict(
    night="#0b1020", deep="#152142", panel="#1d2a52",
    snow="#eef4ff", ice="#8fe3d6", blue="#6fb7ff", steel="#4b6aa5",
    amber="#ffcf7a", ember="#ff9f5a", gold="#ffd479",
    green="#7ef1c9", violet="#b79bff", rose="#ff8ba7",
    parkaR="#c96f4a", parkaB="#3f6fa8", parkaG="#5a8f6b", parkaP="#8f6fb0",
    fur="#f3ece0", skin="#e7b58c", skin2="#c98f63", dark="#2a2140",
    grey="#9fb0d6", brown="#8a5a3c", red="#e2604f", white="#ffffff",
)

# ---------------------------------------------------------------------------
# WORD ICONS — each inner drawing sits on a soft rounded tile.
# ---------------------------------------------------------------------------
def tile(inner, a, b):
    return (
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" '
      'role="img">'
      '<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'
      '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/>'
      '</linearGradient></defs>'
      '<rect x="2" y="2" width="96" height="96" rx="20" fill="url(#g)"/>'
      '%s</svg>' % (a, b, inner)
    )

def _fill(fill, extra):
    # avoid emitting a duplicate fill= when the extra already specifies one
    return "" if "fill=" in extra else ('fill="%s" ' % fill)
def circle(cx, cy, r, fill, extra=""):
    return '<circle cx="%s" cy="%s" r="%s" %s%s/>' % (cx, cy, r, _fill(fill, extra), extra)
def rect(x, y, w, h, fill, rx=0, extra=""):
    return '<rect x="%s" y="%s" width="%s" height="%s" rx="%s" %s%s/>' % (x, y, w, h, rx, _fill(fill, extra), extra)
def path(d, fill, extra=""):
    return '<path d="%s" %s%s/>' % (d, _fill(fill, extra), extra)
def poly(pts, fill, extra=""):
    return '<polygon points="%s" %s%s/>' % (pts, _fill(fill, extra), extra)
def line(x1, y1, x2, y2, stroke, w=3, extra=""):
    return '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s" stroke-linecap="round" %s/>' % (x1, y1, x2, y2, stroke, w, extra)

def head_figure(skin, parka, cx=50, cy=44, s=1.0):
    """A simple hooded figure head+shoulders."""
    return (
      circle(cx, cy, 22*s, C["fur"]) +                 # fur hood
      circle(cx, cy, 16*s, skin) +                     # face
      circle(cx-6*s, cy-2*s, 2.2*s, C["dark"]) +
      circle(cx+6*s, cy-2*s, 2.2*s, C["dark"]) +
      path("M%s %s q%s %s %s 0" % (cx-6*s, cy+7*s, 6*s, 6*s, 12*s), "none",
           'stroke="%s" stroke-width="2.2" stroke-linecap="round"' % C["dark"]) +
      path("M%s 92 q%s -26 %s 0 Z" % (cx-26*s, 26*s, 52*s), parka)  # shoulders
    )

ICONS = {}
# --- family ---
ICONS["mother"]      = ("#3a2e5e", "#241c40", head_figure(C["skin"], C["parkaR"]))
ICONS["father"]      = ("#2b3a5e", "#1a2440", head_figure(C["skin2"], C["parkaB"]))
ICONS["grandfather"] = ("#3a3450", "#221f33",
    head_figure(C["skin2"], C["parkaG"]) +
    path("M40 40 q10 8 20 0", "none", 'stroke="%s" stroke-width="3"' % C["fur"]))  # grey brow
ICONS["woman"]       = ("#4a2e50", "#2a1a36", head_figure(C["skin"], C["parkaP"]))
ICONS["man"]         = ("#28405e", "#182636", head_figure(C["skin2"], C["parkaB"]))
ICONS["child"]       = ("#3a4a60", "#20303e", head_figure(C["skin"], C["ember"], cy=48, s=0.8))
ICONS["boy"]         = ("#2e4a58", "#1a2c34", head_figure(C["skin2"], C["parkaG"], cy=48, s=0.8))
ICONS["girl"]        = ("#4a2e58", "#2a1a34", head_figure(C["skin"], C["rose"], cy=48, s=0.8))
ICONS["baby"]        = ("#40506a", "#26323e",
    circle(50, 52, 20, C["fur"]) + circle(50, 52, 13, C["skin"]) +
    circle(45, 50, 1.8, C["dark"]) + circle(55, 50, 1.8, C["dark"]))
ICONS["sister"]      = ("#4a2e58", "#2a1a34", head_figure(C["skin"], C["rose"]))
ICONS["brother"]     = ("#2e4a58", "#1a2c34", head_figure(C["skin2"], C["parkaG"]))
ICONS["friend"]      = ("#2e3a5e", "#1a2440",
    head_figure(C["skin"], C["parkaR"], cx=38, s=0.72) +
    head_figure(C["skin2"], C["parkaB"], cx=64, s=0.72))
# --- body ---
skinface = ("#f0d9c4", "#d8b193")
ICONS["eye"]   = ("#5aa6c8", "#2f6f8c",
    '<ellipse cx="50" cy="50" rx="34" ry="20" fill="%s"/>' % C["white"] +
    circle(50, 50, 13, C["blue"]) + circle(50, 50, 6, C["dark"]) + circle(46, 46, 2.5, C["white"]))
ICONS["head"]  = ("#caa,","#a88",) if False else ("#e0b48f", "#c08f63",
    circle(50, 46, 24, C["skin"]) + circle(41, 44, 2.6, C["dark"]) + circle(59, 44, 2.6, C["dark"]) +
    path("M42 56 q8 7 16 0", "none", 'stroke="%s" stroke-width="3" stroke-linecap="round"' % C["dark"]))
ICONS["mouth"] = ("#c86a6a", "#9a3f3f",
    path("M28 46 q22 24 44 0 q-22 10 -44 0 Z", C["red"]) +
    rect(30, 44, 40, 4, C["white"], rx=2))
ICONS["nose"]  = ("#e0b48f", "#c08f63",
    path("M50 26 q10 30 12 44 q-12 8 -24 0 q2 -14 12 -44 Z", C["skin"]) +
    circle(44, 66, 2.4, C["skin2"]) + circle(56, 66, 2.4, C["skin2"]))
ICONS["ear"]   = ("#e0b48f", "#c08f63",
    path("M62 24 q-30 -6 -30 30 q0 22 18 22 q10 0 8 -12 q-2 -8 6 -10 q14 -4 -2 -30 Z", C["skin"]) +
    path("M50 40 q-10 4 -8 22", "none", 'stroke="%s" stroke-width="3" fill="none" stroke-linecap="round"' % C["skin2"]))
ICONS["arm"]   = ("#3a4a60", "#20303e",
    path("M30 30 l16 -6 l30 42 q6 10 -4 16 l-6 -12 Z", C["parkaB"]) +
    circle(74, 78, 9, C["skin"]))
ICONS["cheek"] = ("#e0b48f", "#c08f63", circle(50, 46, 24, C["skin"]) + circle(58, 52, 8, C["rose"], 'opacity="0.6"'))
ICONS["chin"]  = ("#e0b48f", "#c08f63", circle(50, 42, 24, C["skin"]) + path("M36 52 q14 22 28 0", "none", 'stroke="%s" stroke-width="3" fill="none"' % C["skin2"]))
ICONS["beard"] = ("#3a3450", "#221f33", circle(50, 40, 22, C["skin2"]) + path("M30 44 q20 40 40 0 q-4 26 -20 28 q-16 -2 -20 -28 Z", C["fur"]))
ICONS["blood"] = ("#5a2030", "#33121c", path("M50 20 q18 30 18 44 a18 18 0 1 1 -36 0 q0 -14 18 -44 Z", C["red"]))
# --- animals ---
ICONS["dog"] = ("#3a4a60", "#20303e",
    '<ellipse cx="52" cy="60" rx="26" ry="16" fill="%s"/>' % C["brown"] +
    circle(30, 48, 12, C["brown"]) + poly("22,38 26,50 34,46", C["brown"]) + poly("40,38 34,50 44,46", C["brown"]) +
    circle(26, 48, 2, C["dark"]) + circle(22, 52, 2, C["dark"]) +
    path("M74 52 q10 -6 8 8", "none", 'stroke="%s" stroke-width="5" fill="none" stroke-linecap="round"' % C["brown"]))
ICONS["caribou"] = ("#3a4a3e", "#1f2a22",
    '<ellipse cx="54" cy="62" rx="24" ry="14" fill="%s"/>' % C["brown"] +
    circle(34, 52, 11, C["brown"]) +
    path("M30 44 q-6 -18 -14 -20 M34 42 q-2 -20 4 -26 M40 42 q4 -16 12 -18", "none",
         'stroke="%s" stroke-width="3" fill="none" stroke-linecap="round"' % C["fur"]) +
    circle(30, 52, 2, C["dark"]))
ICONS["seal"] = ("#3a5a6e", "#1f3240",
    '<ellipse cx="50" cy="58" rx="30" ry="18" fill="%s"/>' % C["steel"] +
    circle(30, 48, 12, C["steel"]) + circle(26, 46, 2.4, C["dark"]) + circle(33, 46, 2.4, C["dark"]) +
    line(20, 50, 30, 50, C["night"], 1.5) + line(20, 54, 30, 54, C["night"], 1.5) +
    poly("74,50 84,44 82,58", C["steel"]))
ICONS["bear"] = ("#40506a", "#26323e",
    '<ellipse cx="52" cy="60" rx="28" ry="17" fill="%s"/>' % C["fur"] +
    circle(32, 50, 14, C["fur"]) + circle(24, 40, 5, C["fur"]) + circle(40, 40, 5, C["fur"]) +
    circle(28, 50, 2.2, C["dark"]) + circle(36, 50, 2.2, C["dark"]) + circle(32, 56, 3, C["dark"]))
ICONS["loon"] = ("#26405e", "#152436",
    '<ellipse cx="50" cy="60" rx="26" ry="14" fill="%s"/>' % C["dark"] +
    path("M58 30 q16 4 12 24", "none", 'stroke="%s" stroke-width="10" fill="none" stroke-linecap="round"' % C["dark"]) +
    circle(70, 30, 8, C["dark"]) + poly("76,28 90,30 76,34", C["gold"]) +
    circle(72, 28, 2, C["red"]) +
    line(34, 56, 66, 56, C["white"], 1.6, 'opacity="0.7"'))
ICONS["fish"] = ("#2f6f8c", "#184454",
    '<ellipse cx="46" cy="52" rx="28" ry="15" fill="%s"/>' % C["blue"] +
    poly("70,52 88,40 88,64", C["blue"]) + circle(30, 48, 3, C["white"]) + circle(30, 48, 1.5, C["dark"]) +
    path("M40 40 q6 6 0 24 M52 38 q6 8 0 28", "none", 'stroke="%s" stroke-width="2" fill="none" opacity="0.5"' % C["night"]))
# --- food ---
ICONS["eat"] = ("#4a3a2e", "#2a2018",
    circle(50, 54, 22, C["fur"]) + circle(50, 54, 15, C["ember"]) +
    line(30, 30, 30, 70, C["grey"], 4) + line(72, 30, 72, 70, C["grey"], 4) + poly("68,30 76,30 74,44 70,44", C["grey"]))
ICONS["meat"] = ("#4a2e2e", "#2a1818",
    path("M28 44 q22 -18 44 0 q6 22 -22 26 q-28 -4 -22 -26 Z", C["red"]) +
    rect(44, 30, 12, 14, C["fur"], rx=4))
ICONS["blubber"] = ("#3a4a5e", "#20303e", rect(28, 34, 44, 34, C["fur"], rx=10) + rect(34, 40, 32, 8, C["rose"], rx=4) + rect(34, 52, 32, 8, C["ice"], rx=4))
ICONS["egg"] = ("#4a4436", "#2a2820", '<ellipse cx="50" cy="54" rx="18" ry="24" fill="%s"/>' % C["fur"])
ICONS["berry"] = ("#3a2e4a", "#201830",
    circle(40, 56, 10, C["violet"]) + circle(58, 58, 10, C["violet"]) + circle(50, 44, 10, C["rose"]) +
    line(50, 44, 44, 28, C["green"], 3))
# --- clothing ---
ICONS["boot"] = ("#3a2e2e", "#201818",
    path("M40 24 l14 0 l0 34 l18 6 q8 4 8 12 l-40 0 l0 -58 Z", C["brown"]) +
    rect(38, 72, 44, 8, C["dark"], rx=3) + line(42, 34, 52, 34, C["fur"], 3))
ICONS["coat"] = ("#2e3a5e", "#1a2440",
    path("M34 28 q16 -8 32 0 l10 8 l-8 12 l-4 -4 l0 34 l-28 0 l0 -34 l-4 4 l-8 -12 Z", C["parkaB"]) +
    path("M50 24 q10 2 12 10 q-12 8 -24 0 q2 -8 12 -10 Z", C["fur"]))
ICONS["mitt"] = ("#3a2e4a", "#201830",
    path("M40 30 q18 -6 26 8 l0 30 q-2 8 -12 8 l-14 0 l0 -46 Z", C["parkaR"]) +
    path("M40 44 q-10 0 -10 10 q0 8 10 8 Z", C["parkaR"]) + rect(38, 70, 30, 6, C["fur"], rx=3))
ICONS["clothing"] = ("#3a3450", "#221f33",
    path("M30 30 l14 -4 l6 8 l6 -8 l14 4 l6 12 l-10 6 l0 26 l-32 0 l0 -26 l-10 -6 Z", C["parkaG"]))
ICONS["hood"] = ("#2e3a5e", "#1a2440", circle(50, 52, 26, C["parkaB"]) + circle(50, 52, 18, C["fur"]) + circle(50, 54, 12, C["skin"]))
# --- weather / land / nature ---
ICONS["snow"] = ("#3a4a6e", "#20304a",
    line(50, 26, 50, 74, C["snow"], 4) + line(26, 50, 74, 50, C["snow"], 4) +
    line(33, 33, 67, 67, C["snow"], 4) + line(67, 33, 33, 67, C["snow"], 4) + circle(50, 50, 4, C["ice"]))
ICONS["wind"] = ("#2f5a6e", "#183440",
    path("M24 40 h34 a7 7 0 1 0 -7 -7", "none", 'stroke="%s" stroke-width="5" fill="none" stroke-linecap="round"' % C["ice"]) +
    path("M24 54 h44 a7 7 0 1 1 -7 7", "none", 'stroke="%s" stroke-width="5" fill="none" stroke-linecap="round"' % C["snow"]) +
    path("M24 68 h24", "none", 'stroke="%s" stroke-width="5" fill="none" stroke-linecap="round"' % C["ice"]))
ICONS["cold"] = ("#2e4a6e", "#182c40",
    '<ellipse cx="50" cy="50" rx="30" ry="30" fill="none" stroke="%s" stroke-width="3"/>' % C["ice"] +
    line(50, 24, 50, 76, C["snow"], 3) + line(28, 38, 72, 62, C["snow"], 3) + line(72, 38, 28, 62, C["snow"], 3))
ICONS["storm"] = ("#242a44", "#141830",
    path("M30 30 q-6 16 8 18 h34 q14 -2 8 -16 q-2 -12 -16 -12 q-6 -10 -18 -4 q-12 0 -16 14 Z", C["grey"]) +
    poly("52,50 42,68 50,66 44,80 62,58 54,60", C["gold"]))
ICONS["cloud"] = ("#3a4a66", "#20304a",
    path("M30 58 q-8 -18 10 -20 q4 -14 20 -8 q16 -4 16 12 q12 2 6 16 q-4 6 -12 4 l-36 0 q-8 0 -10 -6 Z", C["snow"]))
ICONS["fog"] = ("#3a4658", "#202a36",
    line(26, 40, 74, 40, C["grey"], 6) + line(30, 52, 70, 52, C["snow"], 6) + line(24, 64, 76, 64, C["grey"], 6))
ICONS["sea"] = ("#1f5a6e", "#0f3240",
    rect(2, 50, 96, 48, C["steel"]) +
    path("M6 56 q10 -8 20 0 t20 0 t20 0 t20 0", "none", 'stroke="%s" stroke-width="3" fill="none"' % C["ice"]) +
    path("M6 68 q10 -8 20 0 t20 0 t20 0 t20 0", "none", 'stroke="%s" stroke-width="3" fill="none"' % C["snow"]))
ICONS["water"] = ("#2f6f8c", "#184454",
    path("M50 22 q22 30 22 44 a22 22 0 1 1 -44 0 q0 -14 22 -44 Z", C["blue"]) +
    path("M42 56 q-2 10 6 14", "none", 'stroke="%s" stroke-width="3" fill="none" stroke-linecap="round"' % C["white"]))
ICONS["shore"] = ("#3a4a4e", "#20302a",
    rect(2, 58, 96, 40, C["steel"]) + path("M2 58 q30 -14 60 -2 q20 8 36 4 l0 40 l-96 0 Z", C["brown"]))
ICONS["rock"] = ("#3a3a44", "#20202a",
    path("M24 66 q-4 -22 18 -24 q10 -14 24 -2 q16 0 12 20 q2 8 -8 8 l-38 0 q-8 0 -8 -2 Z", C["grey"]) +
    path("M40 50 l8 8 l-6 8", "none", 'stroke="%s" stroke-width="2" fill="none"' % C["dark"]))
ICONS["beach"] = ("#4a4636", "#2a2820",
    rect(2, 62, 96, 36, C["gold"]) + rect(2, 50, 96, 14, C["steel"]) +
    path("M2 56 q12 -6 24 0 t24 0 t24 0 t24 0", "none", 'stroke="%s" stroke-width="2.5" fill="none"' % C["ice"]))
ICONS["sun"] = ("#3a2e1e", "#221810",
    circle(50, 50, 18, C["gold"]) +
    "".join(line(50, 50, 50+34*__import__('math').cos(a), 50+34*__import__('math').sin(a), C["amber"], 4)
            for a in [i*0.7854 for i in range(8)]))
ICONS["moon"] = ("#20264a", "#12162e",
    path("M58 24 a28 28 0 1 0 0 52 a22 22 0 1 1 0 -52 Z", C["fur"]) +
    circle(46, 40, 3, C["grey"], 'opacity="0.6"') + circle(40, 56, 2, C["grey"], 'opacity="0.6"'))
ICONS["star"] = ("#20264a", "#12162e",
    poly("50,20 57,42 80,42 61,56 68,78 50,64 32,78 39,56 20,42 43,42", C["gold"]))
ICONS["night"] = ("#141a36", "#0a0e22",
    path("M60 26 a24 24 0 1 0 0 48 a19 19 0 1 1 0 -48 Z", C["fur"]) +
    poly("30,34 33,42 41,42 35,47 37,55 30,50 23,55 25,47 19,42 27,42", C["gold"]))
ICONS["fire"] = ("#3a1e1a", "#220f0c",
    path("M50 22 q16 18 12 34 q14 -2 8 -18 q10 10 6 26 q-6 18 -26 18 q-22 0 -26 -20 q-2 -16 12 -22 q-4 12 6 14 q-8 -18 8 -32 Z", C["ember"]) +
    path("M50 44 q8 10 4 20 q-4 10 -12 8 q-8 -2 -6 -14 q2 -10 14 -14 Z", C["gold"]))
# --- hunting & tools ---
ICONS["knife"] = ("#2e3440", "#181c26",
    path("M24 62 q30 -30 46 -34 q4 8 -2 14 q-16 10 -34 30 Z", C["ice"]) +
    rect(18, 60, 16, 8, C["brown"], rx=3, extra='transform="rotate(-40 26 64)"'))
ICONS["net"] = ("#2f5a5e", "#183234",
    "".join(line(24, 26+i*12, 76, 26+i*12, C["ice"], 2) for i in range(5)) +
    "".join(line(24+i*13, 26, 24+i*13, 74, C["ice"], 2) for i in range(5)))
ICONS["spear"] = ("#2e3440", "#181c26",
    line(28, 74, 66, 30, C["brown"], 5) + poly("66,30 76,22 72,36", C["ice"]))
ICONS["hook"] = ("#2e3a44", "#181f28",
    path("M52 22 l0 30 q0 18 -16 18 q-14 0 -14 -14", "none",
         'stroke="%s" stroke-width="5" fill="none" stroke-linecap="round"' % C["grey"]) +
    poly("22,56 16,48 26,48", C["grey"]))
ICONS["boat"] = ("#2f5a6e", "#183440",
    path("M18 52 q32 22 64 0 q-6 18 -32 18 q-26 0 -32 -18 Z", C["brown"]) +
    line(50, 20, 50, 52, C["grey"], 4) + poly("50,24 50,44 70,34", C["fur"]))
# --- nouns added for the nouns-only revision ---
ICONS["snowhouse"] = ("#2e3e6a", "#16223e",
    path("M18 72 q32 -48 64 0 Z", C["fur"]) +
    path("M20 72 q30 -42 60 0", "none", 'stroke="%s" stroke-width="2" fill="none" opacity="0.6"' % C["steel"]) +
    line(34, 58, 34, 72, C["steel"], 2) + line(50, 52, 50, 72, C["steel"], 2) + line(66, 58, 66, 72, C["steel"], 2) +
    path("M42 72 q8 -16 16 0 Z", C["deep"]) + rect(16, 72, 68, 6, C["snow"], rx=2))
ICONS["sled"] = ("#3a2e22", "#201810",
    rect(20, 60, 60, 6, C["brown"], rx=3) + rect(20, 44, 60, 6, C["brown"], rx=3) +
    "".join(rect(28 + i * 12, 46, 5, 18, C["brown"]) for i in range(5)) +
    path("M20 60 q-8 0 -8 -10", "none", 'stroke="%s" stroke-width="6" fill="none" stroke-linecap="round"' % C["brown"]))
ICONS["grandchild"] = ("#3a4a60", "#20303e", head_figure(C["skin"], C["ember"], cy=50, s=0.82))
ICONS["raven"] = ("#20263a", "#10131f",
    '<ellipse cx="52" cy="58" rx="26" ry="15" fill="%s"/>' % C["dark"] +
    circle(32, 46, 12, C["dark"]) + poly("22,44 8,48 22,52", C["dark"]) +
    circle(30, 44, 3, C["gold"]) + circle(30, 44, 1.4, C["dark"]) +
    path("M62 52 q14 -8 12 10", "none", 'stroke="%s" stroke-width="6" fill="none" stroke-linecap="round"' % C["dark"]) +
    path("M44 50 q10 6 22 2", "none", 'stroke="%s" stroke-width="2" fill="none" opacity="0.5"' % C["steel"]))
ICONS["spring"] = ("#2e4a3e", "#16281f",
    circle(64, 34, 12, C["gold"]) +
    "".join(line(64, 34, 64 + 20 * __import__('math').cos(a), 34 + 20 * __import__('math').sin(a), C["amber"], 3) for a in [i * 0.7854 for i in range(8)]) +
    path("M20 66 q14 -8 28 0 t28 0", "none", 'stroke="%s" stroke-width="4" fill="none"' % C["blue"]) +
    line(38, 60, 38, 44, C["green"], 3) + path("M38 50 q8 -4 10 -10", "none", 'stroke="%s" stroke-width="3" fill="none"' % C["green"]))

# --- actions ---
ICONS["see"] = ICONS["eye"]
ICONS["come"] = ("#2e4a4e", "#182a2c",
    path("M28 50 h34", "none", 'stroke="%s" stroke-width="6" fill="none" stroke-linecap="round"' % C["green"]) +
    poly("56,36 78,50 56,64", C["green"]))
ICONS["sleep"] = ("#20264a", "#12162e",
    path("M60 26 a24 24 0 1 0 0 48 a19 19 0 1 1 0 -48 Z", C["fur"]) +
    '<text x="30" y="44" font-size="16" fill="%s" font-family="sans-serif">z</text>' % C["ice"] +
    '<text x="24" y="60" font-size="22" fill="%s" font-family="sans-serif">Z</text>' % C["ice"])
ICONS["run"] = ("#2e4a58", "#182c34",
    circle(58, 30, 7, C["skin"]) +
    path("M58 38 l-8 16 l10 12 M50 54 l-16 6 M50 44 l16 4 l6 14", "none",
         'stroke="%s" stroke-width="5" fill="none" stroke-linecap="round"' % C["ember"]))
ICONS["walk"] = ("#2e4a58", "#182c34",
    circle(52, 28, 7, C["skin"]) +
    path("M52 36 l0 20 l-10 16 M52 56 l10 16 M52 44 l12 2 M52 44 l-12 2", "none",
         'stroke="%s" stroke-width="5" fill="none" stroke-linecap="round"' % C["blue"]))
ICONS["sing"] = ("#3a2e4a", "#201830",
    circle(44, 50, 14, C["skin"]) + circle(44, 52, 6, C["red"]) +
    '<text x="64" y="40" font-size="20" fill="%s" font-family="sans-serif">&#9834;</text>' % C["gold"] +
    '<text x="70" y="60" font-size="16" fill="%s" font-family="sans-serif">&#9835;</text>' % C["green"])
ICONS["dance"] = ("#4a2e50", "#2a1a36",
    circle(50, 26, 7, C["skin"]) +
    path("M50 34 l0 18 l-12 18 M50 52 l12 18 M50 40 l-16 -6 M50 40 l16 8", "none",
         'stroke="%s" stroke-width="5" fill="none" stroke-linecap="round"' % C["violet"]))
ICONS["whip"] = ("#3a2e2e", "#201818",
    path("M24 70 q20 -10 26 -26 q4 -12 16 -16 q-6 10 -2 16 q-16 4 -20 20 q-6 14 -20 6 Z", C["brown"]))
ICONS["strong"] = ("#3a3020", "#221c12",
    path("M32 44 q-8 0 -8 8 q0 8 8 8 l4 0 l0 -16 Z", C["skin"]) +
    rect(34, 42, 8, 20, C["skin"]) + rect(58, 42, 8, 20, C["skin"]) +
    rect(42, 48, 16, 8, C["grey"]) + circle(30, 40, 8, C["parkaR"]) + circle(70, 40, 8, C["parkaR"]))
# --- greetings (abstract) ---
ICONS["yes"] = ("#2e4a3a", "#182a22", path("M28 52 l14 16 l32 -34", "none",
    'stroke="%s" stroke-width="9" fill="none" stroke-linecap="round" stroke-linejoin="round"' % C["green"]))
ICONS["no"] = ("#4a2e2e", "#2a1818", line(32, 32, 68, 68, C["red"], 9) + line(68, 32, 32, 68, C["red"], 9))
ICONS["thanks"] = ("#3a2e4a", "#201830",
    path("M50 70 q-24 -14 -24 -32 q0 -12 12 -12 q8 0 12 8 q4 -8 12 -8 q12 0 12 12 q0 18 -24 32 Z", C["rose"]))
ICONS["sorry"] = ("#3a3444", "#201d28",
    circle(50, 46, 20, C["skin"]) + circle(43, 44, 2.4, C["dark"]) + circle(57, 44, 2.4, C["dark"]) +
    path("M42 58 q8 -8 16 0", "none", 'stroke="%s" stroke-width="3" fill="none" stroke-linecap="round"' % C["dark"]))

# placeholder
PLACE = tile(
    circle(50, 44, 16, C["grey"]) + rect(34, 62, 32, 6, C["grey"], rx=3) +
    '<text x="50" y="50" font-size="20" fill="%s" font-family="sans-serif" text-anchor="middle" dominant-baseline="middle">?</text>' % C["night"],
    C["panel"], C["deep"])

def build_icons():
    for slug, spec in ICONS.items():
        a, b, inner = spec
        write("words/%s.svg" % slug, tile(inner, a, b))
    write("words/_placeholder.svg", PLACE)

# ---------------------------------------------------------------------------
# CHARACTER PORTRAITS (240 x 300)
# ---------------------------------------------------------------------------
def portrait(bg1, bg2, body, name=""):
    return (
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 300" role="img">'
      '<defs><radialGradient id="bg" cx="50%%" cy="35%%" r="80%%">'
      '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></radialGradient></defs>'
      '<rect width="240" height="300" fill="url(#bg)"/>%s</svg>' % (bg1, bg2, body)
    )

def person(parka, skin, hair=None, extra=""):
    body = (
      # shoulders / parka
      path("M40 300 q0 -90 80 -90 q80 0 80 90 Z", parka) +
      # fur ruff
      '<ellipse cx="120" cy="150" rx="78" ry="30" fill="%s"/>' % C["fur"] +
      circle(120, 120, 60, C["fur"]) +          # hood fur
      circle(120, 120, 46, skin) +              # face
      circle(103, 116, 4.5, C["dark"]) + circle(137, 116, 4.5, C["dark"]) +
      path("M104 140 q16 14 32 0", "none",
           'stroke="%s" stroke-width="4" fill="none" stroke-linecap="round"' % C["dark"]) +
      circle(100, 132, 6, C["rose"], 'opacity="0.35"') + circle(140, 132, 6, C["rose"], 'opacity="0.35"') +
      extra
    )
    if hair:
        body = path("M74 118 q46 -40 92 0 q-6 -28 -46 -28 q-40 0 -46 28 Z", hair) + body
    return body

CHARS = {}
CHARS["grandmother"] = portrait("#3a2e5e", "#1a1430",
    person(C["parkaR"], C["skin"], hair=None,
           extra=path("M96 108 q10 6 20 0 M124 108 q10 6 20 0", "none",
                      'stroke="%s" stroke-width="3" fill="none"' % C["grey"]) +   # brows
                 path("M92 150 q28 8 56 0", "none", 'stroke="%s" stroke-width="2" fill="none" opacity="0.5"' % C["skin2"])))
CHARS["hunter"] = portrait("#26405e", "#101c30",
    person(C["parkaB"], C["skin2"], extra=path("M96 150 q24 12 48 0 q-4 16 -24 16 q-20 0 -24 -16 Z", C["dark"], 'opacity="0.85"')))  # beard
CHARS["mother"] = portrait("#4a2e50", "#241628", person(C["parkaP"], C["skin"]))
CHARS["child"] = portrait("#2e4a58", "#16262e",
    '<svg></svg>' if False else person(C["ember"], C["skin"]))
CHARS["raven"] = portrait("#1a2036", "#0a0e1c",
    '<ellipse cx="120" cy="200" rx="70" ry="60" fill="%s"/>' % C["dark"] +
    circle(120, 120, 52, C["dark"]) +
    path("M120 96 q40 6 34 40 q-6 -8 -20 -6 Z", C["dark"]) +          # beak base
    poly("150,120 196,128 150,140", "#20263a") +                      # beak
    circle(108, 112, 7, C["gold"]) + circle(108, 112, 3, C["dark"]) +
    path("M70 150 q-30 30 -6 60 M170 150 q30 30 6 60", "none",
         'stroke="%s" stroke-width="10" fill="none" stroke-linecap="round"' % "#20263a"))
CHARS["spirit"] = portrait("#1e2a4e", "#0c1226",
    '<ellipse cx="120" cy="170" rx="70" ry="90" fill="%s" opacity="0.5"/>' % C["violet"] +
    circle(120, 120, 50, C["violet"], 'opacity="0.7"') + circle(120, 120, 40, C["fur"], 'opacity="0.6"') +
    circle(104, 116, 6, C["night"]) + circle(136, 116, 6, C["night"]) +
    "".join(circle(60+i*24, 60+((i*37)%40), 3, C["green"], 'opacity="0.8"') for i in range(6)))
CHARS["seawoman"] = portrait("#123a4e", "#06202c",
    path("M120 120 q60 40 40 160 l-80 0 q-20 -120 40 -160 Z", C["ice"], 'opacity="0.7"') +
    path("M70 110 q50 -50 100 0 q-10 60 -50 70 q-40 -10 -50 -70 Z", C["blue"]) +   # long hair
    circle(120, 120, 44, C["ice"]) + circle(105, 118, 4.5, C["night"]) + circle(135, 118, 4.5, C["night"]) +
    path("M106 138 q14 8 28 0", "none", 'stroke="%s" stroke-width="3" fill="none" stroke-linecap="round"' % C["night"]))
# enemies
CHARS["shadow"] = portrait("#141026", "#060410",
    path("M120 40 q70 40 60 140 q-8 70 -60 76 q-52 -6 -60 -76 q-10 -100 60 -140 Z", C["dark"]) +
    circle(102, 120, 9, C["red"]) + circle(138, 120, 9, C["red"]) +
    circle(102, 120, 3, C["gold"]) + circle(138, 120, 3, C["gold"]) +
    path("M96 160 q24 -14 48 0 q-8 18 -24 18 q-16 0 -24 -18 Z", C["night"]))
CHARS["icebeast"] = portrait("#173049", "#081627",
    path("M60 220 q0 -110 60 -110 q60 0 60 110 Z", C["steel"]) +
    circle(120, 120, 56, C["ice"]) +
    poly("120,54 108,96 132,96", C["ice"]) +
    poly("78,84 84,120 60,110", C["ice"]) + poly("162,84 156,120 180,110", C["ice"]) +
    circle(104, 118, 7, C["blue"]) + circle(136, 118, 7, C["blue"]) +
    circle(104, 118, 3, C["night"]) + circle(136, 118, 3, C["night"]) +
    path("M100 150 l10 -6 l10 6 l10 -6 l10 6", "none",
         'stroke="%s" stroke-width="3" fill="none"' % C["night"]))
CHARS["hunger"] = portrait("#2a1420", "#120810",
    path("M120 50 q64 30 56 150 q-6 60 -56 66 q-50 -6 -56 -66 q-8 -120 56 -150 Z", "#3a2030") +
    circle(104, 116, 10, C["gold"]) + circle(136, 116, 10, C["gold"]) + circle(104, 116, 4, C["night"]) + circle(136, 116, 4, C["night"]) +
    path("M96 150 q24 20 48 0 l0 6 q-24 22 -48 0 Z", C["night"]) +
    "".join(poly("%s,158 %s,150 %s,150" % (100+i*8, 96+i*8, 104+i*8), C["fur"]) for i in range(6)))

def build_chars():
    for slug, svg in CHARS.items():
        write("chars/%s.svg" % slug, svg)

# ---------------------------------------------------------------------------
# BACKGROUNDS (1200 x 675)
# ---------------------------------------------------------------------------
def bg_frame(defs, body):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 675" '
            'preserveAspectRatio="xMidYMid slice" role="img"><defs>%s</defs>%s</svg>' % (defs, body))

def lin(id, stops, x1=0,y1=0,x2=0,y2=1):
    s = "".join('<stop offset="%s" stop-color="%s"/>' % (o, c) for o, c in stops)
    return '<linearGradient id="%s" x1="%s" y1="%s" x2="%s" y2="%s">%s</linearGradient>' % (id, x1, y1, x2, y2, s)

def build_bg():
    # snow-house interior (warm lamplight)
    write("bg/snowhouse.svg", bg_frame(
        lin("sk", [("0", "#20305a"), ("1", "#0c1330")]) +
        '<radialGradient id="lamp" cx="50%" cy="70%" r="60%"><stop offset="0" stop-color="#ffcf7a"/><stop offset="0.5" stop-color="#c98a44" stop-opacity="0.5"/><stop offset="1" stop-color="#0c1330" stop-opacity="0"/></radialGradient>',
        rect(0,0,1200,675,"url(#sk)") +
        # snow dome
        path("M120 675 q480 -560 960 0 Z", "#22305a") +
        # curved block seams inside the dome
        "".join('<path d="M%s 675 q%s -%s %s -%s" stroke="#33436e" stroke-width="2.5" fill="none" opacity="0.6"/>' % (150+i*95, (600-(150+i*95))*0.2, 300+i*8, (600-(150+i*95))*0.5, 300+i*8) for i in range(10)) +
        # horizontal wall courses
        "".join(line(140, y, 1060, y, "#2a3a66", 2, 'opacity="0.4"') for y in (300, 380, 460)) +
        rect(0,0,1200,675,"url(#lamp)") +
        # qulliq lamp
        '<ellipse cx="600" cy="560" rx="120" ry="30" fill="#2a2030"/>' +
        path("M500 560 q100 -40 200 0 q-8 26 -100 26 q-92 0 -100 -26 Z", "#4a3a2a") +
        "".join(path("M%s 556 q6 -30 12 0 Z" % (520+i*30), C["amber"]) for i in range(6)) +
        '<ellipse cx="600" cy="556" rx="90" ry="12" fill="#ffcf7a" opacity="0.8"/>'
    ))
    # aurora night sky over tundra
    write("bg/aurora.svg", bg_frame(
        lin("sky", [("0", "#0a0e26"), ("0.6", "#122045"), ("1", "#0c1730")]) +
        lin("au", [("0", "#7ef1c9"), ("1", "#0a0e26")], 0,0,0,1),
        rect(0,0,1200,675,"url(#sky)") +
        "".join(circle((i*137)%1200, (i*89)%360, (i%3)*0.6+0.6, C["white"], 'opacity="0.8"') for i in range(90)) +
        # aurora bands
        path("M-40 200 q300 -120 640 20 q300 130 640 -30 l0 120 q-340 150 -640 20 q-340 -130 -640 -10 Z", C["green"], 'opacity="0.35"') +
        path("M-40 260 q300 -100 640 40 q300 120 640 -10 l0 80 q-340 120 -640 0 q-340 -120 -640 -20 Z", C["violet"], 'opacity="0.28"') +
        path("M-40 320 q360 -80 700 40 q280 100 580 0 l0 60 q-320 100 -600 10 q-360 -110 -680 -30 Z", C["blue"], 'opacity="0.22"') +
        # tundra ridge
        path("M0 560 q300 -60 600 -10 q300 50 600 -20 l0 145 l-1200 0 Z", "#0e1730") +
        path("M0 600 q300 -30 600 0 q300 30 600 -10 l0 85 l-1200 0 Z", "#0a1226")
    ))
    # grey sea + ice floes
    write("bg/sea.svg", bg_frame(
        lin("sky2", [("0", "#5b6f92"), ("1", "#9fb0c9")]) +
        lin("water", [("0", "#3f6a86"), ("1", "#1d3a4e")]),
        rect(0,0,1200,340,"url(#sky2)") +
        circle(980, 120, 60, "#e9d9b0", 'opacity="0.7"') +
        rect(0,300,1200,375,"url(#water)") +
        "".join(path("M0 %s q300 -14 600 0 t600 0 l0 30 l-1200 0 Z" % y, "#4a6f8a", 'opacity="0.4"') for y in [330, 380, 440, 520]) +
        # ice floes
        path("M120 470 q80 -20 160 4 q40 30 -30 40 q-120 8 -150 -14 q-20 -20 20 -30 Z", C["snow"]) +
        path("M820 520 q120 -24 200 8 q30 28 -50 34 q-150 6 -170 -18 q-10 -18 20 -24 Z", "#dce8f4") +
        path("M520 600 q90 -16 150 6 q20 22 -40 26 q-110 4 -130 -14 Z", C["snow"])
    ))
    # tundra / coast day
    write("bg/tundra.svg", bg_frame(
        lin("sky3", [("0", "#7fb0d6"), ("1", "#cfe4f2")]) +
        lin("gr", [("0", "#6f7f5a"), ("1", "#4a5a3a")]),
        rect(0,0,1200,675,"url(#sky3)") +
        circle(220, 130, 54, "#fff2cf") +
        path("M0 420 q300 -80 600 -20 q300 60 600 -30 l0 305 l-1200 0 Z", "#8a9a6a") +
        rect(0,470,1200,205,"url(#gr)") +
        "".join(path("M%s 470 q6 -30 12 0 Z" % x, "#5a6a3a") for x in range(60, 1180, 90)) +
        "".join(circle(x, 500+((x*7)%40), 5, C["rose"], 'opacity="0.6"') for x in range(120, 1120, 160))
    ))
    # title / map
    write("bg/title.svg", bg_frame(
        lin("t", [("0", "#0a0e26"), ("1", "#122045")]),
        rect(0,0,1200,675,"url(#t)") +
        "".join(circle((i*197)%1200, (i*113)%675, (i%3)*0.7+0.5, C["white"], 'opacity="0.7"') for i in range(120)) +
        path("M-40 240 q320 -120 660 10 q320 130 620 -20 l0 90 q-300 140 -620 10 q-340 -130 -660 -10 Z", C["green"], 'opacity="0.30"') +
        path("M-40 300 q320 -90 660 30 q300 110 620 0 l0 70 q-300 110 -620 0 q-340 -110 -660 -20 Z", C["violet"], 'opacity="0.24"') +
        path("M0 560 q300 -50 600 -6 q300 44 600 -16 l0 137 l-1200 0 Z", "#0c1428")
    ))

if __name__ == "__main__":
    build_icons()
    build_chars()
    build_bg()
    n = sum(len(f) for _, _, f in os.walk(ROOT))
    print("assets written under", ROOT + "/")
    for d in ("words", "chars", "bg"):
        p = os.path.join(ROOT, d)
        print("  %s/: %d files" % (d, len(os.listdir(p))))
