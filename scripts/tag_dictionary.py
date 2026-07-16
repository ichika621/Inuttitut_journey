# -*- coding: utf-8 -*-
"""
Step 2 — assign a THEME and a DIFFICULTY tier (1-4) to every dictionary
record, by keyword-matching the English gloss. The PDF is alphabetical with
no categories, so this is auto-tagging.

Themes: greetings, family, body, animals, food, clothing, weather,
        land_nature, hunting_tools, actions, misc
Difficulty:
  1  short high-frequency single words  (greetings, family, numbers, body)
  2  concrete nouns                     (animals, food, clothing)
  3  nature, tools, hunting, actions
  4  phrases / multi-word entries       (sentence-like glosses or multi-word forms)
"""
import io, re, json, sys

INP = sys.argv[1] if len(sys.argv) > 1 else "data/dictionary.json"
OUT = sys.argv[2] if len(sys.argv) > 2 else "data/dictionary.json"

# Ordered themes: first matching keyword-set wins. Order matters where a gloss
# could match two themes (e.g. "seal meat" -> food beats animals? we put food
# after animals so "seal" wins animals; "meat" alone -> food).
THEME_KEYWORDS = [
    ("greetings", [
        r"\bhello\b", r"\bwelcome\b", r"\bthank", r"\bgoodbye\b", r"\bgood ?bye\b",
        r"\bgreeting", r"\bplease\b", r"\bsorry\b", r"\bfarewell\b",
        r"\byes\b", r"\bno\b", r"\bgood morning\b", r"\bgood night\b",
    ]),
    ("family", [
        r"\bmother\b", r"\bfather\b", r"\bson\b", r"\bdaughter\b", r"\bbrother\b",
        r"\bsister\b", r"\baunt\b", r"\buncle\b", r"\bgrandmother\b",
        r"\bgrandfather\b", r"\bgrandchild", r"\bgrandparent", r"\bchild\b",
        r"\bchildren\b", r"\bbaby\b", r"\bwife\b", r"\bhusband\b", r"\bfamily\b",
        r"\bcousin\b", r"\bparent", r"\bin-?law\b", r"\bnephew\b", r"\bniece\b",
        r"\btwin\b", r"\borphan\b", r"\bwidow", r"\brelative", r"\bboy\b",
        r"\bgirl\b", r"\bfriend\b",
    ]),
    ("body", [
        r"\bhead\b", r"\beye\b", r"\bear\b", r"\bnose\b", r"\bmouth\b", r"\bhand\b",
        r"\bfoot\b", r"\bfeet\b", r"\barm\b", r"\bleg\b", r"\bfinger", r"\bhair\b",
        r"\btooth\b", r"\bteeth\b", r"\bface\b", r"\bheart\b", r"\bblood\b",
        r"\bbone\b", r"\bbelly\b", r"\bknee\b", r"\bneck\b", r"\btongue\b",
        r"\bthroat\b", r"\bnail\b", r"\belbow\b", r"\bshoulder\b", r"\bchin\b",
        r"\blip\b", r"\bcheek\b", r"\bforehead\b", r"\bstomach\b", r"\bliver\b",
        r"\blung\b", r"\bthumb\b", r"\btoe\b", r"\bwrist\b", r"\bankle\b",
        r"\bskull\b", r"\bbrain\b", r"\bribs?\b", r"\bnostril", r"\bbeard\b",
        r"\bhip\b", r"\bthigh\b", r"\bpalm\b", r"\bbody\b",
    ]),
    ("animals", [
        r"\bseal\b", r"\bdog\b", r"\bhusky\b", r"\bwhale\b", r"\bbear\b", r"\bfox\b",
        r"\bwolf\b", r"\bwolverine\b", r"\bcaribou\b", r"\bbird\b", r"\bfish\b",
        r"\bduck\b", r"\bgoose\b", r"\bgeese\b", r"\bgull\b", r"\bhare\b",
        r"\brabbit\b", r"\blemming\b", r"\bowl\b", r"\braven\b", r"\bsalmon\b",
        r"\bcod\b", r"\btrout\b", r"\bchar\b", r"\banimal", r"\bwalrus\b",
        r"\bptarmigan\b", r"\bloon\b", r"\beagle\b", r"\bhawk\b", r"\bmouse\b",
        r"\bshrew\b", r"\bweasel\b", r"\botter\b", r"\bsquirrel\b", r"\binsect\b",
        r"\bmosquito\b", r"\bbeetle\b", r"\bworm\b", r"\bspider\b", r"\bdeer\b",
        r"\bmoose\b", r"\bcat\b", r"\bhorse\b", r"\bcow\b", r"\bsheep\b", r"\bpig\b",
        r"\bpuppy\b", r"\bpup\b", r"\bbeluga\b", r"\bnarwhal\b", r"\bfawn\b",
        r"\bmink\b", r"\bfrog\b", r"\bfly\b", r"\bbee\b", r"\btail\b", r"\bfur\b",
        r"\bfeather", r"\bwing\b", r"\bpelt\b", r"\bcurlew\b", r"\bpuffin\b",
        r"\bmurre\b", r"\bteal\b", r"\bgannet\b", r"\bkittiwake\b",
    ]),
    ("food", [
        r"\beat\b", r"\bfood\b", r"\bmeat\b", r"\bfat\b", r"\bberry\b", r"\bberries\b",
        r"\begg\b", r"\bsoup\b", r"\bbread\b", r"\btea\b", r"\bsugar\b", r"\bdrink\b",
        r"\bbroth\b", r"\bblubber\b", r"\bcook", r"\bboil", r"\braw\b", r"\bmeal\b",
        r"\bhungry\b", r"\bmilk\b", r"\bfeast\b", r"\bsupper\b", r"\bdinner\b",
        r"\bbreakfast\b", r"\bbake", r"\bfry\b", r"\bfried\b", r"\bkettle\b",
        r"\bflour\b", r"\bmarrow\b",
    ]),
    ("clothing", [
        r"\bboot\b", r"\bmitt", r"\bcoat\b", r"\bparka\b", r"\bpants\b", r"\bhat\b",
        r"\bdress\b", r"\bcloth", r"\bsock\b", r"\bglove\b", r"\bkamik\b",
        r"\bapron\b", r"\bhood\b", r"\bgarment\b", r"\bshirt\b", r"\bsleeve\b",
        r"\bcollar\b", r"\bbutton\b", r"\bzipper\b", r"\bsnowsuit\b", r"\bslipper\b",
        r"\bmoccasin\b", r"\bsealskin\b", r"\bskin clothing\b", r"\bdickie\b",
        r"\bscarf\b", r"\bbelt\b",
    ]),
    ("weather", [
        r"\bsnow", r"\bwind\b", r"\brain\b", r"\bstorm\b", r"\bcold\b", r"\bwarm\b",
        r"\bice\b", r"\bfog\b", r"\bcloud\b", r"\bweather\b", r"\bfrost\b",
        r"\bblizzard\b", r"\bfreez", r"\bthaw\b", r"\bbreeze\b", r"\bgust\b",
        r"\bsleet\b", r"\bslush\b", r"\bicicle\b", r"\bmelt\b", r"\bdrift\b",
    ]),
    ("land_nature", [
        r"\bland\b", r"\bsea\b", r"\bocean\b", r"\bmountain\b", r"\briver\b",
        r"\blake\b", r"\bisland\b", r"\brock\b", r"\bhill\b", r"\bwater\b",
        r"\bstar\b", r"\bmoon\b", r"\bsun\b", r"\btree\b", r"\bplant\b",
        r"\bflower\b", r"\bgrass\b", r"\bmoss\b", r"\bshore\b", r"\bbeach\b",
        r"\bvalley\b", r"\bcliff\b", r"\bbay\b", r"\btundra\b", r"\bground\b",
        r"\bearth\b", r"\bworld\b", r"\bwave\b", r"\btide\b", r"\bnorth\b",
        r"\bsouth\b", r"\beast\b", r"\bwest\b", r"\bsky\b", r"\bglacier\b",
        r"\bfjord\b", r"\bpond\b", r"\bwaterfall\b", r"\bboulder\b", r"\binlet\b",
        r"\bcape\b", r"\bcove\b", r"\bnorthern lights\b", r"\baurora\b",
    ]),
    ("hunting_tools", [
        r"\bhunt", r"\bharpoon\b", r"\bknife\b", r"\bspear\b", r"\bnet\b",
        r"\btrap\b", r"\bgun\b", r"\bhook\b", r"\bkayak\b", r"\bkajak\b",
        r"\bboat\b", r"\bsled\b", r"\bsledge\b", r"\bkomatik\b", r"\bkamutik\b",
        r"\btool\b", r"\bneedle\b", r"\baxe\b", r"\bpaddle\b", r"\brifle\b",
        r"\bbullet\b", r"\barrow\b", r"\bbow\b", r"\bsnare\b", r"\bfishing\b",
        r"\bdrum\b", r"\bhammer\b", r"\bnail\b", r"\brope\b", r"\bline\b",
        r"\bfloat\b", r"\bulu\b", r"\bblade\b", r"\bcanoe\b", r"\bpaddle\b",
        r"\bshovel\b", r"\bscraper\b", r"\bfishhook\b",
    ]),
]

# Native number words (English glosses) — treated as tier-1 greetings-ish core.
NUMBER_RE = re.compile(
    r"^(one|two|three|four|five|six|seven|eight|nine|ten|"
    r"eleven|twelve|number|count|first|second|third)\b", re.I)

def strip_sci(gloss):
    """Remove parenthetical scientific names / notes to judge word-count."""
    return re.sub(r"\([^)]*\)", "", gloss)

def classify_theme(gloss):
    g = gloss.lower()
    for theme, pats in THEME_KEYWORDS:
        for p in pats:
            if re.search(p, g):
                return theme
    return "misc"

def is_phrase(rec):
    """Sentence-like / multi-word entry -> tier 4 candidate."""
    core = strip_sci(rec["english"]).strip()
    words = [w for w in re.split(r"\s+", core) if w]
    if len(words) >= 5:
        return True
    # multi-word Inuttut form (a constructed phrase, e.g. 'Nunatsuillo imak suillo')
    if any(" " in f for f in rec["inuttut"]):
        return True
    # gloss that reads as a full sentence (contains a verb-y clause) — heuristic:
    if re.search(r"\b(he|she|it|they|someone|something|you|to)\b", core.lower()) \
       and len(words) >= 3:
        return True
    return False

def difficulty(rec, theme):
    if is_phrase(rec):
        return 4
    if NUMBER_RE.search(rec["english"]):
        return 1
    if theme in ("greetings", "family", "body"):
        return 1
    if theme in ("animals", "food", "clothing"):
        return 2
    if theme in ("weather", "land_nature", "hunting_tools", "actions"):
        return 3
    # misc
    core = strip_sci(rec["english"]).strip()
    nwords = len([w for w in re.split(r"\s+", core) if w])
    if rec.get("pos") == "v.":
        return 3           # verbs -> actions-ish
    return 2 if nwords <= 2 else 3

# --- Image asset layer -----------------------------------------------------
# Every record gets an `image` path so the picture-based UI has a swappable
# asset per word. Words with hand-drawn icons map to a specific slug; all others
# point at a shared placeholder icon. Art is original flat-SVG (see make_assets).
PLACEHOLDER = "assets/words/_placeholder.svg"
IMAGE_SLUGS = {
    # family
    "Mother": "mother", "Father": "father", "Grandfather": "grandfather",
    "Child": "child", "Woman": "woman", "Man": "man", "Boy": "boy",
    "Girl": "girl", "Friend": "friend", "Baby": "baby",
    "Girl's older sister": "sister", "Brother of a girl": "brother",
    # body
    "Eye": "eye", "Head": "head", "Mouth": "mouth", "Nose": "nose",
    "Ear": "ear", "Arm": "arm", "Cheek": "cheek", "Chin": "chin",
    "Beard": "beard", "Blood": "blood",
    # animals
    "Inuit dog": "dog", "Caribou (Rangifer tarandus)": "caribou",
    "Seal, animal that lifts it head out of the water": "seal",
    "Polar bear (Ursus maritimus)": "bear", "Loon (Gavia immer)": "loon",
    "Fish": "fish",
    # food
    "Eat": "eat", "Dried meat": "meat", "Blubber": "blubber",
    "Egg": "egg", "Berry": "berry",
    # clothing
    "Boot": "boot", "Coat": "coat", "Mitt": "mitt", "Clothing": "clothing",
    "Hood": "hood",
    # weather / land / nature
    "Snow": "snow", "Wind": "wind", "Cold": "cold", "Storm": "storm",
    "Cloud": "cloud", "Fog": "fog", "Sea": "sea", "Water": "water",
    "Shore": "shore", "Rock": "rock", "Beach": "beach",
    "Sun": "sun", "Moon": "moon", "Star": "star", "Night": "night",
    "Fire": "fire",
    # hunting & tools
    "Knife": "knife", "Fish or seal net": "net", "Spear": "spear",
    "Hook": "hook", "Boat": "boat",
    # actions
    "See": "see", "Come": "come", "Sleep": "sleep", "Run": "run",
    "Walk": "walk", "Sing": "sing", "Dance": "dance", "Whip": "whip",
    "Strong": "strong",
    # greetings
    "Yes": "yes", "No": "no", "Thank you": "thanks", "Sorry": "sorry",
    # nouns added for the nouns-only revision
    "Snow house (igloo)": "snowhouse", "Sled": "sled", "Grandchild": "grandchild",
    "Crow (Common raven, Corvus corax)": "raven", "Spring": "spring",
    "Spear, lance for hunting": "spear", "Rock": "rock", "Cloud": "cloud",
    "Head": "head", "Nose": "nose", "Egg": "egg",
    "Caribou (Rangifer tarandus)": "caribou",
}

def image_for(rec):
    slug = IMAGE_SLUGS.get(rec["english"])
    return "assets/words/%s.svg" % slug if slug else PLACEHOLDER

def main():
    data = json.load(io.open(INP, encoding="utf-8"))
    from collections import Counter
    tc, dc = Counter(), Counter()
    nimg = 0
    for rec in data:
        theme = classify_theme(rec["english"])
        # verbs with no strong noun theme -> actions
        if theme == "misc" and rec.get("pos") == "v.":
            theme = "actions"
        rec["theme"] = theme
        rec["difficulty"] = difficulty(rec, theme)
        rec["image"] = image_for(rec)
        if rec["image"] != PLACEHOLDER:
            nimg += 1
        tc[theme] += 1
        dc[rec["difficulty"]] += 1
    io.open(OUT, "w", encoding="utf-8").write(
        json.dumps(data, ensure_ascii=False, indent=1))
    print("themes:", dict(tc.most_common()))
    print("difficulty:", dict(sorted(dc.items())))
    print("records with a specific icon:", nimg)

if __name__ == "__main__":
    main()
