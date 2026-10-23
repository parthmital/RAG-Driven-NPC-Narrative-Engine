# Results: Memory and State Control for LLM-Driven NPC Dialogue

Generated 2026-10-22T23:51:16Z from backend bundle `9f7d7e7bbb0d`, ladder level 1, backbone IFM/K2-Horizon-7B (fp16, vLLM 0.30.0, reasoning effort low, thinking budget 192 tokens). Values: mean [95% cluster-bootstrap CI]; held-out = W2a to W4-128.

## Table 1: Main comparison (held-out worlds)

| Condition                                   | Recall, age 20+ (%) | Committed violations per 100 transitions | Probe attack success (%) | MRR@6                | P50 / P95 latency (ms) | Input tokens per turn | Replay consistency (%)        |
| ------------------------------------------- | ------------------- | ---------------------------------------- | ------------------------ | -------------------- | ---------------------- | --------------------- | ----------------------------- |
| Proposed (dual-tier + barrier)              | 82.4 [78.0, 86.8]   | 0.0 [0.0, 0.0]                           | 0.8 [0.0, 2.0]           | 0.721 [0.704, 0.737] | 6635 / 8157            | 1445                  | 100.0 [100.0, 100.0]          |
| Proposed before revision (Review-02)        | 85.6 [81.4, 90.0]   | 3.0 [0.0, 7.7]                           | 1.6 [0.4, 3.2]           | 0.890 [0.866, 0.914] | 6926 / 8586            | 1400                  | not replayable (no event log) |
| B0 Full history                             | 76.4 [70.8, 81.8]   | 24.7 [15.3, 34.8]                        | 4.4 [2.0, 7.1]           | n/a                  | 10950 / 24932          | 4414                  | not replayable (no event log) |
| B1 Rolling, B                               | 0.0 [0.0, 0.0]      | 24.7 [15.3, 34.7]                        | 4.4 [2.0, 7.1]           | n/a                  | 6767 / 7712            | 1478                  | not replayable (no event log) |
| B1 Rolling, 2B                              | 19.4 [14.4, 25.0]   | n/a (no probe context)                   | n/a                      | n/a                  | 6970 / 8871            | 1876                  | not replayable (no event log) |
| B2 Vector memory                            | 80.6 [74.1, 86.8]   | 22.6 [14.4, 31.2]                        | 4.4 [2.0, 7.1]           | 0.745 [0.720, 0.771] | 6083 / 10135           | 1451                  | not replayable (no event log) |
| B3 Generic RAG                              | 59.3 [52.6, 65.3]   | 35.9 [26.7, 45.4]                        | 5.2 [2.8, 7.9]           | 0.706 [0.678, 0.734] | 6103 / 13004           | 1506                  | not replayable (no event log) |
| B4 Scored memory stream (Generative Agents) | 63.0 [57.3, 68.7]   | n/a (no probe context)                   | n/a                      | 0.618 [0.585, 0.649] | nan / nan              | 1449                  | not replayable (no event log) |
| B5 Forgetting-curve memory (MemoryBank)     | 77.8 [72.2, 83.3]   | n/a (no probe context)                   | n/a                      | 0.735 [0.704, 0.765] | nan / nan              | 1450                  | not replayable (no event log) |

## Table 2: Recall by fact age (held-out worlds, %)

| Condition                                   | 5                  | 10                | 20                | 40                | 80                | 160                |
| ------------------------------------------- | ------------------ | ----------------- | ----------------- | ----------------- | ----------------- | ------------------ |
| Proposed (dual-tier + barrier)              | 80.6 [70.8, 88.9]  | 81.9 [72.2, 90.3] | 83.3 [73.6, 91.7] | 79.2 [69.4, 87.5] | 81.2 [68.8, 91.7] | 91.7 [79.2, 100.0] |
| Proposed before revision (Review-02)        | 97.2 [93.1, 100.0] | 91.7 [84.7, 97.2] | 83.3 [73.6, 91.7] | 86.1 [77.8, 93.1] | 83.3 [72.9, 91.7] | 95.8 [87.5, 100.0] |
| B0 Full history                             | 81.9 [72.2, 90.3]  | 77.8 [68.1, 86.1] | 79.2 [69.4, 87.5] | 69.4 [59.7, 79.2] | 77.1 [64.6, 87.5] | 87.5 [75.0, 100.0] |
| B1 Rolling, B                               | 80.6 [70.8, 90.3]  | 63.9 [51.4, 76.4] | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]     |
| B1 Rolling, 2B                              | 79.2 [69.4, 87.5]  | 75.0 [65.3, 83.3] | 58.3 [45.8, 70.8] | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]     |
| B2 Vector memory                            | 83.3 [75.0, 90.3]  | 87.5 [79.2, 94.4] | 81.9 [73.6, 90.3] | 77.8 [68.1, 86.1] | 77.1 [64.6, 89.6] | 91.7 [79.2, 100.0] |
| B3 Generic RAG                              | 69.4 [59.7, 79.2]  | 63.9 [52.8, 75.0] | 59.7 [48.6, 70.8] | 56.9 [45.8, 68.1] | 60.4 [47.9, 72.9] | 62.5 [45.8, 79.2]  |
| B4 Scored memory stream (Generative Agents) | 86.1 [79.1, 93.1]  | 86.1 [77.8, 93.1] | 83.3 [75.0, 91.7] | 70.8 [62.5, 79.2] | 35.4 [22.9, 47.9] | 33.3 [16.7, 50.0]  |
| B5 Forgetting-curve memory (MemoryBank)     | 90.3 [83.3, 95.8]  | 86.1 [77.8, 93.1] | 80.6 [72.2, 88.9] | 77.8 [68.1, 86.1] | 68.8 [54.2, 81.2] | 87.5 [75.0, 100.0] |
| A1 No long-term memory                      | 87.5 [80.6, 94.4]  | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]     |
| A2 No short-term buffer                     | 87.5 [80.6, 94.4]  | 87.5 [80.6, 94.4] | 84.7 [76.4, 91.7] | 84.7 [76.4, 93.1] | 81.2 [70.8, 89.6] | 87.5 [75.0, 100.0] |
| A3 No scoping                               | 70.8 [61.1, 80.6]  | 84.7 [76.4, 91.7] | 86.1 [76.4, 94.4] | 72.2 [62.5, 81.9] | 79.2 [66.7, 89.6] | 87.5 [75.0, 100.0] |
| A4 No fallback                              | 86.1 [77.8, 93.1]  | 80.6 [70.8, 90.3] | 83.3 [73.6, 91.7] | 79.2 [69.4, 87.5] | 81.2 [68.8, 93.8] | 91.7 [79.2, 100.0] |
| n (F4 probes)                               | 72                 | 72                | 72                | 72                | 48                | 24                 |

## Table 3: Factorial separation (memory x control, live)

| Cell                  | Recall, live probes (%) | Committed violations per 100 transitions | False rejection (%) | Desync rate (%)  | Sessions |
| --------------------- | ----------------------- | ---------------------------------------- | ------------------- | ---------------- | -------- |
| F1 rolling, direct    | 0.0 [0.0, 0.0]          | 545.9 [474.4, 634.5]                     | n/a                 | 3.3 [1.5, 5.9]   | 7        |
| F2 rolling, barrier   | 0.0 [0.0, 0.0]          | 0.0 [0.0, 0.0]                           | 0.0 [0.0, 0.0]      | 12.1 [9.5, 14.3] | 7        |
| F3 dual-tier, direct  | 32.1 [14.3, 50.0]       | 423.9 [313.2, 566.7]                     | n/a                 | 2.6 [1.5, 3.7]   | 7        |
| F4 dual-tier, barrier | 39.3 [17.9, 60.7]       | 0.0 [0.0, 0.0]                           | 1.2 [0.0, 4.1]      | 9.5 [6.6, 12.5]  | 7        |

## Table 3b: Simple effects and interaction contrast (live, per session, pp)

| outcome   | contrast                            | n_sessions              | effect                 | p_wilcoxon              |
| --------- | ----------------------------------- | ----------------------- | ---------------------- | ----------------------- |
| recall    | memory effect                       | direct writes (F3 - F1) | 7                      | +32.1 [+14.3, +50.0]    | 0.0625   |
| recall    | memory effect                       | barrier (F4 - F2)       | 7                      | +39.3 [+17.9, +60.7]    | 0.0625   |
| recall    | control effect                      | rolling (F2 - F1)       | 7                      | +0.0 [+0.0, +0.0]       | 1.0      |
| recall    | control effect                      | dual-tier (F4 - F3)     | 7                      | +7.1 [-25.0, +42.9]     | 1.0      |
| recall    | interaction ((F4 - F2) - (F3 - F1)) | 7                       | +7.1 [-25.0, +42.9]    | 1.0                     |
| violation | memory effect                       | direct writes (F3 - F1) | 7                      | -107.4 [-209.1, +13.0]  | 0.1875   |
| violation | memory effect                       | barrier (F4 - F2)       | 7                      | +0.0 [+0.0, +0.0]       | 1.0      |
| violation | control effect                      | rolling (F2 - F1)       | 7                      | -529.9 [-625.6, -432.1] | 0.015625 |
| violation | control effect                      | dual-tier (F4 - F3)     | 7                      | -422.5 [-583.3, -250.6] | 0.03125  |
| violation | interaction ((F4 - F2) - (F3 - F1)) | 7                       | +107.4 [-13.2, +209.3] | 0.1875                  |

## Table 4: Ablations

| Ablation                 | Recall, age 20+ (%)                  | MRR@6                | Committed violations per 100 transitions   | Local compute P50 (ms) | Recovery at turn 160 (ms)             | Replay consistency (%)               |
| ------------------------ | ------------------------------------ | -------------------- | ------------------------------------------ | ---------------------- | ------------------------------------- | ------------------------------------ |
| Full system (F4)         | 82.4 [78.0, 86.8]                    | 0.721 [0.704, 0.737] | probes 0.0 [0.0, 0.0]; live 0.0 [0.0, 0.0] | 26.2                   | 1.7 (snapshot) vs 290.1 (full replay) | 100.0 [100.0, 100.0]                 |
| A1 No long-term memory   | 0.0 [0.0, 0.0]                       | n/a                  | same as full system (memory-only change)   | n/a                    | n/a                                   | as full system                       |
| A2 No short-term buffer  | 84.3 [80.3, 88.4]                    | 0.890 [0.867, 0.914] | same as full system (memory-only change)   | n/a                    | n/a                                   | as full system                       |
| A3 No scoping            | 80.1 [75.7, 84.4]                    | 0.579 [0.554, 0.604] | same as full system (memory-only change)   | n/a                    | n/a                                   | as full system                       |
| A4 No fallback           | 82.4 [77.9, 86.8]                    | 0.758 [0.744, 0.773] | same as full system (memory-only change)   | n/a                    | n/a                                   | as full system                       |
| A5 No validation barrier | as full system (control-only change) | as full system       | probes 5.4 [1.8, 9.6]; live 4.7 [0.0, 9.8] | 25.6                   | 1.7 (snapshot) vs 290.1 (full replay) | 100.0 [100.0, 100.0]                 |
| A6 No event sourcing     | as full system                       | as full system       | live 0.0 [0.0, 0.0]                        | 12.7                   | no log to recover from                | not replayable                       |
| A7 No snapshots          | as full system                       | as full system       | as full system                             | n/a                    | 290.1                                 | 100 (full fold, CPU replay sessions) |

## Table 5: Adversarial probes by category

| Category    | n attacks | Attack success, direct writes (%) | Attack success, reducer only A5 (%) | Attack success, barrier v1 (%) | Attack success, barrier v2 (%) | False rejection of lawful twin (%) | Validator gap v1 (%) | Validator gap v2 (%) |
| ----------- | --------- | --------------------------------- | ----------------------------------- | ------------------------------ | ------------------------------ | ---------------------------------- | -------------------- | -------------------- |
| teleport    | 210       | 13.3 [6.2, 21.4]                  | 0.0 [0.0, 0.0]                      | 0.0 [0.0, 0.0]                 | 0.0 [0.0, 0.0]                 | 0.0 [0.0, 0.0]                     | 9.2 [0.0, 20.3]      | 0.0 [0.0, 0.0]       |
| fabrication | 210       | 5.7 [1.4, 11.0]                   | 0.0 [0.0, 0.0]                      | 0.0 [0.0, 0.0]                 | 0.0 [0.0, 0.0]                 | 0.0 [0.0, 0.0]                     | 7.7 [0.0, 30.8]      | 0.0 [0.0, 0.0]       |
| theft       | 210       | 13.8 [6.7, 21.9]                  | 1.4 [0.0, 4.3]                      | 0.0 [0.0, 0.0]                 | 0.0 [0.0, 0.0]                 | 0.0 [0.0, 0.0]                     | 0.0 [0.0, 0.0]       | 0.0 [0.0, 0.0]       |
| trust       | 210       | 0.0 [0.0, 0.0]                    | 0.0 [0.0, 0.0]                      | 0.0 [0.0, 0.0]                 | 0.0 [0.0, 0.0]                 | 0.0 [0.0, 0.0]                     | 0.0 [0.0, 0.0]       | 0.0 [0.0, 0.0]       |
| currency    | 210       | 12.4 [4.3, 21.4]                  | 12.4 [4.3, 21.9]                    | 8.1 [1.9, 15.7]                | 0.0 [0.0, 0.0]                 | 1.5 [0.0, 5.3]                     | 58.6 [24.1, 100.0]   | 0.0 [0.0, 0.0]       |
| injection   | 210       | 0.0 [0.0, 0.0]                    | 0.0 [0.0, 0.0]                      | 0.0 [0.0, 0.0]                 | 0.0 [0.0, 0.0]                 | n/a (no lawful proposals)          | n/a                  | n/a                  |
| secret      | 210       | 2.9 [0.0, 7.1]                    | 2.9 [0.0, 7.1]                      | 2.9 [0.0, 7.1]                 | 2.9 [0.0, 7.1]                 | 0.0 [0.0, 0.0]                     | 100.0 [100.0, 100.0] | 0.0 [0.0, 0.0]       |
| all         | 1470      | 6.9 [4.7, 9.3]                    | 2.4 [1.0, 4.0]                      | 1.6 [0.5, 2.9]                 | 0.4 [0.0, 1.0]                 | 0.2 [0.0, 0.8]                     | 15.2 [6.7, 24.9]     | 0.0 [0.0, 0.0]       |

## Table 6: Per-stage latency (proposed system, single stream)

| Stage      | P50 (ms) | P95 (ms) | P99 (ms) | n turns |
| ---------- | -------- | -------- | -------- | ------- |
| input      | 0.002    | 0.002    | 0.003    | 24      |
| retrieval  | 0.121    | 0.158    | 0.172    | 24      |
| prompt     | 0.114    | 0.154    | 0.163    | 24      |
| llm        | 0.068    | 0.096    | 6240.346 | 24      |
| parse      | 0.061    | 0.075    | 0.076    | 24      |
| validate   | 0.009    | 1.604    | 1.77     | 24      |
| commit     | 8.088    | 12.649   | 13.251   | 24      |
| output     | 0.008    | 0.016    | 0.017    | 24      |
| local      | 14.765   | 20.147   | 20.738   | 24      |
| end to end | 15.656   | 20.89    | 6255.737 | 24      |

## Table 7: Per-world and backbone breakdown

| World  | Backbone        | Recall 20+: F4       | Recall 20+: best baseline | Attack success: F4 barrier | Attack success: best baseline (direct) |
| ------ | --------------- | -------------------- | ------------------------- | -------------------------- | -------------------------------------- |
| W1     | K2-Horizon-7B   | 86.1 [77.5, 96.9]    | B2: 86.1 [77.5, 96.9]     | 0.0 [0.0, 0.0]             | B0: 19.0 [7.1, 31.0]                   |
| W2a    | K2-Horizon-7B   | 86.1 [80.0, 93.3]    | B2: 80.6 [64.7, 97.1]     | 0.0 [0.0, 0.0]             | B3: 0.0 [0.0, 0.0]                     |
| W2b    | K2-Horizon-7B   | 91.7 [84.4, 97.6]    | B5: 80.6 [70.0, 91.7]     | 0.0 [0.0, 0.0]             | B0: 4.8 [0.0, 11.9]                    |
| W2c    | K2-Horizon-7B   | 83.3 [77.3, 92.9]    | B2: 80.6 [57.9, 97.4]     | 0.0 [0.0, 0.0]             | B2: 0.0 [0.0, 0.0]                     |
| W3     | K2-Horizon-7B   | 69.4 [53.6, 77.8]    | B0: 80.6 [65.9, 94.4]     | 0.0 [0.0, 0.0]             | B2: 0.0 [0.0, 0.0]                     |
| W4-32  | K2-Horizon-7B   | 80.6 [66.7, 94.4]    | B2: 88.9 [80.0, 97.4]     | 0.0 [0.0, 0.0]             | B0: 0.0 [0.0, 0.0]                     |
| W4-128 | K2-Horizon-7B   | 83.3 [73.7, 93.8]    | B5: 88.9 [77.8, 97.6]     | 4.8 [0.0, 11.9]            | B0: 4.8 [0.0, 11.9]                    |
| W1     | K2-Horizon-3.7B | 83.3 [83.3, 83.3]    | B2: 91.7 [83.3, 100.0]    | 0.0 [0.0, 0.0]             | F4: 14.3 [4.8, 26.2]                   |
| W2a    | K2-Horizon-3.7B | 83.3 [83.3, 83.3]    | B5: 75.0 [66.7, 83.3]     | 0.0 [0.0, 0.0]             | F4: 14.3 [4.8, 26.2]                   |
| W3     | K2-Horizon-3.7B | 75.0 [66.7, 83.3]    | B2: 66.7 [66.7, 66.7]     | 0.0 [0.0, 0.0]             | F4: 11.9 [2.4, 21.4]                   |
| W4-32  | K2-Horizon-3.7B | 91.7 [83.3, 100.0]   | B5: 91.7 [83.3, 100.0]    | 0.0 [0.0, 0.0]             | F4: 16.7 [7.1, 28.6]                   |
| W1     | qwen2.5-7b      | 100.0 [100.0, 100.0] | B5: 100.0 [100.0, 100.0]  | 0.0 [0.0, 0.0]             | F4: 59.5 [45.2, 73.8]                  |
| W2a    | qwen2.5-7b      | 100.0 [100.0, 100.0] | B2: 83.3 [66.7, 100.0]    | 0.0 [0.0, 0.0]             | F4: 45.2 [31.0, 59.5]                  |
| W3     | qwen2.5-7b      | 83.3 [83.3, 83.3]    | B2: 91.7 [83.3, 100.0]    | 0.0 [0.0, 0.0]             | F4: 40.5 [26.2, 54.8]                  |
| W4-32  | qwen2.5-7b      | 91.7 [83.3, 100.0]   | B2: 91.7 [83.3, 100.0]    | 2.4 [0.0, 7.1]             | F4: 33.3 [19.0, 47.6]                  |
| W1     | phi4-mini       | 91.7 [83.3, 100.0]   | B4: 75.0 [50.0, 100.0]    | 0.0 [0.0, 0.0]             | F4: 21.4 [9.5, 33.3]                   |
| W2a    | phi4-mini       | 75.0 [50.0, 100.0]   | B2: 75.0 [66.7, 83.3]     | 0.0 [0.0, 0.0]             | F4: 19.0 [7.1, 31.0]                   |
| W3     | phi4-mini       | 75.0 [50.0, 100.0]   | B5: 83.3 [66.7, 100.0]    | 0.0 [0.0, 0.0]             | F4: 31.0 [16.7, 45.2]                  |
| W4-32  | phi4-mini       | 91.7 [83.3, 100.0]   | B2: 83.3 [66.7, 100.0]    | 0.0 [0.0, 0.0]             | F4: 23.8 [11.9, 38.1]                  |

## Table 8: Before and after the Review-03 corrections (paired, same oracle)

| test | metric                                                             | before                 | after                 | n     | effect_pp | p_raw                  | p_holm                 |
| ---- | ------------------------------------------------------------------ | ---------------------- | --------------------- | ----- | --------- | ---------------------- | ---------------------- |
| R1   | attack success, all categories                                     | 2.0 [0.7, 3.7]         | 0.7 [0.0, 1.7]        | 294.0 | 1.36      | 0.125                  | 0.75                   |
| R1   | attack success, currency                                           | 9.5 [2.4, 19.0]        | 0.0 [0.0, 0.0]        | 42.0  | 9.52      | 0.125                  | 0.75                   |
| R1   | validator gap, currency proposals                                  | 58.6 [23.5, 100.0]     | 0.0 [0.0, 0.0]        |       |           |                        |                        |
| R1   | validator gap, all proposals                                       | 15.2 [6.8, 24.9]       | 0.0 [0.0, 0.0]        |       |           |                        |                        |
| R1   | false rejection of lawful twins                                    | 0.2 [0.0, 0.8]         | 0.2 [0.0, 0.8]        |       |           |                        |                        |
| R2   | crash trials recovered inconsistently                              | 74.3% (5.6 turns lost) | 0.0% (0.0 turns lost) | 300.0 | 74.33     | 1.4836824602749686e-67 | 1.3353142142474717e-66 |
| R2   | load path after a crash (replay sessions)                          | 0% consistent          | 100% consistent       |       |           |                        |                        |
| R3   | judge contradiction, repaired probes                               | 35.5%                  | 35.5%                 | 31.0  | 0.0       | 1.0                    | 1.0                    |
| R3   | judge contradiction, repaired live F4 turns                        | 40.0%                  | 45.0%                 | 20.0  | -5.0      | 1.0                    | 1.0                    |
| R3   | judge contradiction per judged live turn, F4v1 vs F4 (per session) | 51.0%                  | 20.8%                 | 7.0   | 28.37     | 0.015625               | 0.125                  |
| R3   | desync proxy, live F4 turns (draft vs repaired)                    | 9.5%                   | 9.5%                  | 273.0 | 0.0       | 1.0                    | 1.0                    |
| R3   | desync proxy per live turn, F4v1 vs F4 (per session)               | 17.2 [13.6, 20.9]      | 9.5 [6.6, 12.8]       | 7.0   | 7.69      | 0.015625               | 0.125                  |
| R4   | committed violations per 100 transitions, F4v1 vs F4 (per session) | 0.0 [0.0, 0.0]         | 0.0 [0.0, 0.0]        | 7.0   | 0.0       | 1.0                    | 1.0                    |

## Hypothesis verdicts

| hypothesis              | verdict                                     | evidence                                                                                                                                                                                                                                                    |
| ----------------------- | ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| H1 Memory               | not supported                               | F4 input tokens 1445 vs B2 1451, B3 1506                                                                                                                                                                                                                    |
| H2 Retrieval            | not supported                               | per-probe reciprocal rank, Wilcoxon                                                                                                                                                                                                                         |
| H3 State control        | not supported                               | probes McNemar + live Wilcoxon                                                                                                                                                                                                                              |
| H4 Cost of control      | supported                                   | false rejection 1.2 [0.0, 4.2]%; validate P95 1.604 ms                                                                                                                                                                                                      |
| H5 Replay               | supported                                   | live event-sourced sessions all consistent: True; CPU replay, restart, backend load path after a crash and 300 randomised crash trials all consistent: True                                                                                                 |
| H6 Separability         | not supported                               | memory->recall coef 2.57 (p=2.19e-18); control->violation coef -7.48 (p=2.7e-27); interaction p recall=0.00486, violation=0.147                                                                                                                             |
| H7 Generalisation       | not supported                               | W2 LIGHT-derived: dRecall=+0.870, dAttack=+0.063; W3 held-out genre: dRecall=+0.694, dAttack=+0.024; W4 procedural: dRecall=+0.819, dAttack=+0.000; backbone qwen2.5-7b: dRecall=+0.938, dAttack=+0.440; backbone phi4-mini: dRecall=+0.833, dAttack=+0.238 |
| R1 Currency invariant   | confirmed (no failure after the correction) | v2 currency validator gap 0.0 [0.0, 0.0]%                                                                                                                                                                                                                   |
| R2 Snapshot recovery    | confirmed (no failure after the correction) | 300/300 crash trials consistent after the correction                                                                                                                                                                                                        |
| R3 Dialogue repair      | not confirmed                               | draft vs repaired (judge, proxy) and F4v1 vs F4                                                                                                                                                                                                             |
| R4 Committed violations | not confirmed                               | F4v1 vs F4, live, per session                                                                                                                                                                                                                               |

## Confirmatory tests

| hypothesis | test                                                            | n   | effect | p_raw  | direction_ok | p_holm |
| ---------- | --------------------------------------------------------------- | --- | ------ | ------ | ------------ | ------ |
| H1         | recall 20+ F4 vs B1 (McNemar)                                   | 216 | 0.8241 | 0.0    | True         | 0.0    |
| H1         | recall 20+ F4 vs B2 (McNemar)                                   | 216 | 0.0185 | 0.6177 | True         | 1.0    |
| H1         | recall 20+ F4 vs B3 (McNemar)                                   | 216 | 0.2315 | 0.0    | True         | 0.0    |
| H2         | MRR@6 F4 vs B2 (Wilcoxon, per probe)                            | 360 | -0.024 | 0.6745 | False        | 1.0    |
| H3         | attack success direct vs barrier, F4 context (McNemar)          | 294 | 0.0578 | 0.0    | True         | 0.0001 |
| H3         | live violations per transition F3 vs F4 (Wilcoxon, per session) | 7   | 4.2252 | 0.0312 | True         | 0.0938 |

## Exploratory memory tests

| test                            | n   | effect  | p_raw  | p_holm |
| ------------------------------- | --- | ------- | ------ | ------ |
| recall 20+ F4 vs B4 (McNemar)   | 216 | 0.1944  | 0.0    | 0.0    |
| recall 20+ F4 vs B5 (McNemar)   | 216 | 0.0463  | 0.1641 | 0.3283 |
| recall 20+ F4 vs F4v1 (McNemar) | 216 | -0.0324 | 0.2478 | 0.3283 |

## Limitations of this run

- W3 authorship: notebook author (not independent; see caveat). The article requires an independent author; attach w3_world_seed.json to satisfy it.
- Recall, leaks and the desync proxy are scored automatically (key-word match, secret keywords, refusal/arrival cues); the judge (qwen2.5-7b: 181 items judged) is an LLM. Human evaluation: pending (no human_ratings_*.csv attached).
- Token cost is reported in tokens only; the models are self-hosted, so no provider list price applies.
- Latency was measured on 2x T4 with vLLM; hosted-endpoint latency is not reproduced.
- F4v1 reuses the corrected reducer, event store and commit node; it differs from F4 in the validator, the prompt builder, the unbudgeted memory assembly and the absence of dialogue repair, which are the components Review-03 changed.
- Live sessions address scripted NPCs even when a scripted move was not committed; this divergence is measured as desynchronisation.
- B4 omits the Generative Agents importance score (an LLM call per memory write); B4 and B5 are re-implementations of the retrieval rules, not the original systems.
- Sample size: ladder level 1 of 7 ({'n_rec': 2, 'n_probe': 6, 'n_live': 1}); the article's full targets correspond to level 7. Attach this run's llm_cache_*.jsonl and rerun to reach a larger level.
- Second backbone: run on ['W1', 'W2a', 'W3', 'W4-32']. Independent families: {'qwen2.5-7b': "run on ['W1', 'W2a', 'W3', 'W4-32'] (horizon 100)", 'phi4-mini': "run on ['W1', 'W2a', 'W3', 'W4-32'] (horizon 100)"}.
