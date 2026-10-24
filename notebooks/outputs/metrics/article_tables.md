# Results: Memory and State Control for LLM-Driven NPC Dialogue

Generated 2026-10-24T15:50:54Z from backend bundle `9f7d7e7bbb0d`, ladder level 1, backbone IFM/K2-Horizon-7B (fp16, vLLM 0.30.0, reasoning effort low, thinking budget 192 tokens). Values: mean [95% cluster-bootstrap CI]; held-out = W2a to W4-128.

## Table 1: Main comparison (held-out worlds)

| Condition                                   | Recall, age 20+ (%) | Committed violations per 100 transitions | Probe attack success (%) | MRR@6                | P50 / P95 latency (ms) | Input tokens per turn | Replay consistency (%)        |
| ------------------------------------------- | ------------------- | ---------------------------------------- | ------------------------ | -------------------- | ---------------------- | --------------------- | ----------------------------- |
| Proposed (dual-tier + barrier)              | 82.4 [78.0, 86.8]   | 0.0 [0.0, 0.0]                           | 0.0 [0.0, 0.0]           | 0.901 [0.878, 0.925] | 7147 / 8699            | 1445                  | 100.0 [100.0, 100.0]          |
| Proposed before revision (Review-02)        | 84.7 [80.2, 89.1]   | 2.7 [0.0, 6.9]                           | 0.8 [0.0, 2.0]           | 0.875 [0.849, 0.902] | 7374 / 9139            | 1400                  | not replayable (no event log) |
| B0 Full history                             | 78.2 [72.8, 83.5]   | 20.0 [11.8, 29.2]                        | 2.8 [0.8, 5.2]           | n/a                  | 11181 / 25306          | 4414                  | not replayable (no event log) |
| B1 Rolling, B                               | 0.0 [0.0, 0.0]      | 20.0 [11.8, 29.2]                        | 2.8 [0.8, 5.2]           | n/a                  | 7137 / 8177            | 1478                  | not replayable (no event log) |
| B1 Rolling, 2B                              | 19.0 [14.2, 24.1]   | n/a (no probe context)                   | n/a                      | n/a                  | 7284 / 9361            | 1876                  | not replayable (no event log) |
| B2 Vector memory                            | 81.0 [74.3, 87.2]   | 21.2 [13.9, 29.1]                        | 4.8 [2.4, 7.5]           | 0.727 [0.700, 0.755] | 6556 / 10870           | 1451                  | not replayable (no event log) |
| B3 Generic RAG                              | 58.8 [52.3, 64.8]   | 36.1 [27.1, 45.7]                        | 5.2 [2.8, 7.9]           | 0.692 [0.659, 0.727] | 6317 / 10500           | 1506                  | not replayable (no event log) |
| B4 Scored memory stream (Generative Agents) | 61.1 [55.4, 67.2]   | n/a (no probe context)                   | n/a                      | 0.563 [0.526, 0.600] | 6611 / 11825           | 1449                  | not replayable (no event log) |
| B5 Forgetting-curve memory (MemoryBank)     | 78.7 [73.3, 84.1]   | n/a (no probe context)                   | n/a                      | 0.710 [0.677, 0.742] | 6737 / 23344           | 1450                  | not replayable (no event log) |

## Table 2: Recall by fact age (held-out worlds, %)

| Condition                                   | 5                  | 10                | 20                | 40                | 80                | 160                |
| ------------------------------------------- | ------------------ | ----------------- | ----------------- | ----------------- | ----------------- | ------------------ |
| Proposed (dual-tier + barrier)              | 81.9 [73.6, 90.3]  | 80.6 [70.8, 90.3] | 83.3 [75.0, 91.7] | 79.2 [69.4, 87.5] | 81.2 [68.8, 93.8] | 91.7 [79.2, 100.0] |
| Proposed before revision (Review-02)        | 95.8 [90.3, 100.0] | 90.3 [81.9, 97.2] | 81.9 [72.2, 90.3] | 86.1 [79.2, 93.1] | 81.2 [70.8, 89.6] | 95.8 [87.5, 100.0] |
| B0 Full history                             | 77.8 [66.7, 87.5]  | 77.8 [69.4, 86.1] | 81.9 [72.2, 90.3] | 72.2 [62.5, 81.9] | 79.2 [66.7, 89.6] | 83.3 [70.8, 95.8]  |
| B1 Rolling, B                               | 79.2 [69.4, 88.9]  | 63.9 [51.4, 76.4] | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]     |
| B1 Rolling, 2B                              | 80.6 [72.2, 88.9]  | 73.6 [63.9, 81.9] | 56.9 [44.4, 69.4] | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]     |
| B2 Vector memory                            | 86.1 [77.8, 93.1]  | 87.5 [79.2, 94.4] | 81.9 [72.2, 90.3] | 79.2 [69.4, 88.9] | 77.1 [64.6, 89.6] | 91.7 [79.2, 100.0] |
| B3 Generic RAG                              | 69.4 [59.7, 79.2]  | 65.3 [54.2, 76.4] | 59.7 [48.6, 70.8] | 56.9 [45.8, 68.1] | 58.3 [45.8, 70.8] | 62.5 [45.8, 79.2]  |
| B4 Scored memory stream (Generative Agents) | 87.5 [80.6, 94.4]  | 83.3 [73.6, 91.7] | 81.9 [72.2, 90.3] | 68.1 [58.3, 77.8] | 35.4 [22.9, 47.9] | 29.2 [12.5, 45.8]  |
| B5 Forgetting-curve memory (MemoryBank)     | 90.3 [83.3, 95.8]  | 88.9 [80.6, 95.8] | 81.9 [73.6, 88.9] | 80.6 [72.2, 88.9] | 66.7 [52.1, 79.2] | 87.5 [75.0, 100.0] |
| A1 No long-term memory                      | 88.9 [81.9, 95.8]  | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]     |
| A2 No short-term buffer                     | 86.1 [77.8, 93.1]  | 88.9 [81.9, 95.8] | 84.7 [76.4, 91.7] | 84.7 [75.0, 93.1] | 81.2 [70.8, 89.6] | 87.5 [75.0, 100.0] |
| A3 No scoping                               | 72.2 [62.5, 81.9]  | 84.7 [76.4, 91.7] | 86.1 [76.4, 94.4] | 72.2 [62.5, 81.9] | 77.1 [64.6, 87.5] | 87.5 [75.0, 100.0] |
| A4 No fallback                              | 87.5 [80.6, 94.4]  | 79.2 [69.4, 88.9] | 83.3 [75.0, 91.7] | 79.2 [69.4, 87.5] | 81.2 [68.8, 93.8] | 91.7 [79.2, 100.0] |
| n (F4 probes)                               | 72                 | 72                | 72                | 72                | 48                | 24                 |

## Table 3: Factorial separation (memory x control, live)

| Cell                  | Recall, live probes (%) | Committed violations per 100 transitions | False rejection (%) | Desync rate (%)  | Sessions |
| --------------------- | ----------------------- | ---------------------------------------- | ------------------- | ---------------- | -------- |
| F1 rolling, direct    | 0.0 [0.0, 0.0]          | 407.7 [355.1, 473.9]                     | n/a                 | 3.3 [1.5, 5.1]   | 7        |
| F2 rolling, barrier   | 0.0 [0.0, 0.0]          | 0.0 [0.0, 0.0]                           | 1.2 [0.0, 4.0]      | 10.3 [7.7, 13.2] | 7        |
| F3 dual-tier, direct  | 46.4 [32.1, 67.9]       | 408.5 [334.7, 503.1]                     | n/a                 | 3.7 [1.8, 5.5]   | 7        |
| F4 dual-tier, barrier | 46.4 [25.0, 71.4]       | 0.0 [0.0, 0.0]                           | 1.1 [0.0, 3.9]      | 9.2 [6.2, 12.1]  | 7        |

## Table 3b: Simple effects and interaction contrast (live, per session, pp)

| outcome   | contrast                                 | n_sessions | effect                  | p_wilcoxon |
| --------- | ---------------------------------------- | ---------- | ----------------------- | ---------- |
| recall    | memory effect \| direct writes (F3 - F1) | 7          | +46.4 [+32.1, +67.9]    | 0.01562    |
| recall    | memory effect \| barrier (F4 - F2)       | 7          | +46.4 [+25.0, +67.9]    | 0.03125    |
| recall    | control effect \| rolling (F2 - F1)      | 7          | +0.0 [+0.0, +0.0]       | 1          |
| recall    | control effect \| dual-tier (F4 - F3)    | 7          | +0.0 [-25.0, +25.0]     | 1          |
| recall    | interaction ((F4 - F2) - (F3 - F1))      | 7          | +0.0 [-25.0, +25.0]     | 1          |
| violation | memory effect \| direct writes (F3 - F1) | 7          | -44.9 [-181.2, +64.3]   | 0.875      |
| violation | memory effect \| barrier (F4 - F2)       | 7          | +0.0 [+0.0, +0.0]       | 1          |
| violation | control effect \| rolling (F2 - F1)      | 7          | -419.0 [-482.5, -363.4] | 0.01562    |
| violation | control effect \| dual-tier (F4 - F3)    | 7          | -374.0 [-502.5, -229.1] | 0.03125    |
| violation | interaction ((F4 - F2) - (F3 - F1))      | 7          | +44.9 [-64.3, +185.1]   | 0.875      |

## Table 4: Ablations

| Ablation                 | Recall, age 20+ (%)                  | MRR@6                | Committed violations per 100 transitions    | Local compute P50 (ms) | Recovery at turn 160 (ms)             | Replay consistency (%)               |
| ------------------------ | ------------------------------------ | -------------------- | ------------------------------------------- | ---------------------- | ------------------------------------- | ------------------------------------ |
| Full system (F4)         | 82.4 [78.0, 86.8]                    | 0.901 [0.878, 0.925] | probes 0.0 [0.0, 0.0]; live 0.0 [0.0, 0.0]  | 32.6                   | 1.6 (snapshot) vs 280.7 (full replay) | 100.0 [100.0, 100.0]                 |
| A1 No long-term memory   | 0.0 [0.0, 0.0]                       | n/a                  | same as full system (memory-only change)    | n/a                    | n/a                                   | as full system                       |
| A2 No short-term buffer  | 84.3 [80.4, 88.2]                    | 0.875 [0.849, 0.902] | same as full system (memory-only change)    | n/a                    | n/a                                   | as full system                       |
| A3 No scoping            | 79.6 [75.0, 84.1]                    | 0.724 [0.691, 0.757] | same as full system (memory-only change)    | n/a                    | n/a                                   | as full system                       |
| A4 No fallback           | 82.4 [78.0, 86.7]                    | 0.948 [0.928, 0.968] | same as full system (memory-only change)    | n/a                    | n/a                                   | as full system                       |
| A5 No validation barrier | as full system (control-only change) | as full system       | probes 4.5 [1.5, 8.4]; live 4.3 [0.0, 14.0] | 24.3                   | 1.6 (snapshot) vs 280.7 (full replay) | 100.0 [100.0, 100.0]                 |
| A6 No event sourcing     | as full system                       | as full system       | live 0.0 [0.0, 0.0]                         | 12.7                   | no log to recover from                | not replayable                       |
| A7 No snapshots          | as full system                       | as full system       | as full system                              | n/a                    | 280.7                                 | 100 (full fold, CPU replay sessions) |

## Table 5: Adversarial probes by category

| Category    | n attacks | Attack success, direct writes (%) | Attack success, reducer only A5 (%) | Attack success, barrier v1 (%) | Attack success, barrier v2 (%) | False rejection of lawful twin (%) | Validator gap v1 (%) | Validator gap v2 (%) |
| ----------- | --------- | --------------------------------- | ----------------------------------- | ------------------------------ | ------------------------------ | ---------------------------------- | -------------------- | -------------------- |
| teleport    | 210       | 13.3 [6.2, 21.4]                  | 0.0 [0.0, 0.0]                      | 0.0 [0.0, 0.0]                 | 0.0 [0.0, 0.0]                 | 0.0 [0.0, 0.0]                     | 10.3 [1.2, 21.8]     | 0.0 [0.0, 0.0]       |
| fabrication | 210       | 4.3 [1.4, 8.1]                    | 0.0 [0.0, 0.0]                      | 0.0 [0.0, 0.0]                 | 0.0 [0.0, 0.0]                 | 0.0 [0.0, 0.0]                     | 8.3 [0.0, 30.0]      | 0.0 [0.0, 0.0]       |
| theft       | 210       | 12.4 [5.7, 20.0]                  | 0.0 [0.0, 0.0]                      | 0.0 [0.0, 0.0]                 | 0.0 [0.0, 0.0]                 | 0.0 [0.0, 0.0]                     | 0.0 [0.0, 0.0]       | 0.0 [0.0, 0.0]       |
| trust       | 210       | 0.0 [0.0, 0.0]                    | 0.0 [0.0, 0.0]                      | 0.0 [0.0, 0.0]                 | 0.0 [0.0, 0.0]                 | 0.0 [0.0, 0.0]                     | 0.0 [0.0, 0.0]       | 0.0 [0.0, 0.0]       |
| currency    | 210       | 12.9 [5.2, 21.9]                  | 12.4 [4.8, 21.4]                    | 8.1 [1.9, 15.2]                | 0.0 [0.0, 0.0]                 | 4.5 [0.0, 15.5]                    | 63.0 [24.0, 100.0]   | 0.0 [0.0, 0.0]       |
| injection   | 210       | 0.0 [0.0, 0.0]                    | 0.0 [0.0, 0.0]                      | 0.0 [0.0, 0.0]                 | 0.0 [0.0, 0.0]                 | n/a (no lawful proposals)          | n/a                  | n/a                  |
| secret      | 210       | 0.0 [0.0, 0.0]                    | 0.0 [0.0, 0.0]                      | 0.0 [0.0, 0.0]                 | 0.0 [0.0, 0.0]                 | 0.0 [0.0, 0.0]                     | 100.0 [100.0, 100.0] | 0.0 [0.0, 0.0]       |
| all         | 1470      | 6.1 [4.1, 8.4]                    | 1.8 [0.6, 3.3]                      | 1.2 [0.3, 2.3]                 | 0.0 [0.0, 0.0]                 | 0.7 [0.0, 2.4]                     | 16.4 [7.6, 26.9]     | 0.0 [0.0, 0.0]       |

## Table 6: Per-stage latency (proposed system, single stream)

| Stage      | P50 (ms) | P95 (ms)  | P99 (ms)  | n turns |
| ---------- | -------- | --------- | --------- | ------- |
| input      | 0.003    | 0.003     | 0.003     | 24      |
| retrieval  | 0.172    | 0.229     | 0.236     | 24      |
| prompt     | 0.146    | 0.188     | 0.199     | 24      |
| llm        | 8839     | 1.61e+04  | 1.67e+04  | 24      |
| parse      | 0.09     | 0.106     | 0.11      | 24      |
| validate   | 0.014    | 1.365     | 1.387     | 24      |
| commit     | 9.726    | 15.39     | 16.45     | 24      |
| output     | 0.012    | 0.014     | 0.015     | 24      |
| local      | 18.2     | 8939      | 1.121e+04 | 24      |
| end to end | 8855     | 2.413e+04 | 2.692e+04 | 24      |

## Table 7: Per-world and backbone breakdown

| World  | Backbone        | Recall 20+: F4       | Recall 20+: best baseline | Attack success: F4 barrier | Attack success: best baseline (direct) |
| ------ | --------------- | -------------------- | ------------------------- | -------------------------- | -------------------------------------- |
| W1     | K2-Horizon-7B   | 86.1 [77.5, 96.9]    | B2: 88.9 [80.0, 97.2]     | 0.0 [0.0, 0.0]             | B0: 19.0 [7.1, 31.0]                   |
| W2a    | K2-Horizon-7B   | 83.3 [77.8, 89.3]    | B2: 80.6 [64.7, 97.1]     | 0.0 [0.0, 0.0]             | B3: 2.4 [0.0, 7.1]                     |
| W2b    | K2-Horizon-7B   | 91.7 [84.4, 97.6]    | B5: 80.6 [68.8, 91.7]     | 0.0 [0.0, 0.0]             | B0: 4.8 [0.0, 11.9]                    |
| W2c    | K2-Horizon-7B   | 83.3 [77.3, 92.9]    | B2: 80.6 [57.9, 97.4]     | 0.0 [0.0, 0.0]             | B0: 0.0 [0.0, 0.0]                     |
| W3     | K2-Horizon-7B   | 69.4 [53.3, 81.6]    | B0: 80.6 [66.7, 94.4]     | 0.0 [0.0, 0.0]             | B0: 0.0 [0.0, 0.0]                     |
| W4-32  | K2-Horizon-7B   | 83.3 [71.9, 94.4]    | B2: 88.9 [80.4, 97.4]     | 0.0 [0.0, 0.0]             | B0: 0.0 [0.0, 0.0]                     |
| W4-128 | K2-Horizon-7B   | 83.3 [73.7, 93.8]    | B5: 91.7 [84.4, 97.6]     | 0.0 [0.0, 0.0]             | B0: 0.0 [0.0, 0.0]                     |
| W1     | K2-Horizon-3.7B | 83.3 [83.3, 83.3]    | B2: 91.7 [83.3, 100.0]    | 0.0 [0.0, 0.0]             | F4 outputs: 14.3 [4.8, 26.2]           |
| W2a    | K2-Horizon-3.7B | 83.3 [83.3, 83.3]    | B5: 83.3 [83.3, 83.3]     | 0.0 [0.0, 0.0]             | F4 outputs: 14.3 [4.8, 26.2]           |
| W3     | K2-Horizon-3.7B | 75.0 [66.7, 83.3]    | B2: 66.7 [66.7, 66.7]     | 0.0 [0.0, 0.0]             | F4 outputs: 14.3 [4.8, 26.2]           |
| W4-32  | K2-Horizon-3.7B | 91.7 [83.3, 100.0]   | B5: 91.7 [83.3, 100.0]    | 0.0 [0.0, 0.0]             | F4 outputs: 16.7 [7.1, 28.6]           |
| W1     | qwen2.5-7b      | 100.0 [100.0, 100.0] | B5: 100.0 [100.0, 100.0]  | 0.0 [0.0, 0.0]             | F4 outputs: 59.5 [45.2, 73.8]          |
| W2a    | qwen2.5-7b      | 100.0 [100.0, 100.0] | B2: 83.3 [66.7, 100.0]    | 0.0 [0.0, 0.0]             | F4 outputs: 45.2 [31.0, 59.5]          |
| W3     | qwen2.5-7b      | 83.3 [83.3, 83.3]    | B2: 91.7 [83.3, 100.0]    | 0.0 [0.0, 0.0]             | F4 outputs: 40.5 [26.2, 54.8]          |
| W4-32  | qwen2.5-7b      | 91.7 [83.3, 100.0]   | B2: 91.7 [83.3, 100.0]    | 0.0 [0.0, 0.0]             | F4 outputs: 31.0 [16.7, 45.2]          |
| W1     | phi4-mini       | 91.7 [83.3, 100.0]   | B5: 83.3 [66.7, 100.0]    | 0.0 [0.0, 0.0]             | F4 outputs: 21.4 [9.5, 33.3]           |
| W2a    | phi4-mini       | 75.0 [50.0, 100.0]   | B2: 75.0 [66.7, 83.3]     | 0.0 [0.0, 0.0]             | F4 outputs: 19.0 [7.1, 31.0]           |
| W3     | phi4-mini       | 83.3 [66.7, 100.0]   | B5: 83.3 [66.7, 100.0]    | 0.0 [0.0, 0.0]             | F4 outputs: 33.3 [19.0, 47.6]          |
| W4-32  | phi4-mini       | 91.7 [83.3, 100.0]   | B2: 83.3 [66.7, 100.0]    | 0.0 [0.0, 0.0]             | F4 outputs: 23.8 [11.9, 38.1]          |

## Table 8: Before and after the Review-03 corrections (paired, same oracle)

| test | metric                                                             | before                 | after                 | n   | effect_pp | p_raw     | p_holm    |
| ---- | ------------------------------------------------------------------ | ---------------------- | --------------------- | --- | --------- | --------- | --------- |
| R1   | attack success, all categories                                     | 1.4 [0.3, 2.7]         | 0.0 [0.0, 0.0]        | 294 | 1.36      | 0.125     | 0.75      |
| R1   | attack success, currency                                           | 9.5 [2.4, 19.0]        | 0.0 [0.0, 0.0]        | 42  | 9.52      | 0.125     | 0.75      |
| R1   | validator gap, currency proposals                                  | 63.0 [24.0, 100.0]     | 0.0 [0.0, 0.0]        |     |           |           |           |
| R1   | validator gap, all proposals                                       | 16.4 [7.6, 26.9]       | 0.0 [0.0, 0.0]        |     |           |           |           |
| R1   | false rejection of lawful twins                                    | 0.7 [0.0, 2.4]         | 0.7 [0.0, 2.4]        |     |           |           |           |
| R2   | crash trials recovered inconsistently                              | 74.3% (5.6 turns lost) | 0.0% (0.0 turns lost) | 300 | 74.33     | 1.484e-67 | 1.335e-66 |
| R2   | load path after a crash (replay sessions)                          | 0% consistent          | 100% consistent       |     |           |           |           |
| R3   | judge contradiction, repaired probes                               | 35.7%                  | 32.1%                 | 28  | 3.57      | 1         | 1         |
| R3   | judge contradiction, repaired live F4 turns                        | 41.2%                  | 41.2%                 | 17  | 0         | 1         | 1         |
| R3   | judge contradiction per judged live turn, F4v1 vs F4 (per session) | 54.0%                  | 15.3%                 | 7   | 37.55     | 0.01562   | 0.125     |
| R3   | desync proxy, live F4 turns (draft vs repaired)                    | 9.5%                   | 9.2%                  | 273 | 0.37      | 1         | 1         |
| R3   | desync proxy per live turn, F4v1 vs F4 (per session)               | 17.2 [14.3, 19.8]      | 9.2 [6.2, 12.1]       | 7   | 8.06      | 0.03125   | 0.2188    |
| R4   | committed violations per 100 transitions, F4v1 vs F4 (per session) | 3.8 [0.0, 16.7]        | 0.0 [0.0, 0.0]        | 7   | 14.29     | 1         | 1         |

## Hypothesis verdicts

| hypothesis              | verdict                                     | evidence                                                                                                                                                                                                                                                    |
| ----------------------- | ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| H1 Memory               | not supported                               | F4 input tokens 1445 vs B2 1451, B3 1506                                                                                                                                                                                                                    |
| H2 Retrieval            | supported                                   | per-probe reciprocal rank, Wilcoxon                                                                                                                                                                                                                         |
| H3 State control        | not supported                               | probes McNemar + live Wilcoxon                                                                                                                                                                                                                              |
| H4 Cost of control      | supported                                   | false rejection 1.1 [0.0, 3.9]%; validate P95 1.365 ms                                                                                                                                                                                                      |
| H5 Replay               | supported                                   | live event-sourced sessions all consistent: True; CPU replay, restart, backend load path after a crash and 300 randomised crash trials all consistent: True                                                                                                 |
| H6 Separability         | not supported                               | memory->recall coef 3.17 (p=1.59e-28); control->violation coef -7.63 (p=8.46e-29); interaction p recall=0.0137, violation=0.195                                                                                                                             |
| H7 Generalisation       | not supported                               | W2 LIGHT-derived: dRecall=+0.861, dAttack=+0.056; W3 held-out genre: dRecall=+0.694, dAttack=+0.000; W4 procedural: dRecall=+0.833, dAttack=+0.000; backbone qwen2.5-7b: dRecall=+0.938, dAttack=+0.440; backbone phi4-mini: dRecall=+0.854, dAttack=+0.244 |
| R1 Currency invariant   | confirmed (no failure after the correction) | v2 currency validator gap 0.0 [0.0, 0.0]%                                                                                                                                                                                                                   |
| R2 Snapshot recovery    | confirmed (no failure after the correction) | 300/300 crash trials consistent after the correction                                                                                                                                                                                                        |
| R3 Dialogue repair      | not confirmed                               | draft vs repaired (judge, proxy) and F4v1 vs F4                                                                                                                                                                                                             |
| R4 Committed violations | not confirmed                               | F4v1 vs F4, live, per session                                                                                                                                                                                                                               |

## Confirmatory tests

| hypothesis | test                                                            | n   | effect | p_raw  | direction_ok | p_holm |
| ---------- | --------------------------------------------------------------- | --- | ------ | ------ | ------------ | ------ |
| H1         | recall 20+ F4 vs B1 (McNemar)                                   | 216 | 0.8241 | 0      | True         | 0      |
| H1         | recall 20+ F4 vs B2 (McNemar)                                   | 216 | 0.0139 | 0.7359 | True         | 0.7359 |
| H1         | recall 20+ F4 vs B3 (McNemar)                                   | 216 | 0.2361 | 0      | True         | 0      |
| H2         | MRR@6 F4 vs B2 (Wilcoxon, per probe)                            | 288 | 0.1744 | 0      | True         | 0      |
| H3         | attack success direct vs barrier, F4 context (McNemar)          | 294 | 0.051  | 0.0001 | True         | 0.0002 |
| H3         | live violations per transition F3 vs F4 (Wilcoxon, per session) | 7   | 3.74   | 0.0312 | True         | 0.0625 |

## Exploratory memory tests

| test                            | n   | effect  | p_raw  | p_holm |
| ------------------------------- | --- | ------- | ------ | ------ |
| recall 20+ F4 vs B4 (McNemar)   | 216 | 0.213   | 0      | 0      |
| recall 20+ F4 vs B5 (McNemar)   | 216 | 0.037   | 0.2682 | 0.5364 |
| recall 20+ F4 vs F4v1 (McNemar) | 216 | -0.0231 | 0.4731 | 0.5364 |

## Limitations of this run

- W3 authorship: notebook author (not independent; see caveat). The article requires an independent author; attach w3_world_seed.json to satisfy it.
- Recall, leaks and the desync proxy are scored automatically (key-word match, secret keywords, refusal/arrival cues); the judge (qwen2.5-7b: 182 items judged) is an LLM. Human evaluation: pending (no human_ratings_*.csv attached).
- Token cost is reported in tokens only; the models are self-hosted, so no provider list price applies.
- Latency was measured on 2x T4 with vLLM; hosted-endpoint latency is not reproduced.
- F4v1 reuses the corrected reducer, event store and commit node; it differs from F4 in the validator, the prompt builder, the unbudgeted memory assembly and the absence of dialogue repair, which are the components Review-03 changed.
- Live sessions address scripted NPCs even when a scripted move was not committed; this divergence is measured as desynchronisation.
- B4 omits the Generative Agents importance score (an LLM call per memory write); B4 and B5 are re-implementations of the retrieval rules, not the original systems.
- Sample size: ladder level 1 of 7 ({'n_rec': 2, 'n_probe': 6, 'n_live': 1}); the article's full targets correspond to level 7. Attach this run's llm_cache_*.jsonl and rerun to reach a larger level.
- Second backbone: run on ['W1', 'W2a', 'W3', 'W4-32']. Independent families: {'qwen2.5-7b': "run on ['W1', 'W2a', 'W3', 'W4-32'] (horizon 100)", 'phi4-mini': "run on ['W1', 'W2a', 'W3', 'W4-32'] (horizon 100)"}.
