---
name: repo-shell-tooling
description: Shell, Python and Node pitfalls in this Windows repo. Use before any Bash or PowerShell command whose text contains backslashes (LaTeX, regex, escapes), before pip or npx installs, and before writing helper scripts.
---

# Repo shell and tooling

- **Backslashes get mangled.** Git Bash here collapses `\\` even inside quoted heredocs and `python -c` (a LaTeX `\\begin` became a backspace byte; `sed` dropped the `\` from `\%`). For any text with backslashes, use the Edit tool, or Write a `.py` file and run it. After a scripted edit, check for damage: `grep -cP "[\x00-\x08]" <file>` should print 0.
- **Python:** `.venv/Scripts/python`. Install extras repo-locally: `PIP_CACHE_DIR=.cache/pip .venv/Scripts/python -m pip install <pkg>`. Analysis extras already used: pandas, scipy, statsmodels, pypdf, pypdfium2, pillow.
- **Node CLIs without node_modules:** `npm_config_cache="$PWD/.cache/npm" npx --yes <pkg>@<version locked in a package-lock.json>`, e.g. `prettier@3.9.9`.
- **Scratch versus shared:** throwaway files go in `.agent-local/` (git-ignored). Anything another person needs belongs in the repo: `scripts/*.mjs` or a skill's `scripts/`.
- `.gitattributes` has `* text=auto` and `core.autocrlf=true`, so "LF will be replaced by CRLF" warnings are harmless. `git status` can list many files as `M` with no real change. Before reporting or reverting, list the files that actually changed: `git diff --name-only | while read f; do [ -n "$(git diff --numstat -- "$f")" ] && echo "$f"; done`.
- Never execute `notebooks/*.ipynb` locally; it targets Kaggle GPU T4 x2.
- Make every rewrite script idempotent: rerun it and confirm the second run changes nothing.
