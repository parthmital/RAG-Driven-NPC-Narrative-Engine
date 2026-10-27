# Agent Guide

Purpose: rules and commands every agent task in this repository needs. Read when: always.
Last verified: 2026-10-26.

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
- Paper variants are wrappers that define `\Anonymised`, `\TitlePage`, or `\NoReferences` and then `\input{main}` or `\input{supplementary}`. Guard variant-specific parts with `\ifdefined`.
- Formatting: tabs in JS and TS (`.prettierrc.json`), `black` for Python, LF line endings (`.gitattributes`).

## Gotchas

- **`npm run check` fails at Notebook backend**: `Backend/` changed after the notebook bundle was written. Run `scripts/notebook_bundle.py`, then commit the notebook.
- **First setup takes minutes**: PyTorch downloads and unpacks into `.venv`. The `Still ...` lines show progress. pip's log is `.cache/pip-install.log`.
- **pip backtracks (`This is taking longer than usual`)**: a version cap in `Backend/requirements.txt` conflicts with a transitive dependency. Widen the cap. Do not re-add a `websockets` pin, because `uvicorn[standard]` owns it.
- **Never run the notebook locally**: it needs Kaggle GPU T4 x2. Refresh `notebooks/outputs/` from a Kaggle run.
- **Anonymised paper still identifies authors**: a new repository link bypassed `\repolink`, `\bsrc`, or `\commit`. Use those macros.
- **A VS Code terminal is not in `.venv`**: it opened before setup created `.venv`, or it uses another profile. `.vscode/settings.json` makes `PowerShell (.venv)` the default. Open a new terminal, or call `.venv/Scripts/python.exe` directly.
- **Python writes CRLF on Windows**: write files with `newline="\n"` or bytes.

## Docs

- `README.md`: setup, scripts, API, evaluation results, troubleshooting.
- `ARCHITECTURE.md`: module map, dependency rules, decisions, growth signals.
- `DESIGN.md`: UI tokens, components, and patterns.
- `RESEARCH.md`: dated research behind references, venue, and dependencies.
- `docs/human-evaluation.md`: the rating protocol for the annotation sheets.
