"""Purpose: list every link annotation in a PDF: external URIs (deduplicated, optionally HTTP-checked) and
the count of internal (GoTo) links, to verify that references, citations and URLs are clickable.
Inputs: pdf path, optional --check to request each URI.  Output: printed report.
Run: .venv/Scripts/python .claude/skills/paper-latex/scripts/list_pdf_links.py docs/paper/main.pdf --check
"""

import sys
import urllib.request
from collections import Counter

from pypdf import PdfReader

reader = PdfReader(sys.argv[1])
uris, internal = Counter(), 0
for page in reader.pages:
    for annot in page.get("/Annots") or []:
        a = annot.get_object()
        if a.get("/Subtype") != "/Link":
            continue
        action = a.get("/A")
        if action is not None and action.get_object().get("/URI"):
            uris[str(action.get_object()["/URI"])] += 1
        else:
            internal += 1
print(
    f"internal links: {internal} | external links: {sum(uris.values())} ({len(uris)} unique)"
)
for uri in sorted(uris):
    status = ""
    if "--check" in sys.argv:
        try:
            req = urllib.request.Request(
                uri, method="HEAD", headers={"User-Agent": "Mozilla/5.0"}
            )
            status = urllib.request.urlopen(req, timeout=30).status
        except Exception as exc:  # report, do not stop
            status = getattr(exc, "code", type(exc).__name__)
    print(f"  [{status}] {uri}")
