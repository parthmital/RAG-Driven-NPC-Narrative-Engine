---
name: docs-links
description: Keep the Markdown docs (README.md, ARCHITECTURE.md, DESIGN.md, RESEARCH.md, docs/research_article.md) linked, Prettier-clean and consistent. Use whenever editing any of them or adding links, anchors, citations or cross-references.
---

# Docs links and format

- **Format:** the docs are Prettier-clean with Prettier 3.9.9 (tabs, from `.prettierrc.json`). After editing, run `npm_config_cache="$PWD/.cache/npm" npx --yes prettier@3.9.9 --write <files>` and then `--check`. Table realignment noise in the diff is expected.
- **Paths:** link repository paths in code spans with
  `.venv/Scripts/python .claude/skills/docs-links/scripts/link_doc_paths.py <docs...>`.
  It links only git-tracked paths (so never `.env`, `.cache` or `.agent-local`), resolves `metrics/...` under `notebooks/outputs/`, links model IDs to their model cards, and is idempotent. Untracked files get a manual link once they exist.
- **research_article.md anchors:** `<a id="section-N">`, `table-N`, `figure-N` and `ref-N` sit on their own line before the target, followed by a blank line. Cite as `[Author et al., Year](#ref-N)` and refer to `[Table N](#table-N)`. Do not link a heading to itself.
- **External URLs:** a GitHub file link must exist on GitHub. Backend code is linked at the evaluated commit; run outputs are linked on `main`.
- **Check:** `.venv/Scripts/python .claude/skills/docs-links/scripts/check_md_links.py README.md ARCHITECTURE.md DESIGN.md RESEARCH.md docs/research_article.md --external`
  This catches missing files and anchors, including GitHub heading slugs. Remaining DOI 403s are publisher bot-blocking (see `citation-verification`).
- Numbers and claims follow the `eval-results-facts` sync rule. README edits also follow the global readme-generator rules: ASCII only, no invented facts.
