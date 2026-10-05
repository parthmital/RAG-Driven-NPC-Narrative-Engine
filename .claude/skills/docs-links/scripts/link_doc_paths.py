"""Purpose: make repository paths and model IDs in Markdown docs clickable. A code span such as `Backend/config.py`
becomes [`Backend/config.py`](relative/path) when the path exists and is tracked by git; model IDs link to their
model card. Fenced code blocks, headings, inline HTML and spans that are already links are left untouched.
Inputs: Markdown files.  Output: rewrites them in place (idempotent) and prints the number of new links per file.
Run: .venv/Scripts/python .claude/skills/docs-links/scripts/link_doc_paths.py README.md docs/research_article.md
"""

import os
import re
import subprocess
import sys

ROOT = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
).stdout.strip()
TRACKED = set(
    subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True
    ).stdout.split("\n")
)
TRACKED_DIRS = {os.path.dirname(p) for p in TRACKED}
for p in list(TRACKED_DIRS):
    while p:
        p = os.path.dirname(p)
        TRACKED_DIRS.add(p)

MODELS = {  # verified 2026-10-06 (HTTP 200)
    "IFM/K2-Horizon-7B": "https://huggingface.co/IFM/K2-Horizon-7B",
    "IFM/K2-Horizon-3.7B": "https://huggingface.co/IFM/K2-Horizon-3.7B",
    "openai/gpt-oss-120b": "https://console.groq.com/docs/model/openai/gpt-oss-120b",
    "sentence-transformers/all-MiniLM-L12-v2": "https://huggingface.co/sentence-transformers/all-MiniLM-L12-v2",
}

SPAN = re.compile(r"(?<!\[)`([\w./\-]+)`(?!\]\()")


def target(span, doc_dir):
    if span in MODELS:
        return MODELS[span]
    rel = span.rstrip("/")
    if "/" not in rel or rel.startswith("."):
        return None
    # run outputs are often cited relative to notebooks/outputs/ (metrics/..., predictions/...)
    if (
        rel not in TRACKED
        and rel not in TRACKED_DIRS
        and f"notebooks/outputs/{rel}" in TRACKED | TRACKED_DIRS
    ):
        rel = f"notebooks/outputs/{rel}"
    if rel in TRACKED or rel in TRACKED_DIRS:
        link = os.path.relpath(os.path.join(ROOT, rel), doc_dir).replace(os.sep, "/")
        return link + ("/" if span.endswith("/") else "")
    return None


for doc in sys.argv[1:]:
    path = os.path.abspath(doc)
    doc_dir = os.path.dirname(path)
    lines = open(path, encoding="utf-8").read().split("\n")
    fenced, added = False, 0
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced or line.startswith("#") or line.lstrip().startswith("<"):
            continue

        def rep(m):
            global_added = target(m.group(1), doc_dir)
            if not global_added:
                return m.group(0)
            return f"[`{m.group(1)}`]({global_added})"

        new = SPAN.sub(rep, line)
        added += new.count("](") - line.count("](")
        lines[i] = new
    open(path, "w", encoding="utf-8").write("\n".join(lines))
    print(f"{doc}: {added} new links")
