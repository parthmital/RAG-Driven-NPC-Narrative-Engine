# Agent Guide

Purpose: rules and commands every agent task in this repository needs. Read when: always.
Last verified: 2026-11-17.

## Commands

- Setup and run both services: `npm run dev` (repository root). The first run installs everything into `.venv`, `node_modules`, and `.cache`.
- All checks (CI equivalent): `npm run check`.
- Backend tests, all: `cd Backend && ../.venv/Scripts/python.exe -m unittest discover -s tests` (POSIX: `../.venv/bin/python`).
- Backend tests, one file: `cd Backend && ../.venv/Scripts/python.exe -m unittest tests.test_state_integrity`.
- Backend format: `cd Backend && ../.venv/Scripts/python.exe -m black .`
- Frontend: `npm --prefix Frontend run format`, `typecheck`, `lint`, `test`, `build`.
- Notebook backend bundle: `.venv/Scripts/python.exe scripts/notebook_bundle.py` (rewrite) or `--check`.
- Paper, all six PDFs (manuscript, supplement, variants): `npm run paper`.

## Conventions

- Every world change is an event in `Backend/schemas/events.py`, applied by `Backend/core/reducer.py`, after `Backend/game/validator.py` accepts it.
- Layer rules are in `ARCHITECTURE.md` and enforced by `Backend/tests/test_architecture.py`.
- Validator limits live in `Backend/config.py`. The prompt reads the same constants.
- Launcher code is Node ESM in `scripts/`. Shared setup lives in `scripts/lib/workspace.mjs`.
- Paper numbers come only from `notebooks/outputs/`. The paper has no semicolons in its text.
- The manuscript `docs/paper/main.tex` must stay within 10 pages including references (IEEE Transactions on Games). Detail goes in `docs/paper/supplementary.tex`. Cross-document references use the xr-hyper prefixes `S-` (manuscript to supplement) and `M-` (supplement to manuscript). Shared packages and macros live in `docs/paper/paper-preamble.tex`.
- The paper is written in the third person. Figure, table and algorithm captions are one line, and what a float shows is described in the text that cites it.
- `docs/paper/main.aux`, `main-anonymised.aux`, `supplementary.aux` and `supplementary-anonymised.aux` are tracked so that a standalone compile of either document resolves the `S-` and `M-` references. `npm run paper` rewrites them.
- Paper variants are wrappers that define `\Anonymised`, `\TitlePage`, or `\NoReferences` and then `\input{main}` or `\input{supplementary}`. Guard variant-specific parts with `\ifdefined`.
- Formatting: tabs in JS and TS (`.prettierrc.json`), `black` for Python, LF line endings (`.gitattributes`).

## Gotchas

- **`npm run check` fails at Notebook backend**: `Backend/` changed after the notebook bundle was written. Run `scripts/notebook_bundle.py`, then commit the notebook.
- **First setup takes minutes**: PyTorch downloads and unpacks into `.venv`. The `Still ...` lines show progress. pip's log is `.cache/pip-install.log`.
- **pip backtracks (`This is taking longer than usual`)**: a version cap in `Backend/requirements.txt` conflicts with a transitive dependency. Widen the cap. Do not re-add a `websockets` pin, because `uvicorn[standard]` owns it.
- **Never run the notebook locally**: it needs Kaggle GPU T4 x2. Refresh `notebooks/outputs/` from a Kaggle run.
- **`Reference 'S-...' undefined` in a paper log**: the manuscript was compiled alone without `supplementary.aux` (plain `tectonic main.tex` keeps no intermediates). Run `npm run paper`, which builds the pair in order and keeps the `.aux` files.
- **Anonymised paper still identifies authors**: a new repository link bypassed the macros in `docs/paper/paper-preamble.tex` (`\bsrc`, `\esrc`, `\msrc`, `\mdir`, `\osrc`, `\repolink` with `\evaltree`, `\commit`, `\codeavailability`). Use them: the anonymised copies point them at the anonymous mirror `https://anonymous.4open.science/r/RAG-Driven-NPC-Narrative-Engine/`, which mirrors `main` and expires on 2027-04-17.
- **A VS Code terminal is not in `.venv`**: it opened before setup created `.venv`, or it uses another profile. `.vscode/settings.json` makes `PowerShell (.venv)` the default. Open a new terminal, or call `.venv/Scripts/python.exe` directly.
- **Python writes CRLF on Windows**: write files with `newline="\n"` or bytes.

## Docs

- `README.md`: setup, scripts, API, evaluation results, troubleshooting.
- `ARCHITECTURE.md`: module map, dependency rules, decisions, growth signals.
- `DESIGN.md`: UI tokens, components, and patterns.
- `RESEARCH.md`: dated research behind references, venue, and dependencies.
- `docs/human-evaluation.md`: the rating protocol for the annotation sheets.
