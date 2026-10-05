# Research Notes

## Literature for the research paper (searched 2026-10-05)

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
- Not linked: Holm (1979) has no DOI and its JSTOR page blocks automated checks, so no URL was verified.
