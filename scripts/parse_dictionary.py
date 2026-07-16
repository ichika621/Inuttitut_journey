# -*- coding: utf-8 -*-
"""
Parse the Labrador Virtual Museum "English-Inuttut Dictionary" PDF into
structured JSON. Vocabulary source is ONLY this PDF.

Entry grammar observed in the source:
    English gloss [separator] [pos] InuttutForm[; | .]
  where:
    - separator is an em dash (U+2014) or en dash (U+2013), OR the pos marker
      itself, OR (rare) nothing (form sits alone on its own line after a
      multi-line English gloss).
    - pos marker is "v." (verb) or "n." (noun), appearing before the form.
    - additional Inuttut forms for the same entry appear on following lines,
      each starting with a dash or a pos marker (no English) -> variants array.
    - a trailing "?" on a form = compiler was unsure -> uncertain: true.
Orthography is preserved EXACTLY (case-sensitive, incl. mid-word capital K
representing a uvular consonant, and circumflex vowels a e i o u).
"""
import io, re, json, sys

SRC = sys.argv[1] if len(sys.argv) > 1 else "scratch/raw_full.txt"
OUT = sys.argv[2] if len(sys.argv) > 2 else "data/dictionary.json"

EMDASH = "—"
ENDASH = "–"
DASHES = (EMDASH, ENDASH)

def is_junk(raw):
    t = raw.replace("\xa0", " ").strip()
    if not t:
        return True
    if t.startswith("==== PAGE"):
        return True
    if t.startswith("www.labradorvirtualmuseum"):
        return True
    if t == "English-Inuttut Dictionary":
        return True
    if re.match(r"^\d+/191$", t):
        return True
    if re.match(r"^20\d\d/\d\d/\d\d", t):          # date stamp
        return True
    if re.match(r"^[A-Za-z]\s*[-‑–—]\s*[A-Za-z]$", t):  # A - a divider
        return True
    if t.startswith("Total number of entries"):
        return True
    return False

def norm(raw):
    return raw.replace("\xa0", " ").strip()

def is_continuation_form(s):
    """Line that is an additional form for the previous entry (no English)."""
    return s[:1] in DASHES or bool(re.match(r"^(v\.|n\.)\s", s))

def line_has_form(s):
    """Does this line contain / complete an Inuttut form?"""
    if any(d in s for d in DASHES):
        return True
    if re.search(r"(?:^|\s)(v\.|n\.)\s+[^\s]", s):
        return True
    # standalone single-token form line completing a wrapped English gloss
    if re.match(r"^[A-Za-zÂÊÎÔÛâêîôû'’]+\s*\??\s*[.;]?$", s) \
       and " " not in s.strip().rstrip(".;? "):
        return True
    return False

def clean_form(tok):
    """Strip trailing punctuation, detect uncertainty."""
    tok = tok.strip()
    uncertain = False
    # trailing ? (optionally spaced) marks uncertainty
    m = re.search(r"\?\s*[.;]?\s*$", tok)
    if m:
        uncertain = True
    tok = re.sub(r"[.;]?\s*$", "", tok)      # drop trailing . or ;
    tok = tok.replace("?", "").strip()
    return tok, uncertain

def split_forms(rest):
    """rest is the post-separator text; may hold 'form1; form2' but usually one."""
    parts = [p for p in rest.split(";")]
    forms = []
    unc = False
    for p in parts:
        p = p.strip()
        if not p:
            continue
        f, u = clean_form(p)
        if f:
            forms.append(f)
            unc = unc or u
    return forms, unc

POS_RE = re.compile(r"(?:^|\s)(v\.|n\.)\s+")

def parse_entry(text):
    """Return dict(english, pos, forms[list], uncertain) or None."""
    text = text.strip()
    pos = None
    # locate first dash separator
    didx = min([text.find(d) for d in DASHES if d in text] or [-1])
    if didx >= 0:
        english = text[:didx].strip()
        rest = text[didx + 1:].strip()
        m = re.match(r"^(v\.|n\.)\s+(.*)$", rest)
        if m:
            pos = "v." if m.group(1) == "v." else "n."
            rest = m.group(2).strip()
        forms, unc = split_forms(rest)
    else:
        m = POS_RE.search(text)
        if m:
            pos = m.group(1)
            english = text[:m.start(1)].strip()
            rest = text[m.end():].strip()
            forms, unc = split_forms(rest)
        else:
            # standalone: last whitespace token is the form
            toks = text.rsplit(None, 1)
            if len(toks) != 2:
                return None
            english, rest = toks[0].strip(), toks[1].strip()
            forms, unc = split_forms(rest)
    english = english.rstrip(" .:").strip()
    if not english or not forms:
        return None
    return {"english": english, "pos": pos, "forms": forms, "uncertain": unc}

def parse_continuation(s):
    """Parse an additional-form line -> (pos, forms, uncertain)."""
    pos = None
    if s[:1] in DASHES:
        s = s[1:].strip()
    m = re.match(r"^(v\.|n\.)\s+(.*)$", s)
    if m:
        pos = m.group(1)
        s = m.group(2).strip()
    forms, unc = split_forms(s)
    return pos, forms, unc

def main():
    raw_lines = io.open(SRC, encoding="utf-8").read().splitlines()
    content = [norm(l) for l in raw_lines if not is_junk(l)]

    entries = []
    buf = ""

    def flush(text):
        e = parse_entry(text)
        if e:
            entries.append(e)
            return True
        return False

    for s in content:
        if is_continuation_form(s) and entries and not buf:
            # additional form for the last completed entry
            pos, forms, unc = parse_continuation(s)
            if forms:
                last = entries[-1]
                for f in forms:
                    if f not in last["inuttut_tmp"]:
                        last["inuttut_tmp"].append(f)
                if pos and not last["pos"]:
                    last["pos"] = pos
                last["uncertain"] = last["uncertain"] or unc
            continue

        candidate = (buf + " " + s).strip() if buf else s
        if line_has_form(s) or line_has_form(candidate):
            if flush(candidate):
                entries[-1]["inuttut_tmp"] = list(entries[-1].pop("forms"))
                buf = ""
            else:
                buf = candidate
        else:
            buf = candidate  # English gloss wrapping to next line

    # finalize schema
    out = []
    for i, e in enumerate(entries, 1):
        out.append({
            "id": i,
            "english": e["english"],
            "inuttut": e["inuttut_tmp"],
            "pos": e["pos"],
            "uncertain": bool(e["uncertain"]),
        })

    io.open(OUT, "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False, indent=1))
    # stats
    n = len(out)
    npos = sum(1 for e in out if e["pos"])
    nunc = sum(1 for e in out if e["uncertain"])
    nmulti = sum(1 for e in out if len(e["inuttut"]) > 1)
    print("entries:", n)
    print("with pos:", npos, " uncertain:", nunc, " multi-form:", nmulti)

if __name__ == "__main__":
    main()
