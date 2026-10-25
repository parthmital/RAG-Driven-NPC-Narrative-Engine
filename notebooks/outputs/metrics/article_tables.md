# Results: Memory and State Control for LLM-Driven NPC Dialogue

Generated 2026-10-25T02:38:37Z from backend bundle `9f7d7e7bbb0d`, ladder level 2, backbone IFM/K2-Horizon-7B (fp16, vLLM 0.30.0, reasoning effort low, thinking budget 192 tokens). Values: mean [95% cluster-bootstrap CI]; held-out = W2a to W4-128.

## Table 1: Main comparison (held-out worlds)

| Condition                                   | Recall, age 20+ (%) | Committed violations per 100 transitions | Probe attack success (%) | MRR@6                | P50 / P95 latency (ms) | Input tokens per turn | Replay consistency (%)        |
| ------------------------------------------- | ------------------- | ---------------------------------------- | ------------------------ | -------------------- | ---------------------- | --------------------- | ----------------------------- |
| Proposed (dual-tier + barrier)              | 83.0 [79.4, 86.7]   | 0.0 [0.0, 0.0]                           | 0.0 [0.0, 0.0]           | 0.910 [0.889, 0.931] | 6593 / 8120            | 1444                  | 100.0 [100.0, 100.0]          |
| Proposed before revision (Review-02)        | 88.6 [85.1, 91.9]   | 2.4 [0.0, 5.4]                           | 0.7 [0.0, 1.7]           | 0.888 [0.864, 0.913] | 6888 / 8559            | 1399                  | not replayable (no event log) |
| B0 Full history                             | 77.8 [73.4, 82.2]   | 21.7 [15.2, 28.4]                        | 3.6 [1.9, 5.5]           | n/a                  | 10820 / 24549          | 4406                  | not replayable (no event log) |
| B1 Rolling, B                               | 0.0 [0.0, 0.0]      | 21.7 [15.2, 28.4]                        | 3.6 [1.9, 5.5]           | n/a                  | 6725 / 7665            | 1478                  | not replayable (no event log) |
| B1 Rolling, 2B                              | 19.8 [15.5, 24.2]   | n/a (no probe context)                   | n/a                      | n/a                  | 6903 / 8781            | 1877                  | not replayable (no event log) |
| B2 Vector memory                            | 84.3 [79.3, 88.8]   | 23.4 [17.4, 29.9]                        | 5.5 [3.3, 7.6]           | 0.742 [0.720, 0.765] | 6069 / 10061           | 1451                  | not replayable (no event log) |
| B3 Generic RAG                              | 61.7 [55.8, 67.4]   | 39.7 [32.5, 46.9]                        | 7.4 [5.0, 10.0]          | 0.700 [0.675, 0.726] | 5876 / 9752            | 1506                  | not replayable (no event log) |
| B4 Scored memory stream (Generative Agents) | 63.0 [58.6, 67.5]   | n/a (no probe context)                   | n/a                      | 0.557 [0.527, 0.586] | 6115 / 10972           | 1449                  | not replayable (no event log) |
| B5 Forgetting-curve memory (MemoryBank)     | 79.9 [75.5, 84.5]   | n/a (no probe context)                   | n/a                      | 0.723 [0.697, 0.749] | 6165 / 21517           | 1450                  | not replayable (no event log) |

## Table 2: Recall by fact age (held-out worlds, %)

| Condition                                   | 5                 | 10                | 20                | 40                | 80                | 160                |
| ------------------------------------------- | ----------------- | ----------------- | ----------------- | ----------------- | ----------------- | ------------------ |
| Proposed (dual-tier + barrier)              | 78.7 [71.3, 85.2] | 85.2 [77.8, 91.7] | 83.3 [76.9, 89.8] | 81.5 [74.1, 88.0] | 80.6 [70.8, 88.9] | 91.7 [83.3, 100.0] |
| Proposed before revision (Review-02)        | 96.3 [92.6, 99.1] | 87.0 [80.6, 92.6] | 86.1 [79.6, 92.6] | 90.7 [85.2, 95.4] | 86.1 [79.2, 93.1] | 94.4 [86.1, 100.0] |
| B0 Full history                             | 83.3 [75.0, 90.7] | 76.9 [69.4, 84.3] | 77.8 [69.4, 86.1] | 75.9 [67.6, 84.3] | 81.9 [72.2, 90.3] | 75.0 [63.9, 86.1]  |
| B1 Rolling, B                               | 80.6 [73.1, 88.0] | 59.3 [49.1, 69.4] | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]     |
| B1 Rolling, 2B                              | 75.9 [68.5, 83.3] | 78.7 [71.3, 85.2] | 59.3 [48.1, 70.4] | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]     |
| B2 Vector memory                            | 85.2 [78.7, 90.7] | 88.9 [82.4, 94.4] | 85.2 [78.7, 91.7] | 83.3 [75.0, 90.7] | 80.6 [70.8, 90.3] | 91.7 [83.3, 100.0] |
| B3 Generic RAG                              | 68.5 [60.2, 76.9] | 66.7 [57.4, 75.0] | 62.0 [52.8, 71.3] | 62.0 [52.8, 71.3] | 61.1 [50.0, 72.2] | 61.1 [47.2, 75.0]  |
| B4 Scored memory stream (Generative Agents) | 85.2 [78.7, 90.7] | 90.7 [84.3, 96.3] | 85.2 [78.7, 91.7] | 71.3 [63.9, 78.7] | 37.5 [26.4, 48.6] | 22.2 [8.3, 36.1]   |
| B5 Forgetting-curve memory (MemoryBank)     | 87.0 [81.5, 92.6] | 90.7 [84.3, 96.3] | 85.2 [78.7, 90.7] | 81.5 [75.0, 88.0] | 72.2 [61.1, 81.9] | 75.0 [58.3, 88.9]  |
| A1 No long-term memory                      | 82.4 [75.0, 88.9] | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]     |
| A2 No short-term buffer                     | 85.2 [79.6, 90.7] | 88.9 [83.3, 94.4] | 88.0 [82.4, 93.5] | 85.2 [77.8, 91.7] | 84.7 [76.4, 93.1] | 88.9 [77.8, 97.2]  |
| A3 No scoping                               | 63.9 [55.6, 72.2] | 85.2 [78.7, 90.7] | 85.2 [77.8, 91.7] | 76.9 [69.4, 84.3] | 79.2 [69.4, 87.5] | 86.1 [75.0, 94.4]  |
| A4 No fallback                              | 83.3 [76.9, 89.8] | 83.3 [75.9, 89.8] | 83.3 [76.9, 89.8] | 80.6 [73.1, 87.0] | 81.9 [72.2, 90.3] | 91.7 [83.3, 100.0] |
| n (F4 probes)                               | 108               | 108               | 108               | 108               | 72                | 36                 |

## Table 3: Factorial separation (memory x control, live)

| Cell                  | Recall, live probes (%) | Committed violations per 100 transitions | False rejection (%) | Desync rate (%)  | Sessions |
| --------------------- | ----------------------- | ---------------------------------------- | ------------------- | ---------------- | -------- |
| F1 rolling, direct    | 0.0 [0.0, 0.0]          | 501.1 [425.2, 602.6]                     | n/a                 | 3.1 [1.6, 4.9]   | 14       |
| F2 rolling, barrier   | 0.0 [0.0, 0.0]          | 0.0 [0.0, 0.0]                           | 0.7 [0.0, 2.4]      | 12.5 [9.7, 15.0] | 14       |
| F3 dual-tier, direct  | 37.5 [25.0, 50.0]       | 397.5 [358.8, 447.1]                     | n/a                 | 2.9 [1.5, 4.9]   | 14       |
| F4 dual-tier, barrier | 46.4 [35.7, 58.9]       | 0.0 [0.0, 0.0]                           | 0.7 [0.0, 2.4]      | 9.5 [7.9, 11.7]  | 14       |

## Table 3b: Simple effects and interaction contrast (live, per session, pp)

| outcome   | contrast                                 | n_sessions | effect                  | p_wilcoxon |
| --------- | ---------------------------------------- | ---------- | ----------------------- | ---------- |
| recall    | memory effect \| direct writes (F3 - F1) | 14         | +37.5 [+25.0, +50.0]    | 0.001208   |
| recall    | memory effect \| barrier (F4 - F2)       | 14         | +46.4 [+35.7, +58.9]    | 0.0008312  |
| recall    | control effect \| rolling (F2 - F1)      | 14         | +0.0 [+0.0, +0.0]       | 1          |
| recall    | control effect \| dual-tier (F4 - F3)    | 14         | +8.9 [-1.8, +19.6]      | 0.1576     |
| recall    | interaction ((F4 - F2) - (F3 - F1))      | 14         | +8.9 [-1.8, +19.6]      | 0.1576     |
| violation | memory effect \| direct writes (F3 - F1) | 14         | -207.5 [-439.0, -55.4]  | 0.01435    |
| violation | memory effect \| barrier (F4 - F2)       | 14         | +0.0 [+0.0, +0.0]       | 1          |
| violation | control effect \| rolling (F2 - F1)      | 14         | -628.7 [-871.7, -473.7] | 0.0009646  |
| violation | control effect \| dual-tier (F4 - F3)    | 14         | -421.2 [-470.6, -375.5] | 0.0009618  |
| violation | interaction ((F4 - F2) - (F3 - F1))      | 14         | +207.5 [+51.3, +436.2]  | 0.01435    |

## Table 4: Ablations

| Ablation                 | Recall, age 20+ (%)                  | MRR@6                | Committed violations per 100 transitions   | Local compute P50 (ms) | Recovery at turn 160 (ms)             | Replay consistency (%)               |
| ------------------------ | ------------------------------------ | -------------------- | ------------------------------------------ | ---------------------- | ------------------------------------- | ------------------------------------ |
| Full system (F4)         | 83.0 [79.4, 86.7]                    | 0.910 [0.889, 0.931] | probes 0.0 [0.0, 0.0]; live 0.0 [0.0, 0.0] | 25.0                   | 1.4 (snapshot) vs 243.2 (full replay) | 100.0 [100.0, 100.0]                 |
| A1 No long-term memory   | 0.0 [0.0, 0.0]                       | n/a                  | same as full system (memory-only change)   | n/a                    | n/a                                   | as full system                       |
| A2 No short-term buffer  | 86.4 [83.0, 89.7]                    | 0.888 [0.864, 0.913] | same as full system (memory-only change)   | n/a                    | n/a                                   | as full system                       |
| A3 No scoping            | 81.2 [77.6, 84.8]                    | 0.732 [0.707, 0.759] | same as full system (memory-only change)   | n/a                    | n/a                                   | as full system                       |
| A4 No fallback           | 83.0 [79.5, 86.6]                    | 0.954 [0.939, 0.969] | same as full system (memory-only change)   | n/a                    | n/a                                   | as full system                       |
| A5 No validation barrier | as full system (control-only change) | as full system       | probes 5.0 [2.3, 8.1]; live 3.9 [1.0, 7.1] | 22.3                   | 1.4 (snapshot) vs 243.2 (full replay) | 100.0 [100.0, 100.0]                 |
| A6 No event sourcing     | as full system                       | as full system       | live 0.0 [0.0, 0.0]                        | 10.0                   | no log to recover from                | not replayable                       |
| A7 No snapshots          | as full system                       | as full system       | as full system                             | n/a                    | 243.2                                 | 100 (full fold, CPU replay sessions) |

## Table 5: Adversarial probes by category

| Category    | n attacks | Attack success, direct writes (%) | Attack success, reducer only A5 (%) | Attack success, barrier v1 (%) | Attack success, barrier v2 (%) | False rejection of lawful twin (%) | Validator gap v1 (%) | Validator gap v2 (%) |
| ----------- | --------- | --------------------------------- | ----------------------------------- | ------------------------------ | ------------------------------ | ---------------------------------- | -------------------- | -------------------- |
| teleport    | 350       | 12.6 [7.1, 18.9]                  | 0.9 [0.0, 2.0]                      | 0.9 [0.0, 2.0]                 | 0.0 [0.0, 0.0]                 | 0.0 [0.0, 0.0]                     | 7.8 [2.5, 14.5]      | 0.0 [0.0, 0.0]       |
| fabrication | 350       | 6.0 [2.6, 10.0]                   | 0.0 [0.0, 0.0]                      | 0.0 [0.0, 0.0]                 | 0.0 [0.0, 0.0]                 | 0.0 [0.0, 0.0]                     | 4.7 [0.0, 15.0]      | 0.0 [0.0, 0.0]       |
| theft       | 350       | 13.4 [8.0, 19.4]                  | 1.7 [0.0, 4.3]                      | 0.0 [0.0, 0.0]                 | 0.0 [0.0, 0.0]                 | 0.0 [0.0, 0.0]                     | 0.0 [0.0, 0.0]       | 0.0 [0.0, 0.0]       |
| trust       | 350       | 0.0 [0.0, 0.0]                    | 0.0 [0.0, 0.0]                      | 0.0 [0.0, 0.0]                 | 0.0 [0.0, 0.0]                 | 7.1 [0.0, 30.0]                    | 0.0 [0.0, 0.0]       | 0.0 [0.0, 0.0]       |
| currency    | 350       | 12.6 [6.9, 18.9]                  | 12.6 [6.9, 18.9]                    | 7.4 [3.4, 12.0]                | 0.0 [0.0, 0.0]                 | 3.0 [0.0, 10.3]                    | 59.1 [32.5, 88.5]    | 0.0 [0.0, 0.0]       |
| injection   | 350       | 0.0 [0.0, 0.0]                    | 0.0 [0.0, 0.0]                      | 0.0 [0.0, 0.0]                 | 0.0 [0.0, 0.0]                 | n/a (no lawful proposals)          | n/a                  | n/a                  |
| secret      | 350       | 0.3 [0.0, 0.9]                    | 0.0 [0.0, 0.0]                      | 0.0 [0.0, 0.0]                 | 0.0 [0.0, 0.0]                 | 0.0 [0.0, 0.0]                     | 100.0 [100.0, 100.0] | 0.0 [0.0, 0.0]       |
| all         | 2450      | 6.4 [4.8, 8.2]                    | 2.2 [1.2, 3.3]                      | 1.2 [0.6, 2.0]                 | 0.0 [0.0, 0.0]                 | 0.6 [0.0, 1.7]                     | 13.6 [8.0, 20.1]     | 0.0 [0.0, 0.0]       |

## Table 6: Per-stage latency (proposed system, single stream)

| Stage      | P50 (ms) | P95 (ms)  | P99 (ms)  | n turns |
| ---------- | -------- | --------- | --------- | ------- |
| input      | 0.002    | 0.002     | 0.003     | 24      |
| retrieval  | 0.153    | 0.241     | 0.266     | 24      |
| prompt     | 0.13     | 0.167     | 0.246     | 24      |
| llm        | 8113     | 1.493e+04 | 1.547e+04 | 24      |
| parse      | 0.087    | 0.125     | 0.138     | 24      |
| validate   | 0.013    | 1.397     | 1.52      | 24      |
| repair     | 0.002    | 4491      | 6516      | 24      |
| commit     | 8.427    | 12.98     | 13.39     | 24      |
| output     | 0.01     | 0.012     | 0.013     | 24      |
| local      | 15.1     | 19.21     | 20.39     | 24      |
| end to end | 8127     | 1.767e+04 | 2.147e+04 | 24      |

## Table 7: Per-world and backbone breakdown

| World  | Backbone        | Recall 20+: F4       | Recall 20+: best baseline | Attack success: F4 barrier | Attack success: best baseline (direct) |
| ------ | --------------- | -------------------- | ------------------------- | -------------------------- | -------------------------------------- |
| W1     | K2-Horizon-7B   | 87.0 [79.6, 94.6]    | B2: 88.9 [81.5, 96.3]     | 0.0 [0.0, 0.0]             | B0: 14.3 [7.1, 22.9]                   |
| W2a    | K2-Horizon-7B   | 83.3 [75.0, 91.1]    | B2: 81.5 [69.6, 93.2]     | 0.0 [0.0, 0.0]             | B3: 4.3 [0.0, 10.0]                    |
| W2b    | K2-Horizon-7B   | 88.9 [81.5, 95.8]    | B5: 85.2 [75.9, 94.0]     | 0.0 [0.0, 0.0]             | B0: 2.9 [0.0, 7.1]                     |
| W2c    | K2-Horizon-7B   | 79.6 [71.0, 90.0]    | B2: 83.3 [66.7, 95.8]     | 0.0 [0.0, 0.0]             | B0: 2.9 [0.0, 7.1]                     |
| W3     | K2-Horizon-7B   | 79.6 [70.0, 88.7]    | B2: 81.5 [65.0, 94.8]     | 0.0 [0.0, 0.0]             | B2: 5.7 [1.4, 11.4]                    |
| W4-32  | K2-Horizon-7B   | 83.3 [75.9, 91.1]    | B2: 88.9 [83.3, 95.5]     | 0.0 [0.0, 0.0]             | B0: 0.0 [0.0, 0.0]                     |
| W4-128 | K2-Horizon-7B   | 83.3 [73.9, 91.7]    | B5: 90.7 [83.9, 97.9]     | 0.0 [0.0, 0.0]             | B0: 0.0 [0.0, 0.0]                     |
| W1     | K2-Horizon-3.7B | 88.9 [83.3, 100.0]   | B4: 94.4 [83.3, 100.0]    | 0.0 [0.0, 0.0]             | F4 outputs: 12.9 [5.7, 21.4]           |
| W2a    | K2-Horizon-3.7B | 83.3 [83.3, 83.3]    | B2: 72.2 [50.0, 100.0]    | 0.0 [0.0, 0.0]             | F4 outputs: 11.4 [4.3, 18.6]           |
| W3     | K2-Horizon-3.7B | 72.2 [50.0, 83.3]    | B2: 72.2 [66.7, 83.3]     | 0.0 [0.0, 0.0]             | F4 outputs: 8.6 [2.9, 15.7]            |
| W4-32  | K2-Horizon-3.7B | 83.3 [66.7, 100.0]   | B5: 88.9 [83.3, 100.0]    | 0.0 [0.0, 0.0]             | F4 outputs: 15.7 [7.1, 24.3]           |
| W1     | qwen2.5-7b      | 100.0 [100.0, 100.0] | B2: 94.4 [83.3, 100.0]    | 0.0 [0.0, 0.0]             | F4 outputs: 55.7 [44.3, 67.1]          |
| W2a    | qwen2.5-7b      | 94.4 [83.3, 100.0]   | B2: 83.3 [66.7, 100.0]    | 0.0 [0.0, 0.0]             | F4 outputs: 48.6 [37.1, 60.0]          |
| W3     | qwen2.5-7b      | 88.9 [83.3, 100.0]   | B2: 94.4 [83.3, 100.0]    | 0.0 [0.0, 0.0]             | F4 outputs: 34.3 [22.9, 45.7]          |
| W4-32  | qwen2.5-7b      | 94.4 [83.3, 100.0]   | B2: 83.3 [66.7, 100.0]    | 0.0 [0.0, 0.0]             | F4 outputs: 37.1 [25.7, 48.6]          |
| W1     | phi4-mini       | 83.3 [66.7, 100.0]   | B2: 77.8 [66.7, 83.3]     | 0.0 [0.0, 0.0]             | F4 outputs: 27.1 [17.1, 37.1]          |
| W2a    | phi4-mini       | 72.2 [50.0, 100.0]   | B2: 61.1 [50.0, 83.3]     | 0.0 [0.0, 0.0]             | F4 outputs: 17.1 [8.6, 27.1]           |
| W3     | phi4-mini       | 77.8 [50.0, 100.0]   | B5: 77.8 [66.7, 100.0]    | 0.0 [0.0, 0.0]             | F4 outputs: 27.1 [17.1, 37.1]          |
| W4-32  | phi4-mini       | 88.9 [83.3, 100.0]   | B2: 77.8 [66.7, 100.0]    | 0.0 [0.0, 0.0]             | F4 outputs: 24.3 [14.3, 34.3]          |

## Table 8: Before and after the Review-03 corrections (paired, same oracle)

| test | metric                                                             | before                 | after                 | n   | effect_pp | p_raw     | p_holm    |
| ---- | ------------------------------------------------------------------ | ---------------------- | --------------------- | --- | --------- | --------- | --------- |
| R1   | attack success, all categories                                     | 1.0 [0.2, 2.0]         | 0.0 [0.0, 0.0]        | 490 | 1.02      | 0.0625    | 0.3125    |
| R1   | attack success, currency                                           | 7.1 [1.4, 12.9]        | 0.0 [0.0, 0.0]        | 70  | 7.14      | 0.0625    | 0.3125    |
| R1   | validator gap, currency proposals                                  | 59.1 [32.5, 88.5]      | 0.0 [0.0, 0.0]        |     |           |           |           |
| R1   | validator gap, all proposals                                       | 13.6 [8.0, 20.1]       | 0.0 [0.0, 0.0]        |     |           |           |           |
| R1   | false rejection of lawful twins                                    | 0.6 [0.0, 1.7]         | 0.6 [0.0, 1.7]        |     |           |           |           |
| R2   | crash trials recovered inconsistently                              | 74.3% (5.6 turns lost) | 0.0% (0.0 turns lost) | 300 | 74.33     | 1.484e-67 | 1.335e-66 |
| R2   | load path after a crash (replay sessions)                          | 0% consistent          | 100% consistent       |     |           |           |           |
| R3   | judge contradiction, repaired probes                               | 41.7%                  | 39.6%                 | 48  | 2.08      | 1         | 1         |
| R3   | judge contradiction, repaired live F4 turns                        | 44.7%                  | 42.1%                 | 38  | 2.63      | 1         | 1         |
| R3   | judge contradiction per judged live turn, F4v1 vs F4 (per session) | 57.0%                  | 13.8%                 | 14  | 42.42     | 0.001222  | 0.008628  |
| R3   | desync proxy, live F4 turns (draft vs repaired)                    | 10.6%                  | 9.5%                  | 546 | 1.1       | 0.03125   | 0.1875    |
| R3   | desync proxy per live turn, F4v1 vs F4 (per session)               | 18.9 [16.5, 21.2]      | 9.5 [7.9, 11.7]       | 14  | 9.34      | 0.001078  | 0.008628  |
| R4   | committed violations per 100 transitions, F4v1 vs F4 (per session) | 8.3 [2.0, 17.0]        | 0.0 [0.0, 0.0]        | 14  | 10.71     | 0.1015    | 0.3125    |

## Hypothesis verdicts

| hypothesis              | verdict                                     | evidence                                                                                                                                                                                                                                                    |
| ----------------------- | ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| H1 Memory               | not supported                               | F4 input tokens 1444 vs B2 1451, B3 1506                                                                                                                                                                                                                    |
| H2 Retrieval            | supported                                   | per-probe reciprocal rank, Wilcoxon                                                                                                                                                                                                                         |
| H3 State control        | supported                                   | probes McNemar + live Wilcoxon                                                                                                                                                                                                                              |
| H4 Cost of control      | supported                                   | false rejection 0.7 [0.0, 2.4]%; validate P95 1.397 ms                                                                                                                                                                                                      |
| H5 Replay               | supported                                   | live event-sourced sessions all consistent: True; CPU replay, restart, backend load path after a crash and 300 randomised crash trials all consistent: True                                                                                                 |
| H6 Separability         | not supported                               | memory->recall coef 3.38 (p=2.38e-62); control->violation coef -8.32 (p=9.37e-37); interaction p recall=3.12e-06, violation=0.105                                                                                                                           |
| H7 Generalisation       | not supported                               | W2 LIGHT-derived: dRecall=+0.840, dAttack=+0.048; W3 held-out genre: dRecall=+0.796, dAttack=+0.071; W4 procedural: dRecall=+0.833, dAttack=+0.000; backbone qwen2.5-7b: dRecall=+0.944, dAttack=+0.439; backbone phi4-mini: dRecall=+0.806, dAttack=+0.239 |
| R1 Currency invariant   | confirmed (no failure after the correction) | v2 currency validator gap 0.0 [0.0, 0.0]%                                                                                                                                                                                                                   |
| R2 Snapshot recovery    | confirmed (no failure after the correction) | 300/300 crash trials consistent after the correction                                                                                                                                                                                                        |
| R3 Dialogue repair      | partly confirmed                            | draft vs repaired (judge, proxy) and F4v1 vs F4                                                                                                                                                                                                             |
| R4 Committed violations | not confirmed                               | F4v1 vs F4, live, per session                                                                                                                                                                                                                               |

## Confirmatory tests

| hypothesis | test                                                            | n   | effect  | p_raw  | direction_ok | p_holm |
| ---------- | --------------------------------------------------------------- | --- | ------- | ------ | ------------ | ------ |
| H1         | recall 20+ F4 vs B1 (McNemar)                                   | 324 | 0.8302  | 0      | True         | 0      |
| H1         | recall 20+ F4 vs B2 (McNemar)                                   | 324 | -0.0123 | 0.6835 | False        | 0.6835 |
| H1         | recall 20+ F4 vs B3 (McNemar)                                   | 324 | 0.213   | 0      | True         | 0      |
| H2         | MRR@6 F4 vs B2 (Wilcoxon, per probe)                            | 432 | 0.1679  | 0      | True         | 0      |
| H3         | attack success direct vs barrier, F4 context (McNemar)          | 490 | 0.051   | 0      | True         | 0      |
| H3         | live violations per transition F3 vs F4 (Wilcoxon, per session) | 14  | 4.212   | 0.001  | True         | 0.0019 |

## Exploratory memory tests

| test                            | n   | effect  | p_raw  | p_holm |
| ------------------------------- | --- | ------- | ------ | ------ |
| recall 20+ F4 vs B4 (McNemar)   | 324 | 0.2006  | 0      | 0      |
| recall 20+ F4 vs B5 (McNemar)   | 324 | 0.0309  | 0.2678 | 0.2678 |
| recall 20+ F4 vs F4v1 (McNemar) | 324 | -0.0556 | 0.0096 | 0.0191 |

## Limitations of this run

- W3 authorship: notebook author (not independent; see caveat). The article requires an independent author; attach w3_world_seed.json to satisfy it.
- Recall, leaks and the desync proxy are scored automatically (key-word match, secret keywords, refusal/arrival cues); the judge (qwen2.5-7b: 364 items judged) is an LLM. Human evaluation: pending (no human_ratings_*.csv attached).
- Token cost is reported in tokens only; the models are self-hosted, so no provider list price applies.
- Latency was measured on 2x T4 with vLLM; hosted-endpoint latency is not reproduced.
- F4v1 reuses the corrected reducer, event store and commit node; it differs from F4 in the validator, the prompt builder, the unbudgeted memory assembly and the absence of dialogue repair, which are the components Review-03 changed.
- Live sessions address scripted NPCs even when a scripted move was not committed; this divergence is measured as desynchronisation.
- B4 omits the Generative Agents importance score (an LLM call per memory write); B4 and B5 are re-implementations of the retrieval rules, not the original systems.
- Sample size: ladder level 2 of 7 ({'n_rec': 3, 'n_probe': 10, 'n_live': 2}); the article's full targets correspond to level 7. Attach this run's llm_cache_*.jsonl and rerun to reach a larger level.
- Second backbone: run on ['W1', 'W2a', 'W3', 'W4-32']. Independent families: {'qwen2.5-7b': "run on ['W1', 'W2a', 'W3', 'W4-32'] (horizon 100)", 'phi4-mini': "run on ['W1', 'W2a', 'W3', 'W4-32'] (horizon 100)"}.
