"""Purpose: check every Markdown link in the given docs: relative file targets exist, #anchors match an explicit
<a id> or a GitHub heading slug (in the same or the target file), and external URLs answer (with --external).
Inputs: Markdown files, optional --external.  Output: list of broken links; exit code 1 if any.
Run: .venv/Scripts/python .claude/skills/docs-links/scripts/check_md_links.py README.md docs/research_article.md --external
"""

import os
import re
import sys
import urllib.request

LINK = re.compile(
    r"(?<!\!)\[(?:[^\[\]]|\[[^\]]*\])*\]\(([^)\s]+)\)|!\[[^\]]*\]\(([^)\s]+)\)"
)


def slug(heading):
    s = heading.strip().lower()
    s = re.sub(r"[^\w\- ]", "", s)  # GitHub keeps letters, digits, '-', '_' and spaces
    return s.replace(" ", "-")


def anchors(path, cache={}):
    if path not in cache:
        text = open(path, encoding="utf-8").read()
        text_no_code = re.sub(r"```.*?```", "", text, flags=re.S)
        ids = set(re.findall(r'<a id="([^"]+)"', text))
        seen = {}
        for h in re.findall(r"^#{1,6} (.+)$", text_no_code, flags=re.M):
            base = slug(re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", h).replace("`", ""))
            n = seen.get(base, 0)
            ids.add(base if n == 0 else f"{base}-{n}")
            seen[base] = n + 1
        cache[path] = ids
    return cache[path]


broken, external = [], {}
for doc in [a for a in sys.argv[1:] if not a.startswith("--")]:
    text = open(doc, encoding="utf-8").read()
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"`[^`\n]*`", "", text)  # inline code is never rendered as a link
    base_dir = os.path.dirname(os.path.abspath(doc))
    for m in LINK.finditer(text):
        target = m.group(1) or m.group(2)
        if target.startswith(("http://", "https://")):
            external.setdefault(target, doc)
            continue
        if target.startswith("mailto:"):
            continue
        file_part, _, frag = target.partition("#")
        file_path = (
            os.path.normpath(os.path.join(base_dir, file_part.replace("%20", " ")))
            if file_part
            else os.path.abspath(doc)
        )
        if not os.path.exists(file_path):
            broken.append(f"{doc}: missing file -> {target}")
        elif frag and file_path.endswith(".md") and frag not in anchors(file_path):
            broken.append(f"{doc}: missing anchor -> {target}")

if "--external" in sys.argv:
    for url, doc in sorted(external.items()):
        try:
            req = urllib.request.Request(
                url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"}
            )
            code = urllib.request.urlopen(req, timeout=30).status
        except Exception as exc:
            code = getattr(exc, "code", type(exc).__name__)
        if code not in (200, 202):
            broken.append(f"{doc}: HTTP {code} -> {url}")
print(f"checked {len(external)} external URLs; broken: {len(broken)}")
print("\n".join(broken))
sys.exit(1 if broken else 0)
