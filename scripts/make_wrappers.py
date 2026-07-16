# -*- coding: utf-8 -*-
"""Step 5 — emit file://-friendly JS wrappers from the canonical JSON, so the
game can be opened straight from disk without a server.

Usage:  python scripts/make_wrappers.py
"""
import io

def wrap(json_path, js_path, global_name):
    data = io.open(json_path, encoding="utf-8").read()
    io.open(js_path, "w", encoding="utf-8").write(
        "// Auto-generated file://-friendly wrapper. Canonical data lives in %s.\n"
        "window.%s = %s;\n" % (json_path.split("/")[-1], global_name, data))
    print("wrote", js_path)

wrap("data/dictionary.json", "data/dictionary.js", "DICTIONARY")
wrap("data/nouns.json", "data/nouns.js", "NOUNS")
wrap("data/story.json", "data/story.js", "STORY")
