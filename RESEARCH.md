# Research Notes

Purpose: dated evidence behind the paper's literature, venue, and dependency decisions. Read when: choosing or revisiting a library, reference, venue, or approach.

## Target journal for the paper (2026-10-26)

**Brief.** Pick the journal the paper is formatted for, with an official LaTeX template, and apply its limits.

**Findings.**

- IEEE Transactions on Games fits the topic: the survey already cites an LLM dialogue paper published there (Phillips et al., `phillips2025goal`, see the 2026-10-16 entry). Its scope page was not opened (inference). Its submission guidelines require the standard IEEE Transactions format, with templates from the IEEE Author Center, which is the `IEEEtran` journal class the paper already uses.
- Its limits: abstract of 150 to 200 words in one paragraph with no abbreviations or references, 2 to 5 keywords (another passage says three or four), double-anonymous review for submissions from 1 January 2025 (another passage still says single-blind), and full papers limited to 10 pages with a charge of USD 200 per extra page.
- Runner-up: Entertainment Computing (Elsevier). It fits the topic, but the paper already uses the IEEE class, and its official LaTeX template was not checked.

**Decision.** Adopt IEEE Transactions on Games. The abstract was cut to 200 words with abbreviations spelled out, and the keywords to five. The 27-page paper was split into a 10-page manuscript (references included, so no over-length charge applies) and a 15-page supplementary document, linked with `xr-hyper`, as the guidelines exclude supplementary material from the limit. The anonymised copies, separate title page, and no-references copy are built by `npm run paper`. Final accepted papers also carry author biographies within the 10 pages, which the authors must supply.

**Sources.** [IEEE ToG submission guidelines](https://www.transactions.games/submit/submission-guidelines) (2026-10-26), [IEEE Author Center](https://ieeeauthorcenter.ieee.org/) (linked from the guidelines).

## Backend dependency resolution on a fresh clone (2026-10-26)

**Brief.** The first `npm run dev` on a fresh clone appeared to hang while installing PyTorch.

**Findings.**

- pip's verbose log of a fresh install showed `pip is looking at multiple versions of langsmith` and `This is taking longer than usual`. It fetched metadata for 65 `langsmith` versions, because `langsmith` 0.8.6 to 0.14.12 require `websockets>=15.0` and `Backend/requirements.txt` capped `websockets<14.0`. It settled on `langsmith` 0.8.5.
- No backend code imports `websockets`. `uvicorn[standard]` already declares `websockets>=13.0` for the WebSocket route. The cap dates from the first commit, with no recorded reason.
- `numpy<2.0` resolves to NumPy 1.26.4, which has no wheels for Python 3.13 or newer, so setup on a current Python would try to compile NumPy. The evaluated backend ran on NumPy 2.1.3 and sentence-transformers 5.4.1 (`notebooks/outputs/metrics/run_manifest.json`).
- After removing the `websockets` line and widening `numpy` to `<3.0` and `sentence-transformers` to `<6.0`, a dry run resolved in one pass with no backtracking.
- The launcher ran pip with `--quiet` through a blocking `spawnSync`, so the resolver warnings and the minutes-long, silent unpacking of about 30,000 files into `.venv` were invisible, and `Ctrl+C` could not run a handler.

**Decision.** Fix the conflicting pins (Build) and make the install observable and interruptible in `scripts/lib/workspace.mjs`: streamed status, a heartbeat, a pip log in `.cache/pip-install.log`, and a `Ctrl+C` handler that stops pip and explains how to resume. A full lock file was considered and not adopted: with the conflict removed the resolver needs no backtracking, and a lock file adds an upgrade chore.

**Sources.** Local pip 24.0 logs of fresh installs in `.agent-local/` (2026-10-26). `pip index versions` against PyPI (2026-10-26).

## Paper fact-check after the third Review-03 run (checked 2026-10-26)

**Brief.** Fact-check every claim in `docs/paper/main.tex` before building the submission variants.

**Findings.**

- Every number in the paper was cross-checked against `notebooks/outputs/` with `.agent-local/scripts/paper_number_crosscheck.py`. The only numbers not found verbatim were thousand-separated token counts, rounded p-values, and the Generative Agents figures, and each matched its source.
- Row-level claims were recomputed from the prediction files: the 28 wrong age-5 F4 answers, all with the distractor in the prompt (4 for F4v1), 471 of 546 F1 and 469 of 546 F3 flagged live turns, 4 of 684 lawful twin proposals rejected, A5's 44 currency, 6 theft, and 3 relocation successes, and the per-point crash consistency.
- Three statements were corrected. The error analysis now says that conditions which never reject proposals still trip the arrival cue (17 F1, 16 F3, and 28 A5 turns). The crash-trial sentence now says that the Review-02 path was consistent exactly when the crash lost no turn, not that it failed at every other crash point. The budget-sweep sentence now gives B3's 98.3% at half the budget instead of grouping it with F4 and B2.
- All 34 DOIs resolve in Crossref with matching titles, apart from two temporary HTTP 429 rate-limit responses (`zhong2024memorybank`, `greshake2023indirect`) that were verified on 2026-10-24. Every entry is cited, and no entry is a preprint or a book.

**Sources.** `notebooks/outputs/` at commit `eff999e`, the [Crossref REST API](https://api.crossref.org/) (2026-10-26).

## Paper fact-check after the second Review-03 run (checked 2026-10-24)

**Brief.** Re-verify every reference and every number the paper attributes to other work before publishing the results of the 24 October 2026 run. Scope: the 44 entries of [docs/paper/references.bib](docs/paper/references.bib), the Crossref REST API, the publishers' and proceedings' pages, and the arXiv HTML copy of the base paper.

**Findings.**

- All 34 DOIs resolve in Crossref with the same title and year as the bibliography (`.agent-local/scripts/verify_bib_crossref.py`, git-ignored). The 10 entries without a DOI (PMLR, NeurIPS, ICLR, OpenReview, JSTOR) return HTTP 200. Publisher DOI links that answer 403 or time out (ACM, Wiley, MIT Press, Elsevier) are bot blocks, not dead links; Crossref confirms them.
- Generative Agents (Park et al., UIST 2023), checked in the full text: recency decay 0.995 per sandbox game hour; importance on a 1 to 10 scale; reflection when summed importance exceeds 150; recency, importance and relevance min-max scaled with all weights 1; 100 Prolific evaluators; TrueSkill 29.89 for the full architecture against 21.21 with no memory, planning or reflection, d = 8.16; 1.3% (6 of 453) of awareness answers hallucinated; agents "embellish their knowledge"; `gpt3.5-turbo`; 25 agents for two game days "costing thousands of dollars in token credits". All match the paper.
- NCP-Bench (Ma et al., PMLR 306): the abstract reports a 42% survival rate after 20 turns for the best model and fact-conflict rates of 40% to 68% across models. Matches the paper.

**Recommendation.** No reference or attributed claim needs to change.

**Sources.** [api.crossref.org](https://api.crossref.org/) (2026-10-24); [arXiv HTML of Generative Agents](https://arxiv.org/html/2304.03442), the preprint of the cited UIST paper, used only to check the cited numbers (2026-10-24); [PMLR v306 ma26ap](https://proceedings.mlr.press/v306/ma26ap.html) (2026-10-24).

## Review-03 corrections: baselines, judge, model families and testing (decided 2026-10-22)

**Brief.** Implement the faculty's Review-03 requirements with the least new machinery: stronger memory baselines, dialogue repair, an evaluation of dialogue-state contradictions that does not rely on refusal words, independent model families that run on 2 x T4, property-based tests, and a self-contained reproducibility package. Tier: Quick (bounded choices in a familiar stack; the defects themselves were bug fixes with no research).

**Decisions.**

- **Memory baselines: Borrow.** B4 re-implements the Generative Agents retrieval rule (Park et al., UIST 2023, the base paper: min-max-normalised recency with decay 0.995 plus relevance; the LLM-rated importance term is omitted because it needs an LLM call per memory write). B5 re-implements the MemoryBank forgetting curve (Zhong et al., AAAI 2024: retention exp(-t/S), strength raised on each recall). Both are published; MemGPT and Mem0 were rejected because they are still arXiv-only (see the 2026-10-16 entry below), and their LLM-managed memories would add an LLM call per turn to every condition.
- **Dialogue repair: Borrow.** The validator-feedback re-ask pattern (the rejected proposals and the committed state go back to the model, which rewrites only the reply), with a deterministic neutral fallback when the rewrite does not parse. Runner-up: always appending a fixed correction line, rejected because it leaves the contradicting speech in place.
- **Independent families: Adopt.** [`Qwen/Qwen2.5-7B-Instruct`](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct) (Apache-2.0, ungated, `Qwen2ForCausalLM`) and [`microsoft/Phi-4-mini-instruct`](https://huggingface.co/microsoft/Phi-4-mini-instruct) (MIT, ungated, `Phi3ForCausalLM`), both checked on the Hugging Face API on 2026-10-22 and served by vLLM. Runner-up: [`ibm-granite/granite-3.3-8b-instruct`](https://huggingface.co/ibm-granite/granite-3.3-8b-instruct) (Apache-2.0, ungated), left out for time. Gated families (Llama, Gemma, Mistral) were excluded because the notebook must run without an access token.
- **Contradiction judge: Adopt** Qwen2.5-7B-Instruct as an LLM judge from a different family than the generator, validated against blinded human labels on shared items; the cue-word proxy is kept for comparability with Review-02.
- **Property-based tests: Build** with seeded `random` generators in `unittest` (3,000 random turns per run). Hypothesis was not added because the project's rules require asking before adopting a copyleft (MPL-2.0) dependency; the seeded tests already detect the Review-02 defects (472 of 3,000 random turns committed a violation under the old validator, 0 under the new one).
- **Reproducibility: Build** a hashed, compressed backend bundle inside the notebook ([`scripts/notebook_bundle.py`](scripts/notebook_bundle.py)) instead of a network clone, with exact package pins and a cache-only regeneration mode.

**Sources.** Park et al. (UIST 2023, [10.1145/3586183.3606763](https://doi.org/10.1145/3586183.3606763)); Zhong et al., MemoryBank ([AAAI 29946](https://ojs.aaai.org/index.php/AAAI/article/view/29946)); Hugging Face model API pages above (2026-10-22).

## Published-only references and base paper for the project submission (searched 2026-10-16)

**Brief.** The project submission requires a base paper, reference papers that are all published (no preprints), and a paper with the sections Introduction, Literature Survey, Research Gap, Proposed Methodology, Dataset Description and Usage, Novelty, Algorithms, Implementation and Comparison of Results. Replace every arXiv-only reference in [`docs/paper/references.bib`](docs/paper/references.bib) with a published version or a published substitute, choose the base paper, and collect the reference PDFs.

**Scope.** PMLR volume index and the ICML 2026 volume (v306), ACL Anthology, AAAI OJS (AIIDE), ICLR proceedings, OpenReview, NeurIPS proceedings, Crossref REST API, Unpaywall API, and the publishers' PDFs. IEEE Xplore and ScienceDirect blocked automated access.

**Findings.**

- Base paper: Generative Agents (Park et al., UIST 2023, [10.1145/3586183.3606763](https://doi.org/10.1145/3586183.3606763)), chosen by the user. From the published PDF: retrieval sums min-max-normalised recency (decay 0.995 per sandbox hour), LLM-rated importance (1 to 10) and cosine relevance with equal weights; reflection fires when summed importance exceeds 150; 100 evaluators ranked believability, full architecture TrueSkill $\mu=29.89$ against 21.21 without memory ($d=8.16$); 1.3% (6 of 453) relationship answers hallucinated; two simulated days cost "thousands of dollars in token credits". It describes no rule check of agent actions.
- Now published: NCP-Bench (Ma et al.) appears in PMLR 306 (ICML 2026), pp. 85171 to 85192 ([v306/ma26ap](https://proceedings.mlr.press/v306/ma26ap.html)). Its abstract reports 42% survival after 20 turns for the best model and fact-conflict rates of 40% to 68%, scored by LLM auditors that the authors say can err on ambiguous text.
- Still arXiv-only on 2026-10-16, so dropped: TALES (2504.14128), Mem0 (2504.19413), ASTP (2510.25014), MemGPT (2310.08560), and the NPC preprints of Braas and Esterle (2511.10277), Figueiredo and Elumeze (2510.25820), Xu (2609.18935) and Chen (2608.04037). Kleppmann (2017) is a book, not a paper, and was replaced.
- Published substitutes, each verified on Crossref or the proceedings page and read in full or in abstract: Xu, Szlam and Weston, Beyond Goldfish Memory (ACL 2022, [10.18653/v1/2022.acl-long.356](https://doi.org/10.18653/v1/2022.acl-long.356)); Tan et al., Reflective Memory Management (ACL 2025, [10.18653/v1/2025.acl-long.413](https://doi.org/10.18653/v1/2025.acl-long.413)); Liu et al., SimpleMem (PMLR 306:78500 to 78513, [v306/liu26dx](https://proceedings.mlr.press/v306/liu26dx.html)); Phillips, Lang and Mould, Goal-Oriented Interactions in Games Using LLMs (IEEE ToG 17(2):510 to 521, [10.1109/TG.2024.3515807](https://doi.org/10.1109/TG.2024.3515807)), in which an LLM reads the dialogue history to advance goal states; Kumaran et al., SceneCraft (AIIDE 2023, [10.1609/aiide.v19i1.27504](https://doi.org/10.1609/aiide.v19i1.27504)); Zhu et al., CALYPSO (AIIDE 2023, [10.1609/aiide.v19i1.27534](https://doi.org/10.1609/aiide.v19i1.27534)); Overeem et al., event-sourced systems in industry (JSS 178:110970, [10.1016/j.jss.2021.110970](https://doi.org/10.1016/j.jss.2021.110970)).
- Published papers whose bibliography `url` pointed at arXiv now point at the proceedings: Reflexion and RAG and MiniLM (NeurIPS proceedings), LongMemEval (ICLR 2025 proceedings), ReAct and CoALA (OpenReview).
- PDFs: 33 of the 44 references were downloaded from the publisher or official proceedings, each checked by its first-page text. Not downloadable without a subscription or blocked to automation: TextWorld (Springer), Phillips et al. and FAISS (IEEE), Field and Welsh (Wiley/OUP), McNemar (Springer), Wilcoxon and Holm (JSTOR), and Overeem et al. (open access on ScienceDirect, bot-blocked).

**Recommendation.** Cite only the published versions above; compare against the base paper architecturally and through its memory ablation and the relevance-only analogue B2, and state that its recency and importance retrieval was not reimplemented.

**Sources.** [PMLR index](https://proceedings.mlr.press/), [PMLR v306](https://proceedings.mlr.press/v306/), [ICML 2026 poster 64786](https://icml.cc/virtual/2026/poster/64786), [ACL 2025.acl-long.413](https://aclanthology.org/2025.acl-long.413/), [ACL 2022.acl-long.356](https://aclanthology.org/2022.acl-long.356/), [AIIDE 27534](https://ojs.aaai.org/index.php/AIIDE/article/view/27534), [AIIDE 27504](https://ojs.aaai.org/index.php/AIIDE/article/view/27504), [ICLR 2025 proceedings](https://proceedings.iclr.cc/paper_files/paper/2025), [IEEE ToG spotlight page (Phillips et al. abstract)](https://www.transactions.games/spotlight/november-2025-spotlight-ppaer), [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/), [Unpaywall API](https://unpaywall.org/products/api), arXiv listings of the dropped preprints (checked for a journal reference).

## Literature for the research paper (searched 2026-10-05)

_Partly superseded on 2026-10-16 (section above): NCP-Bench is now cited from PMLR 306, and Mem0, TALES, ASTP, MemGPT, the four NPC preprints and Kleppmann (2017) are no longer cited._

**Brief.** Update the related-work survey of [`docs/paper/main.tex`](docs/paper/main.tex) with peer-reviewed, workshop and preprint literature up to 2026 on LLM agent memory, LLM state tracking in text worlds, verifier-gated LLM output, LLM NPCs in games, and supporting infrastructure, with every bibliographic field verified.

**Scope.** ACL Anthology, AAAI OJS (AAAI, AIIDE), NeurIPS and PMLR proceedings, arXiv abstract pages, and the Crossref API. DBLP and IEEE Xplore blocked automated access, so IEEE entries were checked through Crossref only.

**Findings.**

- Long-term conversational memory is still an open problem in 2024 to 2026 benchmarks: LoCoMo (ACL 2024), LongMemEval (ICLR 2025). Recent memory systems (MemoryBank, AAAI 2024; HippoRAG, NeurIPS 2024; A-Mem, NeurIPS 2025; Mem0, arXiv 2025) organise or consolidate memory with extra LLM calls or graphs; none couples memory to a validated symbolic game state.
- LLMs remain unreliable state simulators (Wang et al., ACL 2024, ByteSized32-State-Prediction) and lose narrative commitments over long horizons (Ma et al., NCP-Bench, accepted at ICML 2026, arXiv 2608.08160).
- Verifier-gated generation is an established position (LLM-Modulo, ICML 2024). In games, PANGeA (AIIDE 2024) validates player input with an LLM, not a symbolic checker; ASTP (arXiv 2025) constrains in-game trading by state-label prompting plus post-processing.
- 2025 to 2026 NPC preprints (Braas and Esterle; Figueiredo and Elumeze; Xu; Chen) address memory or scaffolding but do not report adversarial invariant probes or replay consistency.
- Filtered vector search (Filtered-DiskANN, WWW 2023) supports the paper's point that post-filtering a global top-k loses in-scope neighbours.

**Recommendation.** Position the paper's contribution as a controlled, paired evaluation of memory scoping and pre-commit symbolic validation with an independent oracle, not as a new memory or validation mechanism.

**Sources.**

- ACL Anthology: [D19-1062](https://aclanthology.org/D19-1062/), [2021.naacl-main.64](https://aclanthology.org/2021.naacl-main.64/), [2022.emnlp-main.637](https://aclanthology.org/2022.emnlp-main.637/), [2020.emnlp-main.525](https://aclanthology.org/2020.emnlp-main.525/), [2024.acl-long.747](https://aclanthology.org/2024.acl-long.747/), [2024.acl-short.1](https://aclanthology.org/2024.acl-short.1/)
- AAAI OJS: [AAAI 6297 (Jericho)](https://ojs.aaai.org/index.php/AAAI/article/view/6297), [AAAI 29946 (MemoryBank)](https://ojs.aaai.org/index.php/AAAI/article/view/29946), [AIIDE 31876 (PANGeA)](https://ojs.aaai.org/index.php/AIIDE/article/view/31876)
- NeurIPS and PMLR proceedings: [HippoRAG (2024)](https://proceedings.neurips.cc/paper_files/paper/2024/hash/6ddc001d07ca4f319af96a3024f6dbd1-Abstract-Conference.html), [A-Mem (2025)](https://proceedings.neurips.cc/paper_files/paper/2025/hash/19909c36f51abc4856b4560aff3d36d6-Abstract-Conference.html), [PMLR v235 kambhampati24a](https://proceedings.mlr.press/v235/kambhampati24a.html)
- arXiv: [2410.10813](https://arxiv.org/abs/2410.10813), [2504.19413](https://arxiv.org/abs/2504.19413), [2504.14128](https://arxiv.org/abs/2504.14128), [2608.08160](https://arxiv.org/abs/2608.08160), [2608.04037](https://arxiv.org/abs/2608.04037), [2609.18935](https://arxiv.org/abs/2609.18935), [2510.25014](https://arxiv.org/abs/2510.25014), [2510.25820](https://arxiv.org/abs/2510.25820), [2511.10277](https://arxiv.org/abs/2511.10277), [2302.12173](https://arxiv.org/abs/2302.12173), [2309.06180](https://arxiv.org/abs/2309.06180); identifiers of every cited arXiv paper were re-checked against the [arXiv API](https://info.arxiv.org/help/api/index.html) on 2026-10-06.
- [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/): Greshake et al. ([10.1145/3605764.3623985](https://doi.org/10.1145/3605764.3623985)), Gallotta et al. ([10.1109/TG.2024.3461510](https://doi.org/10.1109/TG.2024.3461510)), Zhang et al. ([10.1145/3748302](https://doi.org/10.1145/3748302)), Field and Welsh, McNemar, Wilcoxon, Efron, Seabold and Perktold, Johnson et al., Reimers and Gurevych, Kim and Schuster, Geng et al., Park et al., Liu et al., Côté et al.
- ~~Not linked: Holm (1979) has no DOI and its JSTOR page blocks automated checks, so no URL was verified.~~ Superseded 2026-10-09: Holm (1979) has no DOI; its JSTOR stable URL [jstor.org/stable/4615733](https://www.jstor.org/stable/4615733) was read off the first page of the JSTOR-issued PDF (title, author, Scand. J. Statist. 6(2):65-70, 1979). Kleppmann (2017) has no DOI; it links the book's site [dataintensive.net](https://dataintensive.net/), which names the book, the author and O'Reilly. The O'Reilly catalogue page returned HTTP 403 to automated access.
- IEEE format (2026-10-09): `IEEEtran.bst` v1.14 has no `doi` field, so each DOI in [`docs/paper/references.bib`](docs/paper/references.bib) is repeated as a `https://doi.org/` `url`, which the style prints as a link.
