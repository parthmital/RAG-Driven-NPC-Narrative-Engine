"""Purpose: render PDF pages to PNG for visual checks, and report page count and '??' (unresolved reference) occurrences.
Inputs: pdf path, output dir, optional scale.  Outputs: page-NN.png files in the output dir.
Run: .venv/Scripts/python .claude/skills/paper-latex/scripts/render_pdf_pages.py docs/paper/main.pdf .agent-local/output/paper/pages 1.3
"""

import sys
from pathlib import Path
import pypdfium2 as pdfium
from pypdf import PdfReader

pdf, out = sys.argv[1], Path(sys.argv[2])
scale = float(sys.argv[3]) if len(sys.argv) > 3 else 1.3
out.mkdir(parents=True, exist_ok=True)
text = "".join(p.extract_text() or "" for p in PdfReader(pdf).pages)
print("pages", len(PdfReader(pdf).pages), "| '??' occurrences:", text.count("??"))
doc = pdfium.PdfDocument(pdf)
for i in range(len(doc)):
    doc[i].render(scale=scale).to_pil().save(out / f"page-{i+1:02d}.png")
