# Results: Memory and State Control for LLM-Driven NPC Dialogue

Generated 2026-10-02T02:03:34Z from commit `0ea345fe14`, ladder level 2, backbone IFM/K2-Horizon-7B (fp16, vLLM 0.30.0, reasoning effort low, thinking budget 192 tokens). Values: mean [95% cluster-bootstrap CI]; held-out = W2a to W4-128.

## Table 1: Main comparison (held-out worlds)

| Condition                      | Recall, age 20+ (%) | Committed violations per 100 transitions | Probe attack success (%) | MRR@6                | P50 / P95 latency (ms) | Input tokens per turn | Replay consistency (%)        |
| ------------------------------ | ------------------- | ---------------------------------------- | ------------------------ | -------------------- | ---------------------- | --------------------- | ----------------------------- |
| Proposed (dual-tier + barrier) | 87.7 [84.2, 91.0]   | 9.2 [4.6, 14.3]                          | 3.1 [1.4, 4.8]           | 0.898 [0.877, 0.917] | 6906 / 9409            | 1399                  | 100.0 [100.0, 100.0]          |
| B0 Full history                | 80.2 [75.9, 84.4]   | 45.0 [38.3, 52.1]                        | 13.3 [10.2, 16.7]        | n/a                  | 10948 / 23984          | 4310                  | not replayable (no event log) |
| B1 Rolling, B                  | 0.0 [0.0, 0.0]      | 45.0 [38.1, 51.9]                        | 13.3 [10.2, 16.7]        | n/a                  | 7020 / 11173           | 1398                  | not replayable (no event log) |
| B1 Rolling, 2B                 | 25.0 [21.3, 28.9]   | n/a (no probe context)                   | n/a                      | n/a                  | 5338 / 5338            | 1823                  | not replayable (no event log) |
| B2 Vector memory               | 84.9 [81.1, 88.6]   | 43.1 [37.3, 48.9]                        | 15.7 [12.4, 19.3]        | 0.750 [0.729, 0.771] | nan / nan              | 1102                  | not replayable (no event log) |
| B3 Generic RAG                 | 63.9 [57.7, 69.9]   | 56.4 [50.8, 61.9]                        | 19.3 [15.7, 23.1]        | 0.707 [0.686, 0.729] | nan / nan              | 1209                  | not replayable (no event log) |

## Table 2: Recall by fact age (held-out worlds, %)

| Condition                      | 5                 | 10                | 20                | 40                | 80                | 160                |
| ------------------------------ | ----------------- | ----------------- | ----------------- | ----------------- | ----------------- | ------------------ |
| Proposed (dual-tier + barrier) | 96.3 [92.6, 99.1] | 85.2 [78.7, 91.7] | 87.0 [80.6, 92.6] | 89.8 [84.3, 94.4] | 83.3 [75.0, 90.3] | 91.7 [83.3, 100.0] |
| B0 Full history                | 75.0 [67.6, 82.4] | 77.8 [69.4, 85.2] | 78.7 [71.3, 86.1] | 75.0 [65.7, 83.3] | 86.1 [79.2, 93.1] | 88.9 [77.8, 97.2]  |
| B1 Rolling, B                  | 86.1 [79.6, 91.7] | 65.7 [55.6, 75.9] | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]     |
| B1 Rolling, 2B                 | 81.5 [74.1, 88.0] | 78.7 [69.4, 87.0] | 75.0 [65.7, 83.3] | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]     |
| B2 Vector memory               | 85.2 [78.7, 91.7] | 82.4 [75.9, 88.9] | 88.9 [82.4, 94.4] | 80.6 [73.1, 88.0] | 84.7 [75.0, 93.1] | 86.1 [75.0, 94.4]  |
| B3 Generic RAG                 | 72.2 [63.0, 80.6] | 69.4 [60.2, 78.7] | 66.7 [57.4, 75.9] | 68.5 [59.3, 77.8] | 62.5 [50.0, 75.0] | 44.4 [30.6, 58.3]  |
| A1 No long-term memory         | 85.2 [77.8, 91.7] | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]     |
| A2 No short-term buffer        | 86.1 [79.6, 91.7] | 88.0 [82.4, 93.5] | 90.7 [85.2, 95.4] | 91.7 [87.0, 96.3] | 84.7 [76.4, 93.1] | 88.9 [77.8, 97.2]  |
| A3 No scoping                  | 94.4 [89.8, 98.1] | 88.9 [82.4, 94.4] | 82.4 [75.9, 88.9] | 79.6 [71.3, 87.0] | 80.6 [70.8, 90.3] | 88.9 [77.8, 97.2]  |
| A4 No fallback                 | 94.4 [89.8, 98.1] | 85.2 [78.7, 91.7] | 88.0 [81.5, 94.4] | 90.7 [85.2, 95.4] | 84.7 [77.8, 91.7] | 91.7 [83.3, 100.0] |
| n (F4 probes)                  | 108               | 108               | 108               | 108               | 72                | 36                 |

## Table 3: Factorial separation (memory x control, live)

| Cell                  | Recall, live probes (%) | Committed violations per 100 transitions | False rejection (%) | Desync rate (%)   | Sessions |
| --------------------- | ----------------------- | ---------------------------------------- | ------------------- | ----------------- | -------- |
| F1 rolling, direct    | 0.0 [0.0, 0.0]          | 351.2 [302.2, 405.6]                     | n/a                 | 2.7 [1.3, 4.4]    | 14       |
| F2 rolling, barrier   | 0.0 [0.0, 0.0]          | 8.8 [0.0, 22.2]                          | 0.0 [0.0, 0.0]      | 18.5 [15.6, 21.6] | 14       |
| F3 dual-tier, direct  | 41.1 [26.8, 55.4]       | 345.9 [305.3, 390.3]                     | n/a                 | 3.7 [1.8, 5.7]    | 14       |
| F4 dual-tier, barrier | 44.6 [30.4, 59.0]       | 14.0 [4.3, 27.6]                         | 0.0 [0.0, 0.0]      | 18.7 [16.5, 20.9] | 14       |

## Table 4: Ablations

| Ablation                 | Recall, age 20+ (%)                  | MRR@6                | Committed violations per 100 transitions       | Local compute P50 (ms) | Recovery at turn 160 (ms)             | Replay consistency (%)               |
| ------------------------ | ------------------------------------ | -------------------- | ---------------------------------------------- | ---------------------- | ------------------------------------- | ------------------------------------ |
| Full system (F4)         | 87.7 [84.2, 91.0]                    | 0.898 [0.878, 0.917] | probes 9.6 [5.5, 14.1]; live 14.0 [4.2, 27.3]  | 41.1                   | 0.5 (snapshot) vs 145.9 (full replay) | 100.0 [100.0, 100.0]                 |
| A1 No long-term memory   | 0.0 [0.0, 0.0]                       | n/a                  | same as full system (memory-only change)       | n/a                    | n/a                                   | as full system                       |
| A2 No short-term buffer  | 89.5 [85.8, 92.9]                    | 0.898 [0.878, 0.917] | same as full system (memory-only change)       | n/a                    | n/a                                   | as full system                       |
| A3 No scoping            | 81.8 [77.7, 85.9]                    | 0.705 [0.682, 0.727] | same as full system (memory-only change)       | n/a                    | n/a                                   | as full system                       |
| A4 No fallback           | 88.6 [85.5, 91.6]                    | 0.950 [0.934, 0.964] | same as full system (memory-only change)       | n/a                    | n/a                                   | as full system                       |
| A5 No validation barrier | as full system (control-only change) | as full system       | probes 13.1 [9.3, 17.1]; live 11.4 [6.3, 16.5] | 43.3                   | 0.5 (snapshot) vs 145.9 (full replay) | 100.0 [100.0, 100.0]                 |
| A6 No event sourcing     | as full system                       | as full system       | live 351.4 [122.6, 675.0]                      | 10.4                   | no log to recover from                | not replayable                       |
| A7 No snapshots          | as full system                       | as full system       | as full system                                 | n/a                    | 145.9                                 | 100 (full fold, CPU replay sessions) |

## Table 5: Adversarial probes by category

| Category    | n attacks | Attack success, direct writes (%) | Attack success, reducer only A5 (%) | Attack success, barrier (%) | False rejection of lawful twin (%) | Validator gap (%) |
| ----------- | --------- | --------------------------------- | ----------------------------------- | --------------------------- | ---------------------------------- | ----------------- |
| teleport    | 350       | 15.1 [9.1, 21.7]                  | 2.9 [1.1, 4.9]                      | 0.0 [0.0, 0.0]              | 0.0 [0.0, 0.0]                     | 0.4 [0.0, 1.2]    |
| fabrication | 350       | 20.9 [13.1, 29.1]                 | 0.0 [0.0, 0.0]                      | 0.0 [0.0, 0.0]              | 0.0 [0.0, 0.0]                     | 0.0 [0.0, 0.0]    |
| theft       | 350       | 33.4 [24.9, 42.3]                 | 3.1 [1.1, 5.7]                      | 0.0 [0.0, 0.0]              | 0.0 [0.0, 0.0]                     | 0.0 [0.0, 0.0]    |
| trust       | 350       | 0.0 [0.0, 0.0]                    | 0.0 [0.0, 0.0]                      | 0.0 [0.0, 0.0]              | n/a (no lawful proposals)          | n/a               |
| currency    | 350       | 36.9 [28.3, 45.7]                 | 36.9 [28.3, 45.7]                   | 19.7 [12.3, 27.7]           | 0.0 [0.0, 0.0]                     | 51.9 [36.7, 66.4] |
| injection   | 350       | 6.0 [2.6, 10.3]                   | 6.0 [2.6, 10.3]                     | 0.0 [0.0, 0.0]              | n/a (no lawful proposals)          | 0.0 [0.0, 0.0]    |
| secret      | 350       | 0.9 [0.0, 2.3]                    | 0.9 [0.0, 2.3]                      | 0.9 [0.0, 2.3]              | 0.0 [0.0, 0.0]                     | n/a               |
| all         | 2450      | 16.2 [13.6, 18.8]                 | 7.1 [5.3, 9.0]                      | 2.9 [1.8, 4.3]              | 0.0 [0.0, 0.0]                     | 11.0 [6.6, 15.7]  |

## Table 6: Per-stage latency (proposed system, single stream)

| Stage      | P50 (ms) | P95 (ms) | P99 (ms) | n turns |
| ---------- | -------- | -------- | -------- | ------- |
| input      | 0.002    | 0.003    | 0.009    | 24      |
| retrieval  | 0.174    | 0.31     | 0.385    | 24      |
| prompt     | 0.123    | 0.158    | 0.167    | 24      |
| llm        | 0.09     | 0.117    | 0.119    | 24      |
| parse      | 0.087    | 0.118    | 0.125    | 24      |
| validate   | 0.031    | 0.039    | 0.046    | 24      |
| commit     | 18.428   | 21.049   | 30.311   | 24      |
| output     | 0.011    | 0.013    | 0.013    | 24      |
| local      | 24.921   | 27.526   | 37.016   | 24      |
| end to end | 25.006   | 27.609   | 37.127   | 24      |

## Table 7: Per-world and backbone breakdown

| World  | Backbone        | Recall 20+: F4       | Recall 20+: best baseline | Attack success: F4 barrier | Attack success: best baseline (direct) |
| ------ | --------------- | -------------------- | ------------------------- | -------------------------- | -------------------------------------- |
| W1     | K2-Horizon-7B   | 87.0 [75.0, 97.7]    | B2: 87.0 [80.3, 94.2]     | 7.1 [1.4, 14.3]            | B0: 18.6 [10.0, 28.6]                  |
| W2a    | K2-Horizon-7B   | 90.7 [87.1, 95.7]    | B2: 85.2 [80.8, 90.0]     | 2.9 [0.0, 7.1]             | B0: 17.1 [8.6, 25.7]                   |
| W2b    | K2-Horizon-7B   | 92.6 [86.5, 98.1]    | B2: 87.0 [77.8, 94.6]     | 4.3 [0.0, 10.0]            | B0: 8.6 [2.9, 15.7]                    |
| W2c    | K2-Horizon-7B   | 83.3 [75.0, 91.7]    | B2: 87.0 [78.3, 96.3]     | 2.9 [0.0, 7.1]             | B2: 10.0 [4.3, 17.1]                   |
| W3     | K2-Horizon-7B   | 79.6 [71.4, 88.6]    | B2: 74.1 [63.8, 83.9]     | 1.4 [0.0, 4.3]             | B0: 11.4 [4.3, 20.0]                   |
| W4-32  | K2-Horizon-7B   | 87.0 [76.0, 96.4]    | B0: 90.7 [82.6, 96.8]     | 4.3 [0.0, 10.0]            | B0: 15.7 [7.1, 24.3]                   |
| W4-128 | K2-Horizon-7B   | 92.6 [85.7, 100.0]   | B2: 88.9 [81.8, 95.8]     | 2.9 [0.0, 7.1]             | B0: 14.3 [7.1, 22.9]                   |
| W1     | K2-Horizon-3.7B | 100.0 [100.0, 100.0] | B2: 88.9 [66.7, 100.0]    | 0.0 [0.0, 0.0]             | F4: 22.9 [12.9, 32.9]                  |
| W2a    | K2-Horizon-3.7B | 83.3 [66.7, 100.0]   | B2: 72.2 [66.7, 83.3]     | 0.0 [0.0, 0.0]             | F4: 14.3 [7.1, 22.9]                   |
| W3     | K2-Horizon-3.7B | 66.7 [66.7, 66.7]    | B2: 66.7 [50.0, 83.3]     | 0.0 [0.0, 0.0]             | F4: 17.1 [8.6, 25.7]                   |
| W4-32  | K2-Horizon-3.7B | 77.8 [50.0, 100.0]   | B0: 66.7 [50.0, 83.3]     | 0.0 [0.0, 0.0]             | F4: 20.0 [11.4, 30.0]                  |

## Hypothesis verdicts

| hypothesis         | verdict                                                          | evidence                                                                                                                                                                      |
| ------------------ | ---------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| H1 Memory          | not supported (recall) but token-cost condition vs B2/B3 not met | F4 input tokens 1399 vs B2 1102, B3 1209                                                                                                                                      |
| H2 Retrieval       | supported                                                        | per-probe reciprocal rank, Wilcoxon                                                                                                                                           |
| H3 State control   | supported                                                        | probes McNemar + live Wilcoxon                                                                                                                                                |
| H4 Cost of control | supported                                                        | false rejection 0.0 [0.0, 0.0]%; validate P95 0.039 ms                                                                                                                        |
| H5 Replay          | supported                                                        | live event-sourced sessions all consistent: True; CPU replay (full, snapshot, restart) all consistent: True; backend load path after crash consistent in 0% (see limitations) |
| H6 Separability    | not supported                                                    | memory->recall coef 3.57 (p=6.08e-68); control->violation coef -6.77 (p=1.01e-109); interaction p recall=4.91e-05, violation=0.689                                            |
| H7 Generalisation  | supported                                                        | W2 LIGHT-derived: dRecall=+0.889, dAttack=+0.114; W3 held-out genre: dRecall=+0.796, dAttack=+0.086; W4 procedural: dRecall=+0.898, dAttack=+0.121                            |

## Confirmatory tests

| hypothesis | test                                                            | n   | effect | p_raw  | direction_ok | p_holm |
| ---------- | --------------------------------------------------------------- | --- | ------ | ------ | ------------ | ------ |
| H1         | recall 20+ F4 vs B1 (McNemar)                                   | 324 | 0.8765 | 0.0    | True         | 0.0    |
| H1         | recall 20+ F4 vs B2 (McNemar)                                   | 324 | 0.0278 | 0.2976 | True         | 0.2976 |
| H1         | recall 20+ F4 vs B3 (McNemar)                                   | 324 | 0.2377 | 0.0    | True         | 0.0    |
| H2         | MRR@6 F4 vs B2 (Wilcoxon, per probe)                            | 540 | 0.1482 | 0.0    | True         | 0.0    |
| H3         | attack success direct vs barrier, F4 context (McNemar)          | 490 | 0.1143 | 0.0    | True         | 0.0    |
| H3         | live violations per transition F3 vs F4 (Wilcoxon, per session) | 14  | 3.4586 | 0.001  | True         | 0.0019 |

## Limitations of this run

- W3 authorship: notebook author (not independent; see caveat). The article requires an independent author; attach w3_world_seed.json to satisfy it.
- Recall, leaks and desynchronisation are scored automatically (key-word match, secret keywords, refusal/arrival cues). Blinded sheets for two human raters are in annotation/; Cohen's kappa and judge agreement need those labels.
- Token cost is reported in tokens only; the models are self-hosted, so no provider list price applies.
- Latency was measured on 2x T4 with vLLM; the article's hosted-endpoint latency is not reproduced.
- Backend recovery defect: SessionManager.load_session (manager.py:171-177) loads the snapshot only and ignores logged events after it. After a crash between commit and auto-save it was consistent in 0% of CPU replay sessions (mean 8.0 turns lost); snapshot plus event suffix was consistent in 100%.
- Backend parse defect at the pinned commit: GroqClient.extract_json can return a bare JSON string or list, which node_json_parsing does not handle. Such outputs count as JSON parse failures in recall and probes; in live sessions the node raised on 3 of 3276 turns, which were recorded as failed turns that commit nothing.
- active_npc_id is set outside the event log (process_action) and is excluded from replay hashes.
- The prompt advertises trust deltas of -10..10 while the validator allows +/-20; the oracle uses the article's +/-20 bound.
- Live sessions address scripted NPCs even when a scripted move was not committed; this divergence is measured as desynchronisation.
- B4 (scripted FSM) and B5 (MemGPT-style memory) were not run.
- Sample size: ladder level 2 of 7 ({'n_rec': 3, 'n_probe': 10, 'n_live': 2}), chosen by the time-budget planner; the article's full targets correspond to level 7.
- Second backbone: run on ['W1', 'W2a', 'W3', 'W4-32'].
