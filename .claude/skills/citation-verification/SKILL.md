---
name: citation-verification
description: Verify and add literature citations and links for docs/paper/references.bib, docs/research_article.md and RESEARCH.md. Use whenever adding, editing or checking a reference, DOI, arXiv ID or external URL.
---

# Citation verification

Cite only what you have opened or confirmed through an API, and never guess pages, volumes or authors.

- **Metadata:** `.venv/Scripts/python .claude/skills/citation-verification/scripts/crossref_lookup.py "Exact title"` returns authors, venue, volume, pages and DOI. Crossref rate-limits (HTTP 429), so space out large batches.
- **arXiv:** one batch request, `curl -sL "https://export.arxiv.org/api/query?id_list=ID1,ID2&max_results=50" | grep -o "<title>[^<]*</title>"`. Use HTTPS with `-L`.
- **Blocked automated sources:** DBLP, IEEE Xplore and JSTOR. Use Crossref, ACL Anthology, AAAI OJS, or the NeurIPS and PMLR proceedings pages instead.
- **DOI returning 403 or 202** is publisher bot-blocking (ACM, Wiley, MIT Press, IEEE). Confirm with `curl -s -o /dev/null -w "%{http_code} %{redirect_url}" https://doi.org/<doi>`: a 302 to the right publisher means the DOI is fine.
- **API endpoints are not links:** point readers at the docs pages (`info.arxiv.org/help/api`, the Crossref REST API documentation).
- If a source cannot be verified, leave it unlinked and say so in RESEARCH.md (for example Holm 1979).
- Log every search in `RESEARCH.md`: one dated section per topic, linked sources, and no paths into ignored folders.
- BibTeX formatting is covered in the `paper-latex` skill.
