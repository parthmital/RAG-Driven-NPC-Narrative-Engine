---
name: paper-latex
description: Edit, build and verify the LaTeX paper in docs/paper (main.tex, references.bib, main.pdf) with Tectonic. Use for any change to the paper, its figures, tables, bibliography or links, or when `npm run paper` fails.
---

# Paper (docs/paper)

**Build:** `npm run paper` (`scripts/paper.mjs`). It runs `docs/tectonic.exe --keep-logs --reruns 3` with its cache in `.cache/tectonic`, and fails on TeX errors, overfull boxes, undefined references or citations, missing glyphs and BibTeX warnings. Do not drop `--reruns 3`: Tectonic 0.15's own `.bbl` check otherwise loops to 6 passes after the document has converged.

**Harmless output:** `algorithm.sty:11 invalid UTF-8` (upstream package) and `Fontconfig error`.

## Known fixes

| Symptom                                 | Fix                                                                                                                                                          |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Duplicate `@ALG@line` anchors           | `\def\theHALG@line{\thealgorithm.\arabic{ALG@line}}` (`\renewcommand` fails because the macro is undefined)                                                  |
| Wide table                              | `\begin{adjustbox}{max width=\linewidth}`, `p{..}` columns, or `\setlength{\tabcolsep}{4pt}`; split crowded cells into columns                               |
| Overfull line from a path or identifier | `\_` is redefined to allow a break; links use `\linkpath`, which goes through `\nolinkurl` with `xurl`                                                       |
| `_` in link macros or captions          | `\detokenize{#1}`; never `\path` inside a macro argument or caption                                                                                          |
| BibTeX "volume and number"              | drop `number` from `@inproceedings` (plainnat)                                                                                                               |
| Non-clickable DOI or arXiv entry        | the `doi` package handles DOIs; for arXiv use `howpublished = {\href{https://arxiv.org/abs/ID}{arXiv:ID}}`; entries without a DOI get a verified `url` field |
| Floats drift into later sections        | `\usepackage[section]{placeins}` (already loaded)                                                                                                            |
| Cropped or ugly plot title              | `\adjincludegraphics[trim={0 0 0 {0.08\height}},clip]`; never edit the notebook's plots                                                                      |

## Conventions

- Repository links: `\bsrc{core/reducer.py}` for Backend files pinned to the evaluated commit, `\esrc` for repo-root files at that commit, `\msrc` and `\mdir` for files and folders on `main`, `\osrc{metrics/...}` for notebook outputs, plus `\commit{}` and `\hfmodel{}`. Link only files that already exist on GitHub.
- Numbers come from the `eval-results-facts` skill; citations from `citation-verification`.

## Verify after every change

1. `npm run paper` prints "clean log".
2. `.venv/Scripts/python .claude/skills/paper-latex/scripts/render_pdf_pages.py docs/paper/main.pdf .agent-local/output/paper/pages 1.3` reports `'??' occurrences: 0`. Look at the pages you changed.
3. `.venv/Scripts/python .claude/skills/paper-latex/scripts/list_pdf_links.py docs/paper/main.pdf --check` shows every external link at 200 (see `citation-verification` for DOI 403s).
