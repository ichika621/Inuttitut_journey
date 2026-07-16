# -*- coding: utf-8 -*-
"""Generate expression-sheet character portraits and scene backgrounds for the
visual-novel production. Original flat-illustration SVG, CC0 (see assets/CREDITS).
No photos of real people; no sacred/ceremonial imagery. Swappable asset layer:
real art can replace these at the same paths.

Writes:
  assets/chars/<name>/<expression>.svg   240x300 portraits, one per expression
  assets/bg/<scene>.svg                  1200x675 backgrounds
"""
import io, os, math

ROOT = "assets"
def write(path, svg):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    io.open(full, "w", encoding="utf-8").write(svg)

C = dict(
    night="#0b1020", deep="#152142", panel="#1d2a52",
    snow="#eef4ff", ice="#8fe3d6", blue="#6fb7ff", steel="#4b6aa5",
    amber="#ffcf7a", ember="#ff9f5a", gold="#ffd479",
    green="#7ef1c9", violet="#b79bff", rose="#ff8ba7",
    parkaR="#c96f4a", parkaB="#3f6fa8", parkaG="#5a8f6b", parkaP="#8f6fb0",
    fur="#f3ece0", skin="#e7b58c", skin2="#c98f63", dark="#2a2140",
    grey="#9fb0d6", brown="#8a5a3c", red="#e2604f", white="#ffffff",
)
def _f(fill, extra): return "" if "fill=" in extra else ('fill="%s" ' % fill)
def circle(cx, cy, r, fill, extra=""): return '<circle cx="%s" cy="%s" r="%s" %s%s/>' % (cx, cy, r, _f(fill, extra), extra)
def rect(x, y, w, h, fill, rx=0, extra=""): return '<rect x="%s" y="%s" width="%s" height="%s" rx="%s" %s%s/>' % (x, y, w, h, rx, _f(fill, extra), extra)
def path(d, fill, extra=""): return '<path d="%s" %s%s/>' % (d, _f(fill, extra), extra)
def poly(pts, fill, extra=""): return '<polygon points="%s" %s%s/>' % (pts, _f(fill, extra), extra)
def line(x1, y1, x2, y2, s, w=3, extra=""): return '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s" stroke-linecap="round" %s/>' % (x1, y1, x2, y2, s, w, extra)
def stroke(d, s, w, extra=""): return '<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round" %s/>' % (d, s, w, extra)

def frame(bg1, bg2, body):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 300" role="img">'
      '<defs><radialGradient id="bg" cx="50%%" cy="34%%" r="82%%">'
      '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></radialGradient></defs>'
      '<rect width="240" height="300" fill="url(#bg)"/>%s</svg>' % (bg1, bg2, body))

# ---- expression parameters ----
# brow: y-offset & tilt; eyes: 'open'|'wide'|'closed'|'soft'; mouth: shape; tear: bool; blush: bool
EXPR = {
    "neutral":      dict(brow=0, tilt=0, eyes="open", mouth="flat"),
    "wonder":       dict(brow=-6, tilt=0, eyes="wide", mouth="o", blush=True),
    "fear":         dict(brow=-4, tilt=6, eyes="wide", mouth="frown"),
    "determination":dict(brow=4, tilt=-6, eyes="open", mouth="firm"),
    "joy":          dict(brow=-3, tilt=0, eyes="soft", mouth="grin", blush=True),
    "warm":         dict(brow=-2, tilt=0, eyes="soft", mouth="smile", blush=True),
    "teaching":     dict(brow=-2, tilt=0, eyes="open", mouth="talk"),
    "worried":      dict(brow=-7, tilt=7, eyes="open", mouth="frown"),
    "proud":        dict(brow=-2, tilt=0, eyes="soft", mouth="smile", tear=True, blush=True),
    "tender":       dict(brow=-3, tilt=2, eyes="soft", mouth="smile", tear=True),
    "laughing":     dict(brow=-4, tilt=0, eyes="closed", mouth="grin", blush=True),
    "pouting":      dict(brow=3, tilt=0, eyes="open", mouth="pout"),
    "scared":       dict(brow=-6, tilt=8, eyes="wide", mouth="frown"),
    "sleepy":       dict(brow=2, tilt=0, eyes="closed", mouth="small"),
    "delighted":    dict(brow=-5, tilt=0, eyes="wide", mouth="grin", blush=True),
    "calm":         dict(brow=0, tilt=0, eyes="soft", mouth="flat"),
    "focused":      dict(brow=2, tilt=-4, eyes="open", mouth="firm"),
    "stern":        dict(brow=6, tilt=-8, eyes="open", mouth="frown"),
    "approving":    dict(brow=-1, tilt=0, eyes="soft", mouth="smile"),
    "sorrow":       dict(brow=-6, tilt=9, eyes="soft", mouth="frown", tear=True),
    "anger":        dict(brow=8, tilt=-10, eyes="wide", mouth="frown"),
    "release":      dict(brow=-3, tilt=0, eyes="closed", mouth="smile"),
    "yearning":     dict(brow=-5, tilt=5, eyes="soft", mouth="small"),
    "resignation":  dict(brow=2, tilt=3, eyes="soft", mouth="flat"),
    "grief":        dict(brow=-6, tilt=10, eyes="closed", mouth="frown", tear=True),
    "longing":      dict(brow=-5, tilt=4, eyes="soft", mouth="small"),
    "still":        dict(brow=0, tilt=0, eyes="open", mouth="flat"),
    "sly":          dict(brow=3, tilt=-6, eyes="open", mouth="smirk"),
    "curious":      dict(brow=-4, tilt=3, eyes="wide", mouth="small"),
    "alarmed":      dict(brow=-7, tilt=0, eyes="wide", mouth="o"),
    "encouraging":  dict(brow=-2, tilt=0, eyes="open", mouth="smile"),
}

def eyes(cx1, cx2, cy, kind, sk):
    d = C["dark"]
    if kind == "closed":
        return stroke("M%d %d q6 5 12 0" % (cx1-6, cy), d, 2.6) + stroke("M%d %d q6 5 12 0" % (cx2-6, cy), d, 2.6)
    r = 6 if kind == "wide" else (4.5 if kind == "soft" else 5)
    w = circle(cx1, cy, r, C["white"]) + circle(cx1, cy, 2.6, d) + circle(cx2, cy, r, C["white"]) + circle(cx2, cy, 2.6, d)
    if kind == "wide":
        w += circle(cx1-2, cy-2, 1.2, C["white"]) + circle(cx2-2, cy-2, 1.2, C["white"])
    return w

def brows(cx1, cx2, y, tilt, col):
    t = tilt
    return (stroke("M%d %d q7 -3 14 %d" % (cx1-7, y, -t), col, 3.4) +
            stroke("M%d %d q7 %d 14 3" % (cx2-7, y - (-t) - 0 + 0, t), col, 3.4))

def mouth(cx, y, kind):
    d = C["dark"]; r = C["red"]
    if kind == "smile": return stroke("M%d %d q%d 12 %d 0" % (cx-14, y, 14, 28), d, 3)
    if kind == "grin":  return path("M%d %d q%d 16 %d 0 Z" % (cx-16, y, 16, 32), d) + rect(cx-13, y-1, 26, 3, C["white"], rx=1)
    if kind == "frown": return stroke("M%d %d q%d -12 %d 0" % (cx-13, y+8, 13, 26), d, 3)
    if kind == "flat":  return line(cx-11, y+3, cx+11, y+3, d, 3)
    if kind == "firm":  return line(cx-13, y+3, cx+13, y+3, d, 3.6)
    if kind == "o":     return circle(cx, y+3, 6, d) + circle(cx, y+3, 3.5, r)
    if kind == "talk":  return path("M%d %d q%d 10 %d 0 q%d -4 %d 0 Z" % (cx-12, y, 12, 24, -12, -24), r) + rect(cx-11, y-1, 22, 2.5, C["white"], rx=1)
    if kind == "small": return line(cx-6, y+3, cx+6, y+3, d, 3)
    if kind == "pout":  return circle(cx, y+4, 5, r)
    if kind == "smirk": return stroke("M%d %d q10 8 20 -2" % (cx-8, y), d, 3)
    return line(cx-10, y+3, cx+10, y+3, d, 3)

def human(hood, skin, expr, hair=None, ruff=None):
    p = EXPR[expr]; ruff = ruff or C["fur"]
    cx, cy = 120, 120; bw = p.get("brow", 0); tilt = p.get("tilt", 0)
    body = path("M40 300 q0 -92 80 -92 q80 0 80 92 Z", hood)      # shoulders
    body += '<ellipse cx="120" cy="150" rx="78" ry="30" fill="%s"/>' % ruff
    body += circle(cx, cy, 60, ruff)                               # hood fur
    if hair: body = path("M74 116 q46 -42 92 0 q-6 -30 -46 -30 q-40 0 -46 30 Z", hair) + body
    body += circle(cx, cy, 46, skin)                               # face
    body += eyes(103, 137, 118 + max(0, tilt // 3), p["eyes"], skin)
    body += brows(103, 137, 104 + bw, tilt, C["dark"] if hair is None else hair or C["dark"])
    body += mouth(120, 146, p["mouth"])
    if p.get("blush"): body += circle(100, 134, 6, C["rose"], 'opacity="0.4"') + circle(140, 134, 6, C["rose"], 'opacity="0.4"')
    if p.get("tear"): body += path("M110 128 q-3 12 0 20 q3 -8 0 -20 Z", C["blue"], 'opacity="0.8"')
    return body

# --- character base looks + expression lists ---
HUMANS = {
    "me":         dict(hood=C["parkaB"], skin=C["skin"], bg=("#26365e", "#111a30"),
                       exprs=["neutral", "wonder", "fear", "determination", "joy"]),
    "grandmother":dict(hood=C["parkaR"], skin=C["skin2"], hair=C["grey"], bg=("#3a2e5e", "#1a1430"),
                       exprs=["warm", "teaching", "worried", "proud", "tender"]),
    "miki":       dict(hood=C["ember"], skin=C["skin"], bg=("#2e4a58", "#16262e"),
                       exprs=["laughing", "pouting", "scared", "sleepy", "delighted"]),
    "hunter":     dict(hood=C["parkaG"], skin=C["skin2"], bg=("#26405e", "#101c30"),
                       exprs=["calm", "focused", "stern", "approving", "teaching"]),
}
def build_humans():
    for name, spec in HUMANS.items():
        for e in spec["exprs"]:
            svg = frame(spec["bg"][0], spec["bg"][1], human(spec["hood"], spec["skin"], e, spec.get("hair")))
            write("chars/%s/%s.svg" % (name, e), svg)

# --- raven (Tulugak): custom bird face per expression ---
def raven(expr):
    d = "#20263a"; body = ('<ellipse cx="120" cy="205" rx="72" ry="62" fill="%s"/>' % C["dark"] +
        circle(120, 120, 54, C["dark"]))
    # beak
    beak = poly("150,116 202,124 150,136", d)
    # eye state
    if expr in ("alarmed", "curious"):
        eye = circle(106, 110, 9, C["gold"]) + circle(106, 110, 4, C["dark"])
    elif expr == "still":
        eye = circle(106, 112, 7, C["gold"]) + circle(106, 112, 3, C["dark"])
    elif expr == "sly":
        eye = stroke("M98 112 q8 -4 16 0", C["gold"], 4) + circle(108, 112, 3, C["dark"])
    else:  # encouraging
        eye = circle(106, 111, 8, C["gold"]) + circle(106, 111, 3.4, C["dark"])
    # brow feathers by mood
    browf = ""
    if expr == "sly": browf = poly("92,96 128,104 96,108", d)
    if expr == "alarmed": browf = poly("94,90 128,96 98,100", d) + poly("120,88 150,96 122,100", d)
    if expr == "curious": browf = poly("96,92 126,102 100,104", d, 'transform="rotate(-6 110 98)"')
    wings = stroke("M66 150 q-30 30 -4 62", d, 10) + stroke("M174 150 q30 30 4 62", d, 10)
    if expr == "encouraging": wings = stroke("M66 150 q-34 20 -10 40", d, 10) + stroke("M174 150 q34 20 10 40", d, 10)
    head_tilt = ""
    return raven_frame(browf + body + beak + eye + wings)
def raven_frame(inner):
    return frame("#1a2036", "#0a0e1c", inner)
def build_raven():
    for e in ["sly", "curious", "alarmed", "encouraging", "still"]:
        write("chars/raven/%s.svg" % e, raven(e))

# --- celestial + sea (custom colour bases) ---
def seamother(expr):
    p = EXPR[expr]
    hairflow = path("M64 108 q56 -54 112 0 q-8 70 -56 82 q-48 -12 -56 -82 Z", C["blue"])
    tang = path("M120 120 q64 44 42 168 l-84 0 q-22 -128 42 -168 Z", C["ice"], 'opacity="0.65"')
    face = circle(120, 122, 44, C["ice"])
    ey = eyes(105, 135, 120, p["eyes"], C["ice"])
    br = brows(105, 135, 106 + p["brow"], p["tilt"], C["steel"])
    mo = mouth(120, 148, p["mouth"])
    tear = path("M110 130 q-3 14 0 24 q3 -10 0 -24 Z", C["blue"], 'opacity="0.8"') if p.get("tear") else ""
    strands = "".join(path("M%d 96 q-6 60 4 96" % x, C["steel"], 'opacity="0.4"') for x in (86, 104, 136, 154))
    return frame("#123a4e", "#06202c", tang + strands + hairflow + face + ey + br + mo + tear)
def build_seamother():
    for e in ["sorrow", "anger", "calm", "release"]:
        write("chars/seamother/%s.svg" % e, seamother(e))

def celestial(kind, expr):
    p = EXPR[expr]
    if kind == "moon":
        disc = circle(120, 120, 60, C["fur"]) + circle(104, 104, 6, C["grey"], 'opacity="0.5"') + circle(96, 132, 4, C["grey"], 'opacity="0.5"')
        skin = C["fur"]; bg = ("#20264a", "#0c1024"); halo = circle(120, 120, 74, C["blue"], 'opacity="0.18"')
        brc = C["steel"]
    else:  # sun
        rays = "".join(line(120, 120, 120 + 92 * math.cos(a), 120 + 92 * math.sin(a), C["amber"], 6) for a in [i * math.pi / 6 for i in range(12)])
        disc = rays + circle(120, 120, 58, C["gold"])
        skin = C["gold"]; bg = ("#3a2a12", "#180f06"); halo = circle(120, 120, 78, C["amber"], 'opacity="0.2"')
        brc = C["ember"]
    face = circle(120, 120, 40, skin)
    ey = eyes(106, 134, 118, p["eyes"], skin)
    br = brows(106, 134, 104 + p["brow"], p["tilt"], brc)
    mo = mouth(120, 144, p["mouth"])
    tear = path("M112 126 q-3 12 0 20 q3 -8 0 -20 Z", C["blue"], 'opacity="0.8"') if p.get("tear") else ""
    hands = ""
    if kind == "sun" and expr in ("grief", "longing"):  # covering / turned
        hands = path("M78 150 q42 -20 84 0 q-10 22 -42 22 q-32 0 -42 -22 Z", C["gold"], 'opacity="0.85"')
    return frame(bg[0], bg[1], halo + disc + face + ey + br + mo + tear + hands)
def build_celestial():
    for e in ["yearning", "resignation"]:
        write("chars/moon/%s.svg" % e, celestial("moon", e))
    for e in ["grief", "longing", "warmth" if False else "warm"]:
        write("chars/sun/%s.svg" % e, celestial("sun", e))

# ===========================================================================
# BACKGROUNDS
# ===========================================================================
def bgf(defs, body):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 675" '
            'preserveAspectRatio="xMidYMid slice" role="img"><defs>%s</defs>%s</svg>' % (defs, body))
def lin(id, stops, x1=0, y1=0, x2=0, y2=1):
    s = "".join('<stop offset="%s" stop-color="%s"/>' % (o, c) for o, c in stops)
    return '<linearGradient id="%s" x1="%s" y1="%s" x2="%s" y2="%s">%s</linearGradient>' % (id, x1, y1, x2, y2, s)
def stars(n, w=1200, h=400, seed=1):
    return "".join(circle((i * 137 * seed) % w, (i * 89 * seed) % h, (i % 3) * 0.6 + 0.6, C["white"], 'opacity="0.8"') for i in range(n))
def aurora(op=0.3):
    return (path("M-40 200 q300 -120 640 20 q300 130 640 -30 l0 120 q-340 150 -640 20 q-340 -130 -640 -10 Z", C["green"], 'opacity="%s"' % op) +
            path("M-40 260 q300 -100 640 40 q300 120 640 -10 l0 80 q-340 120 -640 0 q-340 -120 -640 -20 Z", C["violet"], 'opacity="%s"' % (op * 0.8)))

def build_bg():
    # snow-house interior, warm lamp (reuse look but with warmer light)
    def snowhouse(warm, spring=False):
        lamp = '<radialGradient id="lamp" cx="50%%" cy="70%%" r="60%%"><stop offset="0" stop-color="%s"/><stop offset="0.5" stop-color="#c98a44" stop-opacity="0.5"/><stop offset="1" stop-color="#0c1330" stop-opacity="0"/></radialGradient>' % (warm)
        sky = "#20305a" if not spring else "#3a5a86"
        body = (rect(0, 0, 1200, 675, "url(#sk)") + path("M120 675 q480 -560 960 0 Z", "#22305a" if not spring else "#3a5a7a") +
            "".join('<path d="M%s 675 q%s -%s %s -%s" stroke="#33436e" stroke-width="2.5" fill="none" opacity="0.6"/>' % (150+i*95, (600-(150+i*95))*0.2, 300+i*8, (600-(150+i*95))*0.5, 300+i*8) for i in range(10)) +
            "".join(line(140, y, 1060, y, "#2a3a66", 2, 'opacity="0.4"') for y in (300, 380, 460)) +
            rect(0, 0, 1200, 675, "url(#lamp)") +
            '<ellipse cx="600" cy="560" rx="120" ry="30" fill="#2a2030"/>' +
            path("M500 560 q100 -40 200 0 q-8 26 -100 26 q-92 0 -100 -26 Z", "#4a3a2a") +
            "".join(path("M%s 556 q6 -30 12 0 Z" % (520+i*30), C["amber"]) for i in range(6)) +
            '<ellipse cx="600" cy="556" rx="90" ry="12" fill="%s" opacity="0.85"/>' % warm)
        if spring: body += "".join(circle(x, 120 + (x % 60), 3, C["gold"], 'opacity="0.5"') for x in range(100, 1150, 130))
        return bgf(lin("sk", [("0", sky), ("1", "#0c1330")]) + lamp, body)
    write("bg/snowhouse_interior_lamplight.svg", snowhouse("#ffcf7a"))
    write("bg/snowhouse_closeup_grandmother.svg", snowhouse("#ffd98f"))
    write("bg/snowhouse_sunrise_spring.svg", snowhouse("#ffe6b0", spring=True))
    # entrance dark
    write("bg/snowhouse_entrance_dark.svg", bgf(lin("e", [("0", "#0e1530"), ("1", "#05080f")]),
        rect(0, 0, 1200, 675, "url(#e)") + path("M0 675 q600 -120 1200 0 Z", "#12203f") +
        path("M420 675 q180 -320 360 0 Z", "#060a14") +          # dark doorway
        '<ellipse cx="600" cy="560" rx="200" ry="40" fill="#0a1020"/>' + stars(40, 1200, 300, 2)))
    # dog line at night
    write("bg/dogline_snow_night.svg", bgf(lin("d", [("0", "#0e1a3a"), ("1", "#14284a")]),
        rect(0, 0, 1200, 675, "url(#d)") + stars(50, 1200, 300, 3) + aurora(0.18) +
        path("M0 470 q600 -40 1200 0 l0 205 l-1200 0 Z", "#dfe9f6") +
        path("M0 520 q600 30 1200 0 l0 155 l-1200 0 Z", "#c7d6ea") +
        "".join(path("M%d 500 q18 -26 36 0 q-4 14 -18 14 q-14 0 -18 -14 Z" % x, "#5a4a3a") for x in range(120, 1120, 180))))  # curled dog shapes
    # tundra with stars, wide
    write("bg/tundra_stars_wide.svg", bgf(lin("t", [("0", "#0a0e26"), ("0.7", "#12204a"), ("1", "#0c1730")]),
        rect(0, 0, 1200, 675, "url(#t)") + stars(90, 1200, 380, 1) + aurora(0.22) +
        path("M0 540 q300 -60 600 -10 q300 50 600 -20 l0 165 l-1200 0 Z", "#0e1730") +
        path("M0 600 q300 -30 600 0 q300 30 600 -10 l0 85 l-1200 0 Z", "#0a1226")))
    write("bg/tundra_dawnless_calm.svg", bgf(lin("tc", [("0", "#122a4e"), ("1", "#0c1a34")]),
        rect(0, 0, 1200, 675, "url(#tc)") + stars(50, 1200, 300, 4) +
        path("M0 500 q600 -50 1200 0 l0 175 l-1200 0 Z", "#12203f") +
        path("M0 560 q600 30 1200 0 l0 115 l-1200 0 Z", "#0e1a34")))
    # frozen lake vision
    write("bg/frozen_lake_vision.svg", bgf(lin("fl", [("0", "#16324e"), ("1", "#0c1c30")]) +
        '<radialGradient id="win" cx="50%" cy="60%" r="45%"><stop offset="0" stop-color="#8fe3d6" stop-opacity="0.5"/><stop offset="1" stop-color="#0c1c30" stop-opacity="0"/></radialGradient>',
        rect(0, 0, 1200, 675, "url(#fl)") + stars(40, 1200, 260, 5) +
        rect(0, 380, 1200, 295, "#2a4a5e") + rect(0, 380, 1200, 295, "url(#win)") +
        "".join(line(120 + i * 130, 400, 200 + i * 130, 560, C["ice"], 2, 'opacity="0.4"') for i in range(9))))
    # ice ridge with bear silhouette hint
    write("bg/ice_ridge_bear.svg", bgf(lin("ir", [("0", "#1a3350"), ("1", "#0e2036")]),
        rect(0, 0, 1200, 675, "url(#ir)") + stars(40, 1200, 240, 6) +
        path("M0 420 L280 300 L520 440 L760 320 L1040 460 L1200 380 L1200 675 L0 675 Z", "#26456a") +
        path("M0 520 q600 -30 1200 20 l0 135 l-1200 0 Z", "#dfe9f6", 'opacity="0.9"')))
    # sea edge, black water
    write("bg/ice_edge_black_water.svg", bgf(lin("se", [("0", "#5b6f92"), ("1", "#243b52")]) + lin("wat", [("0", "#173042"), ("1", "#050c14")]),
        rect(0, 0, 1200, 320, "url(#se)") + circle(980, 120, 54, "#e9d9b0", 'opacity="0.6"') +
        rect(0, 300, 1200, 375, "url(#wat)") +
        path("M0 300 q300 -20 600 0 t600 0 l0 40 l-1200 0 Z", "#eef4ff", 'opacity="0.85"') +   # ice shelf edge
        "".join(path("M0 %d q300 -12 600 0 t600 0" % y, "none", 'stroke="#274a60" stroke-width="2" opacity="0.4"') for y in (360, 430, 520))))
    # descending green dark
    write("bg/descending_green_dark.svg", bgf('<radialGradient id="dg" cx="50%" cy="18%" r="90%"><stop offset="0" stop-color="#2f7f74"/><stop offset="0.5" stop-color="#123f42"/><stop offset="1" stop-color="#04141c"/></radialGradient>',
        rect(0, 0, 1200, 675, "url(#dg)") +
        "".join(circle((i * 173) % 1200, (i * 97) % 675, (i % 4) + 1, C["ice"], 'opacity="0.15"') for i in range(60)) +
        "".join(path("M%d 0 q20 340 0 675" % x, "none", 'stroke="#1f6f66" stroke-width="2" opacity="0.12"') for x in range(80, 1200, 160))))
    # undersea sea-mother hall
    def undersea(close=False):
        return bgf('<radialGradient id="uh" cx="50%%" cy="40%%" r="80%%"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="#03121a"/></radialGradient>' % ("#1a5a5e" if close else "#134a4e"),
            rect(0, 0, 1200, 675, "url(#uh)") +
            "".join(circle((i * 151) % 1200, (i * 83) % 675, (i % 3) + 1.5, C["ice"], 'opacity="0.18"') for i in range(50)) +
            path("M0 620 q300 -40 600 0 t600 0 l0 55 l-1200 0 Z", "#0a2a30") +
            "".join(path("M%d 675 q-20 -120 0 -240" % x, "none", 'stroke="#2f7f74" stroke-width="4" opacity="0.25"') for x in range(120, 1120, 150)))
    write("bg/undersea_seamother_hall.svg", undersea(False))
    write("bg/undersea_seamother_close.svg", undersea(True))
    # sky road of stars
    write("bg/sky_road_stars.svg", bgf(lin("sr", [("0", "#0a0e2a"), ("1", "#141d44")]),
        rect(0, 0, 1200, 675, "url(#sr)") + stars(130, 1200, 675, 7) + aurora(0.26) +
        path("M400 675 L520 200 L680 200 L800 675 Z", C["ice"], 'opacity="0.18"') +          # light road
        "".join(circle(600 + ((i%2)*2-1)*(i*3), 640 - i*30, 3, C["gold"], 'opacity="0.8"') for i in range(15))))
    # sky moon pale
    write("bg/sky_moon_pale.svg", bgf(lin("sm", [("0", "#10163a"), ("1", "#1c2650")]),
        rect(0, 0, 1200, 675, "url(#sm)") + stars(90, 1200, 675, 8) +
        circle(860, 220, 120, C["fur"], 'opacity="0.9"') + circle(820, 190, 16, C["grey"], 'opacity="0.4"') + circle(900, 260, 12, C["grey"], 'opacity="0.4"') +
        circle(860, 220, 150, C["blue"], 'opacity="0.10"')))
    # sky sun hidden
    write("bg/sky_sun_hidden.svg", bgf(lin("ss", [("0", "#141232"), ("0.7", "#3a2a3e"), ("1", "#5a3a2e")]),
        rect(0, 0, 1200, 675, "url(#ss)") + stars(50, 1200, 300, 9) +
        circle(600, 380, 150, C["ember"], 'opacity="0.25"') +
        path("M450 380 q150 -80 300 0 q-30 60 -150 60 q-120 0 -150 -60 Z", C["gold"], 'opacity="0.5"')))   # hidden behind hands
    # sky dawn edge (climax)
    write("bg/sky_dawn_edge.svg", bgf(lin("sd", [("0", "#101a3e"), ("0.55", "#5a4a6a"), ("0.8", "#e08a5a"), ("1", "#ffcf7a")]),
        rect(0, 0, 1200, 675, "url(#sd)") + stars(40, 1200, 220, 10) +
        circle(600, 600, 180, C["gold"], 'opacity="0.7"') +
        "".join(line(600, 600, 600 + 300 * math.cos(a), 600 + 300 * math.sin(a), C["amber"], 5, 'opacity="0.3"') for a in [-math.pi/2 + (i-4)*0.28 for i in range(9)])))

# ---------------------------------------------------------------------------
# ENEMY SPRITE STAGES (portraits that change with the battle's "damage" state)
# ---------------------------------------------------------------------------
def bear_stage(stage):
    # stages: aggro (reared), wary, calm (turning away)
    face_y = {"aggro": 96, "wary": 110, "calm": 122}[stage]
    body = '<ellipse cx="120" cy="230" rx="86" ry="66" fill="%s"/>' % C["fur"]
    head = circle(120, face_y, 56, C["fur"]) + circle(88, face_y-34, 16, C["fur"]) + circle(152, face_y-34, 16, C["fur"])
    if stage == "aggro":
        eyes_ = circle(102, face_y-6, 6, C["red"]) + circle(138, face_y-6, 6, C["red"])
        mouth_ = path("M96 %d q24 20 48 0 l0 8 q-24 18 -48 0 Z" % (face_y+14), C["night"]) + "".join(poly("%d,%d %d,%d %d,%d" % (100+i*9, face_y+22, 96+i*9, face_y+14, 104+i*9, face_y+14), C["white"]) for i in range(6))
    elif stage == "wary":
        eyes_ = circle(102, face_y-4, 6, C["gold"]) + circle(138, face_y-4, 6, C["gold"]) + circle(102, face_y-4, 3, C["dark"]) + circle(138, face_y-4, 3, C["dark"])
        mouth_ = stroke("M100 %d q20 8 40 0" % (face_y+16), C["dark"], 4)
    else:  # calm — turned, softer
        eyes_ = stroke("M96 %d q8 5 16 0" % (face_y-4), C["dark"], 3) + stroke("M128 %d q8 5 16 0" % (face_y-4), C["dark"], 3)
        mouth_ = stroke("M104 %d q16 6 32 0" % (face_y+16), C["dark"], 3)
    nose = circle(120, face_y+8, 6, C["dark"])
    return frame("#3a4a66", "#16202e", body + head + nose + eyes_ + mouth_)

def dog_stage(stage):
    if stage == "asleep":
        return frame("#14243e", "#0a1424",
            path("M50 240 q70 -30 140 0 q-6 30 -70 30 q-64 0 -70 -30 Z", C["brown"]) +      # curled body
            circle(120, 230, 34, C["brown"]) + stroke("M96 226 q10 6 20 0", C["dark"], 3) +  # closed eye
            '<text x="150" y="180" font-size="30" fill="#8fe3d6" font-family="sans-serif" opacity="0.7">z</text>')
    if stage == "rising":
        return frame("#16284a", "#0a1626",
            '<ellipse cx="120" cy="240" rx="70" ry="40" fill="%s"/>' % C["brown"] +
            circle(120, 160, 40, C["brown"]) + poly("92,120 100,150 116,140", C["brown"]) + poly("148,120 140,150 124,140", C["brown"]) +
            circle(108, 158, 4, C["dark"]) + circle(132, 158, 4, C["dark"]) + circle(120, 172, 5, C["dark"]))
    # standing / ready
    return frame("#1a2e50", "#0c1a2e",
        '<ellipse cx="120" cy="210" rx="66" ry="42" fill="%s"/>' % C["brown"] +
        circle(120, 140, 42, C["brown"]) + poly("90,96 100,130 118,120", C["brown"]) + poly("150,96 140,130 122,120", C["brown"]) +
        circle(108, 138, 5, C["gold"]) + circle(132, 138, 5, C["gold"]) + circle(108, 138, 2, C["dark"]) + circle(132, 138, 2, C["dark"]) +
        circle(120, 156, 6, C["dark"]) + stroke("M172 190 q26 -14 20 14", C["brown"], 8))  # wagging tail

def build_enemies():
    for s in ("aggro", "wary", "calm"):
        write("chars/bear/%s.svg" % s, bear_stage(s))
    for s in ("asleep", "rising", "standing"):
        write("chars/dogteam/%s.svg" % s, dog_stage(s))

if __name__ == "__main__":
    build_humans(); build_raven(); build_seamother(); build_celestial(); build_enemies(); build_bg()
    nchar = sum(len(files) for _, _, files in os.walk(os.path.join(ROOT, "chars")))
    print("story assets written.")
    for d in sorted(os.listdir(os.path.join(ROOT, "chars"))):
        p = os.path.join(ROOT, "chars", d)
        if os.path.isdir(p): print("  chars/%s: %s" % (d, sorted(x[:-4] for x in os.listdir(p))))
    print("  backgrounds: %d" % len([f for f in os.listdir(os.path.join(ROOT, "bg"))]))
