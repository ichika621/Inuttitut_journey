# -*- coding: utf-8 -*-
"""Step 0 — extract the dictionary PDF to plain UTF-8 text with PyMuPDF.

Usage:  python scripts/extract_pdf.py "English-Inuttut Dictionary.pdf" scratch/raw_full.txt
Requires: pip install pymupdf
"""
import io, os, sys
import fitz  # PyMuPDF

SRC = sys.argv[1] if len(sys.argv) > 1 else "English-Inuttut Dictionary.pdf"
OUT = sys.argv[2] if len(sys.argv) > 2 else "scratch/raw_full.txt"

os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
doc = fitz.open(SRC)
with io.open(OUT, "w", encoding="utf-8") as f:
    for i in range(doc.page_count):
        f.write("==== PAGE %d ====\n" % (i + 1))
        f.write(doc[i].get_text())
print("extracted %d pages -> %s" % (doc.page_count, OUT))
