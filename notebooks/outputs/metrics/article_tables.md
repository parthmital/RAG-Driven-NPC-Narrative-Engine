# Results: Memory and State Control for LLM-Driven NPC Dialogue

Generated 2026-11-03T05:24:38Z from backend bundle `84a4c1ced397`, ladder level 5, backbone IFM/K2-Horizon-7B (fp16, vLLM 0.30.0, reasoning effort low, thinking budget 192 tokens), protocol digest `cdaa4f484e132abb`, master seed 20261103. Values: mean [95% cluster-bootstrap CI], or the exact Clopper-Pearson interval when no event (or every row) occurred; held-out = W2a to W4-128. Recall is strict (parsed reply, gold value, no competing value).

## Table 1: Main comparison (held-out worlds)

| Condition                                   | Recall, age 20+ (%) | Committed violations per 100 transitions | Probe attack success (%) | MRR@6                | P50 / P95 latency (ms) | Input tokens per turn | Replay consistency (%)        |
| ------------------------------------------- | ------------------- | ---------------------------------------- | ------------------------ | -------------------- | ---------------------- | --------------------- | ----------------------------- |
| Proposed (dual-tier + barrier)              | 63.7 [59.4, 68.0]   | 0.0 [0.0, 1.5]                           | 0.1 [0.0, 0.3]           | 0.805 [0.787, 0.824] | 6750 / 7847            | 1468                  | 100.0 [76.8, 100.0]           |
| Proposed before revision (Review-02)        | 63.3 [59.6, 67.1]   | 1.6 [0.0, 4.8]                           | 0.5 [0.0, 1.3]           | 0.751 [0.732, 0.772] | 6452 / 7478            | 1425                  | not replayable (no event log) |
| B0 Full history                             | 53.4 [49.0, 58.1]   | as B1 (same outputs, direct writes)      | as B1                    | n/a                  | 10737 / 18238          | 4438                  | not replayable (no event log) |
| B1 Rolling, B                               | 0.0 [0.0, 0.7]      | 26.5 [19.0, 35.7]                        | 2.6 [1.2, 4.2]           | n/a                  | 5922 / 7766            | 1513                  | not replayable (no event log) |
| B2 Vector memory                            | 69.3 [65.5, 73.2]   | as B1 (same outputs, direct writes)      | as B1                    | 0.786 [0.767, 0.804] | 6269 / 8139            | 1456                  | not replayable (no event log) |
| B3 Generic RAG                              | 38.0 [34.4, 41.7]   | as B1 (same outputs, direct writes)      | as B1                    | 0.726 [0.703, 0.748] | 5790 / 11501           | 1516                  | not replayable (no event log) |
| B4 Scored memory stream (Generative Agents) | 54.2 [50.1, 58.4]   | as B1 (same outputs, direct writes)      | as B1                    | 0.346 [0.321, 0.370] | 6814 / 8881            | 1460                  | not replayable (no event log) |
| B5 Forgetting-curve memory (MemoryBank)     | 60.7 [56.6, 65.0]   | as B1 (same outputs, direct writes)      | as B1                    | 0.788 [0.766, 0.810] | 6542 / 7723            | 1455                  | not replayable (no event log) |

## Table 2: Recall by fact age (held-out worlds, %)

| Condition                                     | 5                 | 10                | 20                | 40                | 80                | 160               |
| --------------------------------------------- | ----------------- | ----------------- | ----------------- | ----------------- | ----------------- | ----------------- |
| Proposed (dual-tier + barrier)                | 30.0 [23.3, 36.7] | 56.7 [50.0, 63.3] | 60.0 [52.2, 67.8] | 67.8 [60.9, 74.6] | 65.8 [55.8, 75.0] | 58.3 [45.0, 71.7] |
| Proposed before revision (Review-02)          | 52.2 [44.4, 59.4] | 53.3 [46.1, 60.6] | 59.4 [52.8, 66.1] | 68.4 [61.2, 75.4] | 65.0 [55.8, 73.3] | 56.7 [43.3, 70.0] |
| B0 Full history                               | 47.8 [40.0, 55.6] | 50.6 [43.3, 58.3] | 48.3 [41.1, 56.1] | 58.2 [51.7, 64.6] | 57.5 [47.5, 66.7] | 46.7 [33.3, 60.0] |
| B1 Rolling, B                                 | 42.8 [35.6, 50.0] | 36.7 [30.0, 43.9] | 0.0 [0.0, 2.0]    | 0.0 [0.0, 2.1]    | 0.0 [0.0, 3.0]    | 0.0 [0.0, 6.0]    |
| B2 Vector memory                              | 71.1 [64.4, 77.8] | 66.1 [59.4, 72.2] | 71.1 [64.4, 77.8] | 72.9 [66.9, 78.8] | 64.2 [54.2, 73.3] | 63.3 [51.7, 75.0] |
| B3 Generic RAG                                | 38.3 [31.7, 45.0] | 32.2 [26.1, 38.3] | 34.4 [28.3, 41.1] | 41.2 [33.9, 48.9] | 38.3 [30.8, 45.8] | 38.3 [26.7, 50.0] |
| B4 Scored memory stream (Generative Agents)   | 67.8 [61.1, 74.4] | 65.0 [57.8, 72.2] | 71.1 [64.4, 77.2] | 64.4 [57.1, 71.4] | 33.3 [25.0, 41.7] | 15.0 [6.7, 25.0]  |
| B5 Forgetting-curve memory (MemoryBank)       | 71.7 [64.4, 78.3] | 66.1 [59.4, 72.8] | 70.0 [63.3, 76.7] | 63.3 [56.3, 70.2] | 49.2 [39.2, 59.2] | 48.3 [35.0, 61.7] |
| A1 No long-term memory                        | 41.7 [35.6, 47.8] | 0.0 [0.0, 2.0]    | 0.0 [0.0, 2.0]    | 0.0 [0.0, 2.1]    | 0.0 [0.0, 3.0]    | 0.0 [0.0, 6.0]    |
| A2 No short-term buffer                       | 74.4 [67.8, 80.6] | 69.4 [62.2, 76.1] | 66.7 [59.4, 73.9] | 73.4 [66.9, 79.8] | 66.7 [57.5, 75.8] | 56.7 [45.0, 68.3] |
| A3 No scoping                                 | 41.1 [32.8, 49.4] | 58.9 [52.2, 65.6] | 62.8 [55.6, 70.0] | 66.7 [59.9, 73.4] | 60.8 [50.8, 70.0] | 58.3 [45.0, 70.0] |
| A4 No fallback                                | 32.2 [25.6, 38.9] | 56.7 [49.4, 63.9] | 61.1 [53.3, 68.9] | 68.9 [62.1, 75.7] | 67.5 [57.5, 76.7] | 58.3 [45.0, 71.7] |
| A8 No budget (F4 retrieval, unpacked context) | 51.7 [45.0, 58.3] | 46.1 [39.4, 52.8] | 60.0 [52.2, 67.8] | 66.7 [59.8, 73.4] | 63.3 [54.2, 72.5] | 50.0 [38.3, 61.7] |
| n (F4 probes)                                 | 180               | 180               | 180               | 177               | 120               | 60                |

## Table 3: Factorial separation (memory x control, live)

| Cell                  | Recall, live probes (%) | New violations per 100 committed transitions | Turns in a corrupted state (%) | Scripted moves committed by the model (%) | False rejection, probes: lawful / by intent (%) | False rejection by intent, live (%) | Desync rate, non-move turns (%) | Sessions |
| --------------------- | ----------------------- | -------------------------------------------- | ------------------------------ | ----------------------------------------- | ----------------------------------------------- | ----------------------------------- | ------------------------------- | -------- |
| F1 rolling, direct    | 0.0 [0.0, 6.4]          | 77.7 [68.8, 86.6]                            | 24.5 [16.5, 33.9]              | 4.9 [0.9, 10.4]                           | n/a                                             | n/a                                 | 0.9 [0.0, 2.0]                  | 14       |
| F2 rolling, barrier   | 0.0 [0.0, 6.4]          | 0.0 [0.0, 10.6]                              | 0.0 [0.0, 0.7]                 | 2.9 [0.0, 6.2]                            | 0.0 [0.0, 1.4] / 20.0 [12.3, 29.3]              | 61.6 [48.4, 77.8]                   | 2.9 [1.5, 4.4]                  | 14       |
| F3 dual-tier, direct  | 46.4 [30.4, 62.5]       | 79.2 [69.5, 88.1]                            | 33.7 [18.7, 49.8]              | 3.9 [0.9, 8.0]                            | n/a                                             | n/a                                 | 0.9 [0.0, 2.0]                  | 14       |
| F4 dual-tier, barrier | 48.2 [37.5, 60.7]       | 0.0 [0.0, 11.9]                              | 0.0 [0.0, 0.7]                 | 2.9 [0.0, 6.5]                            | 0.0 [0.0, 1.4] / 20.0 [12.3, 29.3]              | 63.7 [53.8, 76.3]                   | 3.6 [2.1, 5.1]                  | 14       |

## Table 3b: Simple effects and interaction contrast (live, per session, pp)

| outcome   | contrast                                 | n_sessions | effect               | p_wilcoxon |
| --------- | ---------------------------------------- | ---------- | -------------------- | ---------- |
| recall    | memory effect \| direct writes (F3 - F1) | 14         | +46.4 [+30.4, +62.5] | 0.001275   |
| recall    | memory effect \| barrier (F4 - F2)       | 14         | +48.2 [+37.5, +60.7] | 0.0008312  |
| recall    | control effect \| rolling (F2 - F1)      | 14         | +0.0 [+0.0, +0.0]    | 1          |
| recall    | control effect \| dual-tier (F4 - F3)    | 14         | +1.8 [-8.9, +12.5]   | 0.923      |
| recall    | interaction ((F4 - F2) - (F3 - F1))      | 14         | +1.8 [-8.9, +12.5]   | 0.923      |
| violation | memory effect \| direct writes (F3 - F1) | 14         | -1.9 [-12.6, +8.0]   | 1          |
| violation | memory effect \| barrier (F4 - F2)       | 14         | +0.0 [+0.0, +0.0]    | 1          |
| violation | control effect \| rolling (F2 - F1)      | 14         | -78.9 [-87.9, -69.6] | 0.0009507  |
| violation | control effect \| dual-tier (F4 - F3)    | 14         | -77.0 [-87.3, -66.2] | 0.0009479  |
| violation | interaction ((F4 - F2) - (F3 - F1))      | 14         | +1.9 [-8.0, +12.7]   | 1          |

## Table 3c: Live recall diagnostics

| Condition | Live probes | Recall (%)        | Plant summary keeps the value (%) | Plant memory retrieved (%) | Recall when retrieved (%) | Recall when not retrieved (%) |
| --------- | ----------- | ----------------- | --------------------------------- | -------------------------- | ------------------------- | ----------------------------- |
| F1        | 56          | 0.0 [0.0, 6.4]    | 76.8 [66.1, 85.7]                 | 0.0 [0.0, 6.4]             | n/a                       | 0.0 [0.0, 6.4]                |
| F2        | 56          | 0.0 [0.0, 6.4]    | 80.4 [71.4, 89.3]                 | 0.0 [0.0, 6.4]             | n/a                       | 0.0 [0.0, 6.4]                |
| F3        | 56          | 46.4 [30.4, 62.5] | 80.4 [67.9, 91.1]                 | 100.0 [93.6, 100.0]        | 46.4 [30.4, 62.5]         | n/a                           |
| F4        | 56          | 48.2 [37.5, 60.7] | 80.4 [71.4, 89.3]                 | 100.0 [93.6, 100.0]        | 48.2 [37.5, 60.7]         | n/a                           |
| F4v1      | 56          | 48.2 [28.6, 67.9] | 80.4 [66.1, 92.9]                 | 100.0 [93.6, 100.0]        | 48.2 [28.6, 67.9]         | n/a                           |
| A5        | 56          | 57.1 [44.6, 69.6] | 76.8 [66.1, 85.7]                 | 100.0 [93.6, 100.0]        | 57.1 [44.6, 69.6]         | n/a                           |
| A6        | 56          | 44.6 [35.7, 53.6] | 73.2 [62.5, 82.1]                 | 100.0 [93.6, 100.0]        | 44.6 [35.7, 53.6]         | n/a                           |

## Table 4: Ablations

| Ablation                                      | Recall, age 20+ (%)                  | MRR@6                | Committed violations per 100 transitions    | Local compute P50 (ms) | Recovery at turn 160 (ms)             | Replay consistency (%)               |
| --------------------------------------------- | ------------------------------------ | -------------------- | ------------------------------------------- | ---------------------- | ------------------------------------- | ------------------------------------ |
| Full system (F4)                              | 63.7 [59.4, 68.0]                    | 0.805 [0.787, 0.824] | probes 0.0 [0.0, 1.1]; live 0.0 [0.0, 11.9] | 25.6                   | 1.4 (snapshot) vs 244.2 (full replay) | 100.0 [76.8, 100.0]                  |
| A1 No long-term memory                        | 0.0 [0.0, 0.7]                       | n/a                  | same as full system (memory-only change)    | n/a                    | n/a                                   | as full system                       |
| A2 No short-term buffer                       | 67.8 [63.8, 71.8]                    | 0.751 [0.732, 0.772] | same as full system (memory-only change)    | n/a                    | n/a                                   | as full system                       |
| A3 No scoping                                 | 63.1 [59.1, 67.1]                    | 0.742 [0.721, 0.764] | same as full system (memory-only change)    | n/a                    | n/a                                   | as full system                       |
| A4 No fallback                                | 64.8 [60.5, 69.2]                    | 0.815 [0.798, 0.834] | same as full system (memory-only change)    | n/a                    | n/a                                   | as full system                       |
| A8 No budget (F4 retrieval, unpacked context) | 61.8 [57.6, 66.0]                    | 0.751 [0.732, 0.772] | same as full system (memory-only change)    | n/a                    | n/a                                   | as full system                       |
| A5 No validation barrier                      | as full system (control-only change) | as full system       | probes 4.4 [0.5, 9.7]; live 1.9 [0.0, 4.5]  | 22.6                   | 1.4 (snapshot) vs 244.2 (full replay) | 100.0 [76.8, 100.0]                  |
| A6 No event sourcing                          | as full system                       | as full system       | live 0.0 [0.0, 13.2]                        | 9.6                    | no log to recover from                | not replayable                       |
| A7 No snapshots                               | as full system                       | as full system       | as full system                              | n/a                    | 244.2                                 | 100 (full fold, CPU replay sessions) |

## Table 5: Adversarial probes by category

| Category    | n attacks | Attack success, direct writes (%) | Attack success, reducer only A5 (%) | Attack success, barrier v1 (%) | Attack success, barrier v2 (%) | Attack success, v2 + canonicaliser (%) | False rejection of lawful twin (%) | Validator gap v1 (%) | Validator gap v2 (%) |
| ----------- | --------- | --------------------------------- | ----------------------------------- | ------------------------------ | ------------------------------ | -------------------------------------- | ---------------------------------- | -------------------- | -------------------- |
| teleport    | 154       | 3.2 [0.6, 6.5]                    | 0.0 [0.0, 2.4]                      | 0.0 [0.0, 2.4]                 | 0.0 [0.0, 2.4]                 | 0.0 [0.0, 2.4]                         | 0.0 [0.0, 11.2]                    | 4.0 [0.0, 10.2]      | 0.0 [0.0, 7.1]       |
| fabrication | 154       | 1.9 [0.0, 4.5]                    | 0.0 [0.0, 2.4]                      | 0.0 [0.0, 2.4]                 | 0.0 [0.0, 2.4]                 | 0.0 [0.0, 2.4]                         | 0.0 [0.0, 3.4]                     | 4.5 [0.0, 15.4]      | 0.0 [0.0, 15.4]      |
| theft       | 154       | 9.7 [5.2, 14.9]                   | 0.0 [0.0, 2.4]                      | 0.0 [0.0, 2.4]                 | 0.0 [0.0, 2.4]                 | 0.0 [0.0, 2.4]                         | 0.0 [0.0, 5.2]                     | 4.3 [0.0, 15.4]      | 0.0 [0.0, 14.8]      |
| trust       | 154       | 0.6 [0.0, 1.9]                    | 0.6 [0.0, 1.9]                      | 0.0 [0.0, 2.4]                 | 0.0 [0.0, 2.4]                 | 0.0 [0.0, 2.4]                         | 0.0 [0.0, 41.0]                    | 0.0 [0.0, 97.5]      | 0.0 [0.0, 97.5]      |
| currency    | 154       | 13.0 [7.8, 18.2]                  | 12.3 [7.1, 17.5]                    | 5.8 [2.6, 9.7]                 | 0.0 [0.0, 2.4]                 | 0.0 [0.0, 2.4]                         | 0.0 [0.0, 10.9]                    | 47.6 [25.0, 71.4]    | 0.0 [0.0, 16.1]      |
| injection   | 154       | 0.0 [0.0, 2.4]                    | 0.0 [0.0, 2.4]                      | 0.0 [0.0, 2.4]                 | 0.0 [0.0, 2.4]                 | 0.0 [0.0, 2.4]                         | n/a (no lawful proposals)          | n/a                  | n/a                  |
| secret      | 154       | 1.9 [0.0, 4.5]                    | 1.3 [0.0, 3.2]                      | 1.3 [0.0, 3.2]                 | 1.3 [0.0, 3.2]                 | 1.3 [0.0, 3.2]                         | 0.0 [0.0, 18.5]                    | 100.0 [100.0, 100.0] | 0.0 [0.0, 97.5]      |
| all         | 1078      | 4.4 [2.3, 6.8]                    | 2.0 [0.4, 4.2]                      | 1.0 [0.1, 2.7]                 | 0.2 [0.0, 0.5]                 | 0.2 [0.0, 0.5]                         | 0.0 [0.0, 1.4]                     | 12.7 [2.6, 28.2]     | 0.0 [0.0, 3.1]       |

## Table 5b: Grounding errors and the canonicalising barrier (probes)

| Context | Proposals | Lawful as written | Lawful by intent | Intent rejected, shipped barrier (%) | Intent rejected, with canonicaliser (%) | Validator gap, with canonicaliser (%) | Attack success, with canonicaliser (%) |
| ------- | --------- | ----------------- | ---------------- | ------------------------------------ | --------------------------------------- | ------------------------------------- | -------------------------------------- |
| F4      | 453       | 335               | 408              | 17.9 [11.3, 25.7]                    | 0.0 [0.0, 0.9]                          | 0.0 [0.0, 7.9]                        | 0.2 [0.0, 0.5]                         |

## Table 5c: Validator differential test (random proposals, oracle-labelled)

| type                            | proposals | lawful | gap v2 (%)                  | false rejection v2 (%)     | gap v1 (%)                         | false rejection v1 (%)        | gap v2 by intent (%)        | false rejection v2 by intent (%) | gap canon by intent (%)     | false rejection canon by intent (%) | turns    | violating turns, barrier | violating turns, barrier_canon | violating turns, barrier_v1 |
| ------------------------------- | --------- | ------ | --------------------------- | -------------------------- | ---------------------------------- | ----------------------------- | --------------------------- | -------------------------------- | --------------------------- | ----------------------------------- | -------- | ------------------------ | ------------------------------ | --------------------------- |
| all                             | 33655     | 7382   | 0.00 [0.00, 0.01] (0/26273) | 0.08 [0.03, 0.18] (6/7382) | 51.71 [51.11, 52.32] (13587/26273) | 0.34 [0.22, 0.50] (25/7382)   | 0.00 [0.00, 0.01] (0/25488) | 9.69 [9.05, 10.35] (791/8167)    | 0.00 [0.00, 0.01] (0/25488) | 0.10 [0.04, 0.19] (8/8167)          |          |                          |                                |                             |
| CLUE_DISCOVERED                 | 2239      | 0      | 0.00 [0.00, 0.16] (0/2239)  | n/a                        | 100.00 [99.84, 100.00] (2239/2239) | n/a                           | 0.00 [0.00, 0.16] (0/2239)  | n/a                              | 0.00 [0.00, 0.16] (0/2239)  | n/a                                 |          |                          |                                |                             |
| CLUE_LINKED                     | 2322      | 0      | 0.00 [0.00, 0.16] (0/2322)  | n/a                        | 100.00 [99.84, 100.00] (2322/2322) | n/a                           | 0.00 [0.00, 0.16] (0/2322)  | n/a                              | 0.00 [0.00, 0.16] (0/2322)  | n/a                                 |          |                          |                                |                             |
| CURRENCY_CHANGED                | 2191      | 1231   | 0.00 [0.00, 0.38] (0/960)   | 0.00 [0.00, 0.30] (0/1231) | 56.98 [53.78, 60.14] (547/960)     | 0.00 [0.00, 0.30] (0/1231)    | 0.00 [0.00, 0.38] (0/960)   | 0.00 [0.00, 0.30] (0/1231)       | 0.00 [0.00, 0.38] (0/960)   | 0.00 [0.00, 0.30] (0/1231)          |          |                          |                                |                             |
| JOURNAL_ENTRY_CREATED           | 2202      | 1117   | 0.00 [0.00, 0.34] (0/1085)  | 0.00 [0.00, 0.33] (0/1117) | 0.00 [0.00, 0.34] (0/1085)         | 0.00 [0.00, 0.33] (0/1117)    | 0.00 [0.00, 0.34] (0/1085)  | 0.00 [0.00, 0.33] (0/1117)       | 0.00 [0.00, 0.34] (0/1085)  | 0.00 [0.00, 0.33] (0/1117)          |          |                          |                                |                             |
| LOCATION_STATE_CHANGED          | 2268      | 1322   | 0.00 [0.00, 0.39] (0/946)   | 0.00 [0.00, 0.28] (0/1322) | 0.00 [0.00, 0.39] (0/946)          | 0.00 [0.00, 0.28] (0/1322)    | 0.00 [0.00, 0.61] (0/598)   | 20.84 [18.91, 22.87] (348/1670)  | 0.00 [0.00, 0.61] (0/598)   | 0.00 [0.00, 0.22] (0/1670)          |          |                          |                                |                             |
| NPC_SPOKE                       | 2269      | 0      | 0.00 [0.00, 0.16] (0/2269)  | n/a                        | 100.00 [99.84, 100.00] (2269/2269) | n/a                           | 0.00 [0.00, 0.16] (0/2269)  | n/a                              | 0.00 [0.00, 0.16] (0/2269)  | n/a                                 |          |                          |                                |                             |
| NPC_STATE_CHANGED               | 2198      | 866    | 0.00 [0.00, 0.28] (0/1332)  | 0.00 [0.00, 0.43] (0/866)  | 31.46 [28.97, 34.03] (419/1332)    | 0.00 [0.00, 0.43] (0/866)     | 0.00 [0.00, 0.33] (0/1109)  | 20.48 [18.12, 23.00] (223/1089)  | 0.00 [0.00, 0.33] (0/1109)  | 0.00 [0.00, 0.34] (0/1089)          |          |                          |                                |                             |
| OBJECT_DROPPED                  | 2223      | 142    | 0.00 [0.00, 0.18] (0/2081)  | 0.00 [0.00, 2.56] (0/142)  | 45.75 [43.59, 47.92] (952/2081)    | 0.00 [0.00, 2.56] (0/142)     | 0.00 [0.00, 0.18] (0/2070)  | 7.19 [3.64, 12.50] (11/153)      | 0.00 [0.00, 0.18] (0/2070)  | 0.00 [0.00, 2.38] (0/153)           |          |                          |                                |                             |
| OBJECT_TAKEN                    | 2165      | 101    | 0.00 [0.00, 0.18] (0/2064)  | 5.94 [2.21, 12.48] (6/101) | 5.57 [4.62, 6.65] (115/2064)       | 24.75 [16.70, 34.33] (25/101) | 0.00 [0.00, 0.18] (0/2051)  | 16.67 [10.34, 24.80] (19/114)    | 0.00 [0.00, 0.18] (0/2051)  | 7.02 [3.08, 13.36] (8/114)          |          |                          |                                |                             |
| PLAYER_FLAG_SET                 | 2281      | 1139   | 0.00 [0.00, 0.32] (0/1142)  | 0.00 [0.00, 0.32] (0/1139) | 0.00 [0.00, 0.32] (0/1142)         | 0.00 [0.00, 0.32] (0/1139)    | 0.00 [0.00, 0.32] (0/1142)  | 0.00 [0.00, 0.32] (0/1139)       | 0.00 [0.00, 0.32] (0/1142)  | 0.00 [0.00, 0.32] (0/1139)          |          |                          |                                |                             |
| PLAYER_MOVED                    | 2246      | 813    | 0.00 [0.00, 0.26] (0/1433)  | 0.00 [0.00, 0.45] (0/813)  | 0.00 [0.00, 0.26] (0/1433)         | 0.00 [0.00, 0.45] (0/813)     | 0.00 [0.00, 0.26] (0/1406)  | 3.21 [2.13, 4.64] (27/840)       | 0.00 [0.00, 0.26] (0/1406)  | 0.00 [0.00, 0.44] (0/840)           |          |                          |                                |                             |
| RELATIONSHIP_CHANGED            | 2282      | 651    | 0.00 [0.00, 0.23] (0/1631)  | 0.00 [0.00, 0.57] (0/651)  | 12.63 [11.06, 14.34] (206/1631)    | 0.00 [0.00, 0.57] (0/651)     | 0.00 [0.00, 0.25] (0/1468)  | 20.02 [17.33, 22.94] (163/814)   | 0.00 [0.00, 0.25] (0/1468)  | 0.00 [0.00, 0.45] (0/814)           |          |                          |                                |                             |
| SESSION_END                     | 2260      | 0      | 0.00 [0.00, 0.16] (0/2260)  | n/a                        | 100.00 [99.84, 100.00] (2260/2260) | n/a                           | 0.00 [0.00, 0.16] (0/2260)  | n/a                              | 0.00 [0.00, 0.16] (0/2260)  | n/a                                 |          |                          |                                |                             |
| SESSION_START                   | 2258      | 0      | 0.00 [0.00, 0.16] (0/2258)  | n/a                        | 100.00 [99.84, 100.00] (2258/2258) | n/a                           | 0.00 [0.00, 0.16] (0/2258)  | n/a                              | 0.00 [0.00, 0.16] (0/2258)  | n/a                                 |          |                          |                                |                             |
| UNKNOWN_TYPE                    | 2251      | 0      | 0.00 [0.00, 0.16] (0/2251)  | n/a                        | 0.00 [0.00, 0.16] (0/2251)         | n/a                           | 0.00 [0.00, 0.16] (0/2251)  | n/a                              | 0.00 [0.00, 0.16] (0/2251)  | n/a                                 |          |                          |                                |                             |
| turn-level (whole turn audited) | 33655     |        |                             |                            |                                    |                               |                             |                                  |                             |                                     | 1.68e+04 | 0                        | 0                              | 1485                        |

## Table 6: Per-stage latency (proposed system, single stream)

| Stage      | P50 (ms) | P95 (ms)  | P99 (ms)  | n turns |
| ---------- | -------- | --------- | --------- | ------- |
| input      | 0.002    | 0.002     | 0.003     | 24      |
| retrieval  | 0.146    | 0.215     | 0.24      | 24      |
| prompt     | 0.123    | 0.151     | 0.159     | 24      |
| llm        | 7410     | 1.489e+04 | 1.708e+04 | 24      |
| parse      | 0.077    | 0.104     | 0.109     | 24      |
| validate   | 0.013    | 0.958     | 1.249     | 24      |
| repair     | 0.002    | 5912      | 7449      | 24      |
| commit     | 8.872    | 16.52     | 18.74     | 24      |
| output     | 0.011    | 0.012     | 0.013     | 24      |
| local      | 15.03    | 22.44     | 25.01     | 24      |
| end to end | 7600     | 1.5e+04   | 2.318e+04 | 24      |

## Table 7: Per-world and backbone breakdown

| World  | Backbone        | Recall 20+: F4     | Recall 20+: best baseline | Attack success: F4 barrier | Attack success: best baseline (direct) |
| ------ | --------------- | ------------------ | ------------------------- | -------------------------- | -------------------------------------- |
| W1     | K2-Horizon-7B   | 62.5 [53.1, 72.5]  | B2: 60.2 [49.0, 71.7]     | 0.6 [0.0, 2.0]             | F4 outputs: 14.9 [7.1, 24.1]           |
| W2a    | K2-Horizon-7B   | 62.9 [51.9, 74.3]  | B2: 73.0 [66.7, 80.2]     | 0.0 [0.0, 2.4]             | F4 outputs: 3.9 [0.7, 7.9]             |
| W2b    | K2-Horizon-7B   | 64.4 [51.1, 76.1]  | B2: 72.2 [62.5, 81.4]     | 0.0 [0.0, 2.4]             | F4 outputs: 5.2 [1.4, 9.7]             |
| W2c    | K2-Horizon-7B   | 63.3 [55.7, 72.2]  | B2: 71.1 [62.7, 79.8]     | 0.0 [0.0, 2.4]             | F4 outputs: 0.6 [0.0, 2.1]             |
| W3     | K2-Horizon-7B   | 68.9 [61.5, 76.8]  | B2: 68.9 [57.4, 81.0]     | 0.0 [0.0, 2.4]             | F4 outputs: 1.9 [0.0, 4.5]             |
| W4-32  | K2-Horizon-7B   | 73.3 [61.9, 83.7]  | B2: 67.8 [58.7, 76.7]     | 0.0 [0.0, 2.4]             | F4 outputs: 2.6 [0.6, 5.2]             |
| W4-128 | K2-Horizon-7B   | 48.9 [42.5, 56.0]  | B2: 62.5 [53.4, 71.3]     | 0.6 [0.0, 2.2]             | F4 outputs: 1.3 [0.0, 3.4]             |
| W1     | K2-Horizon-3.7B | 72.2 [50.0, 83.3]  | B2: 72.2 [66.7, 83.3]     | 0.0 [0.0, 3.7]             | F4 outputs: 13.3 [4.1, 24.8]           |
| W2a    | K2-Horizon-3.7B | 83.3 [66.7, 100.0] | B5: 88.9 [83.3, 100.0]    | 0.0 [0.0, 3.7]             | F4 outputs: 13.3 [3.2, 26.1]           |
| W3     | K2-Horizon-3.7B | 61.1 [50.0, 66.7]  | B5: 55.6 [50.0, 66.7]     | 0.0 [0.0, 3.7]             | F4 outputs: 7.1 [1.9, 14.0]            |
| W4-32  | K2-Horizon-3.7B | 61.1 [33.3, 83.3]  | B0: 72.2 [50.0, 100.0]    | 0.0 [0.0, 3.7]             | F4 outputs: 4.1 [0.0, 9.7]             |
| W1     | qwen2.5-7b      | 77.8 [66.7, 83.3]  | B2: 77.8 [66.7, 83.3]     | 0.0 [0.0, 3.7]             | F4 outputs: 62.2 [46.7, 76.5]          |
| W2a    | qwen2.5-7b      | 88.9 [83.3, 100.0] | B2: 100.0 [81.5, 100.0]   | 0.0 [0.0, 3.7]             | F4 outputs: 54.1 [40.2, 69.0]          |
| W3     | qwen2.5-7b      | 83.3 [83.3, 83.3]  | B2: 88.9 [83.3, 100.0]    | 0.0 [0.0, 3.7]             | F4 outputs: 36.7 [21.0, 54.1]          |
| W4-32  | qwen2.5-7b      | 61.1 [33.3, 83.3]  | B2: 83.3 [66.7, 100.0]    | 0.0 [0.0, 3.7]             | F4 outputs: 44.9 [29.9, 59.8]          |
| W1     | phi4-mini       | 66.7 [16.7, 100.0] | B5: 72.2 [66.7, 83.3]     | 0.0 [0.0, 3.7]             | F4 outputs: 28.6 [17.0, 41.4]          |
| W2a    | phi4-mini       | 83.3 [66.7, 100.0] | B2: 77.8 [66.7, 83.3]     | 0.0 [0.0, 3.7]             | F4 outputs: 22.4 [11.9, 35.0]          |
| W3     | phi4-mini       | 77.8 [66.7, 83.3]  | B2: 61.1 [33.3, 83.3]     | 0.0 [0.0, 3.7]             | F4 outputs: 26.5 [14.6, 40.2]          |
| W4-32  | phi4-mini       | 72.2 [50.0, 83.3]  | B2: 72.2 [66.7, 83.3]     | 0.0 [0.0, 3.7]             | F4 outputs: 31.6 [17.8, 46.6]          |

## Table 2b: Recall by fact type (held-out, age 20+)

| Condition                                     | Plain facts (%)   | Knowledge updates (%) | Outdated answers on updates (%) | With a lure turn (%) | Lenient recall (%) | Adjudicated recall (%) | Hedged replies (%) |
| --------------------------------------------- | ----------------- | --------------------- | ------------------------------- | -------------------- | ------------------ | ---------------------- | ------------------ |
| Proposed (dual-tier + barrier)                | 79.1 [73.2, 84.9] | 20.7 [14.3, 27.7]     | 4.3 [1.4, 7.8]                  | 64.7 [58.9, 70.6]    | 83.1 [80.0, 86.0]  | 74.3 [70.8, 77.9]      | 19.2 [16.0, 22.3]  |
| Proposed before revision (Review-02)          | 80.1 [74.2, 85.7] | 18.6 [12.1, 25.8]     | 4.3 [1.4, 7.8]                  | 62.7 [56.9, 68.7]    | 83.1 [80.3, 85.7]  | 74.7 [71.1, 78.2]      | 19.4 [16.2, 22.5]  |
| B0 Full history                               | 71.4 [64.5, 78.1] | 25.7 [18.9, 32.9]     | 15.0 [9.6, 21.1]                | 48.4 [42.3, 54.6]    | 65.4 [61.3, 69.5]  | 58.7 [54.1, 63.3]      | 11.9 [9.3, 14.7]   |
| B1 Rolling, B                                 | 0.0 [0.0, 1.8]    | 0.0 [0.0, 2.6]        | 0.0 [0.0, 2.6]                  | 0.0 [0.0, 1.5]       | 0.0 [0.0, 0.7]     | 0.0 [0.0, 0.7]         | 0.0 [0.0, 0.7]     |
| B2 Vector memory                              | 87.4 [83.0, 91.6] | 20.7 [14.3, 27.8]     | 3.6 [0.7, 6.9]                  | 68.7 [62.5, 74.9]    | 86.0 [83.0, 89.0]  | 80.6 [77.3, 83.8]      | 16.8 [13.4, 20.2]  |
| B3 Generic RAG                                | 48.1 [41.7, 54.5] | 22.9 [16.5, 29.5]     | 3.6 [0.7, 6.8]                  | 34.1 [28.7, 39.7]    | 65.2 [61.3, 69.2]  | 44.9 [41.0, 48.8]      | 26.8 [23.3, 30.5]  |
| B4 Scored memory stream (Generative Agents)   | 63.1 [55.7, 70.7] | 25.7 [18.4, 33.3]     | 10.0 [5.3, 15.6]                | 55.2 [48.8, 61.6]    | 65.5 [61.7, 69.4]  | 60.3 [56.2, 64.5]      | 11.2 [8.7, 13.7]   |
| B5 Forgetting-curve memory (MemoryBank)       | 77.2 [71.6, 82.6] | 14.3 [9.4, 19.4]      | 4.3 [1.4, 7.6]                  | 61.9 [55.4, 68.6]    | 79.5 [75.8, 83.0]  | 72.8 [68.8, 76.8]      | 18.8 [16.1, 21.5]  |
| A1 No long-term memory                        | 0.0 [0.0, 1.8]    | 0.0 [0.0, 2.6]        | 0.0 [0.0, 2.6]                  | 0.0 [0.0, 1.5]       | 0.0 [0.0, 0.7]     | 0.0 [0.0, 0.7]         | 0.0 [0.0, 0.7]     |
| A2 No short-term buffer                       | 87.4 [82.7, 91.8] | 15.7 [9.9, 22.1]      | 2.1 [0.0, 4.7]                  | 69.0 [63.5, 74.7]    | 85.7 [82.3, 88.8]  | 81.4 [78.1, 84.6]      | 17.9 [14.6, 21.1]  |
| A3 No scoping                                 | 79.6 [73.9, 85.1] | 20.7 [14.7, 27.5]     | 7.1 [3.4, 11.3]                 | 62.3 [56.7, 67.9]    | 78.6 [75.4, 81.7]  | 73.7 [70.3, 77.1]      | 15.3 [12.4, 18.2]  |
| A4 No fallback                                | 81.1 [75.2, 86.8] | 20.7 [14.4, 27.5]     | 3.6 [0.7, 6.8]                  | 65.5 [59.8, 71.2]    | 84.4 [81.2, 87.4]  | 75.8 [72.2, 79.4]      | 19.4 [16.2, 22.5]  |
| A8 No budget (F4 retrieval, unpacked context) | 77.2 [71.6, 82.7] | 18.6 [12.6, 25.4]     | 5.0 [1.7, 8.5]                  | 63.9 [57.5, 70.0]    | 81.2 [77.9, 84.4]  | 72.6 [68.8, 76.3]      | 18.8 [15.7, 22.0]  |

## Table 8b: Contradiction judges on control items with a known verdict

| judge      | n   | judged | accuracy | sensitivity | specificity |
| ---------- | --- | ------ | -------- | ----------- | ----------- |
| qwen2.5-7b | 27  | 27     | 0.8148   | 0.8333      | 0.8         |
| phi4-mini  | 27  | 27     | 0.5556   | 1           | 0.2         |

## Table 8: Before and after the Review-03 corrections (paired, same oracle)

| test | metric                                                             | before                 | after                 | n    | effect_pp | p_raw     | p_holm    |
| ---- | ------------------------------------------------------------------ | ---------------------- | --------------------- | ---- | --------- | --------- | --------- |
| R1   | attack success, all categories                                     | 1.0 [0.1, 2.7]         | 0.2 [0.0, 0.5]        | 1078 | 0.83      | 0.003906  | 0.03125   |
| R1   | attack success, currency                                           | 5.8 [0.0, 16.6]        | 0.0 [0.0, 2.4]        | 154  | 5.84      | 0.003906  | 0.03125   |
| R1   | validator gap, currency proposals                                  | 47.6 [0.0, 96.3]       | 0.0 [0.0, 16.1]       |      |           |           |           |
| R1   | validator gap, all proposals                                       | 12.7 [2.6, 28.2]       | 0.0 [0.0, 3.1]        |      |           |           |           |
| R1   | false rejection of lawful twins                                    | 0.0 [0.0, 1.4]         | 0.0 [0.0, 1.4]        |      |           |           |           |
| R2   | crash trials recovered inconsistently                              | 69.0% (5.9 turns lost) | 0.0% (0.0 turns lost) | 300  | 69        | 9.723e-63 | 8.751e-62 |
| R2   | load path after a crash (replay sessions)                          | 0% consistent          | 100% consistent       |      |           |           |           |
| R3   | judge contradiction, repaired probes                               | 48.7%                  | 47.0%                 | 117  | 1.71      | 0.8145    | 1         |
| R3   | judge contradiction, repaired live F4 turns                        | 10.0%                  | 5.0%                  | 20   | 5         | 1         | 1         |
| R3   | judge contradiction per judged live turn, F4v1 vs F4 (per session) | 38.9%                  | 8.0%                  | 7    | 38.1      | 0.0625    | 0.3125    |
| R3   | desync proxy, live F4 turns (draft vs repaired)                    | 3.6%                   | 3.6%                  | 444  | 0         | 1         | 1         |
| R3   | desync proxy per live turn, F4v1 vs F4 (per session)               | 4.1 [2.3, 6.1]         | 3.6 [2.1, 5.1]        | 14   | 0.43      | 0.7279    | 1         |
| R4   | committed violations per 100 transitions, F4v1 vs F4 (per session) | 13.0 [4.3, 22.2]       | 0.0 [0.0, 11.9]       | 14   | 10.36     | 0.05194   | 0.3117    |

## Hypothesis verdicts

| hypothesis                             | verdict                                                      | evidence                                                                                                                                                                                                                                                    |
| -------------------------------------- | ------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| H1a Memory, superiority over B1 and B3 | supported (recall) but token-cost condition vs B2/B3 not met | F4 input tokens 1468 vs B2 1456, B3 1516                                                                                                                                                                                                                    |
| H1b Memory, non-inferiority to B2      | not supported                                                | margin 5 pp; recall 20+ F4 vs B2, non-inferiority margin 5 pp (one-sided lower bound -9.1 pp)                                                                                                                                                               |
| H2 Retrieval                           | not supported                                                | per-probe reciprocal rank, Wilcoxon                                                                                                                                                                                                                         |
| H3 State control                       | supported                                                    | probes McNemar + live Wilcoxon                                                                                                                                                                                                                              |
| H4 Cost of control                     | not supported                                                | false rejection by intent 20.0 [12.3, 29.3]% (strict 0.0 [0.0, 1.4]%); validate P95 0.958 ms                                                                                                                                                                |
| H5 Replay                              | supported                                                    | live event-sourced sessions all consistent: True; CPU replay, restart, backend load path after a crash and 300 randomised crash trials all consistent: True                                                                                                 |
| H6 Separability                        | supported                                                    | memory->recall coef 0.46 (p=8.56e-05); control->violation coef -0.15 (p=2.08e-07); interaction p recall=0.754, violation=1                                                                                                                                  |
| H7 Generalisation                      | supported                                                    | W2 LIGHT-derived: dRecall=+0.636, dAttack=+0.032; W3 held-out genre: dRecall=+0.689, dAttack=+0.019; W4 procedural: dRecall=+0.612, dAttack=+0.016; backbone qwen2.5-7b: dRecall=+0.778, dAttack=+0.495; backbone phi4-mini: dRecall=+0.750, dAttack=+0.273 |
| R1 Currency invariant                  | confirmed (no failure after the correction)                  | v2 currency validator gap 0.0 [0.0, 16.1]%                                                                                                                                                                                                                  |
| R2 Snapshot recovery                   | confirmed (no failure after the correction)                  | 300/300 crash trials consistent after the correction                                                                                                                                                                                                        |
| R3 Dialogue repair                     | not confirmed                                                | draft vs repaired (judge, proxy) and F4v1 vs F4                                                                                                                                                                                                             |
| R4 Committed violations                | not confirmed                                                | F4v1 vs F4, live, per session                                                                                                                                                                                                                               |

## Confirmatory tests

| hypothesis | test                                                                             | n    | effect  | p_raw  | direction_ok | p_holm |
| ---------- | -------------------------------------------------------------------------------- | ---- | ------- | ------ | ------------ | ------ |
| H1a        | recall 20+ F4 vs B1 (McNemar)                                                    | 537  | 0.6369  | 0      | True         | 0      |
| H1a        | recall 20+ F4 vs B3 (McNemar)                                                    | 537  | 0.257   | 0      | True         | 0      |
| H1b        | recall 20+ F4 vs B2, non-inferiority margin 5 pp (one-sided lower bound -9.1 pp) | 537  | -0.0559 | 0.6062 | False        | 0.6062 |
| H2         | MRR@6 F4 vs B2 (Wilcoxon, per probe)                                             | 717  | 0.0195  | 0.0326 | True         | 0.0653 |
| H3         | attack success direct vs barrier, F4 context (McNemar)                           | 1078 | 0.0417  | 0      | True         | 0      |
| H3         | live violations per transition F3 vs F4 (Wilcoxon, per session)                  | 14   | 0.7705  | 0.0009 | True         | 0.0028 |

## Exploratory memory tests

| test                                                                                                | n   | effect  | p_raw  | p_holm |
| --------------------------------------------------------------------------------------------------- | --- | ------- | ------ | ------ |
| recall 20+ F4 vs B2 (McNemar)                                                                       | 537 | -0.0559 | 0.0064 | 0.0445 |
| recall 20+ F4 vs B4 (McNemar)                                                                       | 537 | 0.095   | 0.0001 | 0.0011 |
| recall 20+ F4 vs B5 (McNemar)                                                                       | 537 | 0.0298  | 0.1847 | 1      |
| recall 20+ F4 vs F4v1 (McNemar)                                                                     | 537 | 0.0037  | 0.917  | 1      |
| recall 20+ F4 vs A3 (McNemar)                                                                       | 537 | 0.0056  | 0.8243 | 1      |
| recall 20+ F4 vs A8 (McNemar)                                                                       | 537 | 0.0186  | 0.2954 | 1      |
| recall 20+ A8 vs F4v1 (McNemar)                                                                     | 537 | -0.0149 | 0.4557 | 1      |
| sensitivity: recall 20+ F4 vs B2, adjudicated, non-inferiority 5 pp (one-sided lower bound -9.8 pp) | 537 | -0.0633 | 0.7316 | 1      |

## Contradiction judges: agreement

| source         | n_items | agreement | kappa  | rate_qwen2.5-7b | rate_phi4-mini |
| -------------- | ------- | --------- | ------ | --------------- | -------------- |
| all items      | 329     | 0.5562    | 0.224  | 0.3799          | 0.7994         |
| live_draft     | 20      | 0.4       | 0.0909 | 0.1             | 0.7            |
| live_final     | 75      | 0.6133    | 0.2339 | 0.1467          | 0.5067         |
| probe_draft    | 117     | 0.5812    | 0.1795 | 0.4872          | 0.906          |
| probe_repaired | 117     | 0.5214    | 0.0862 | 0.4701          | 0.8974         |

## Protocol amendments before this run

- fresh master seed: every benchmark instance is new to this run
- recall sessions: each attribute at most once per session (removes ambiguous probes), knowledge-update facts, topical lure turns and varied scripted replies
- recall scoring: strict (gold key present, distractor and outdated keys absent, parsed output); the old lenient rule is kept as a secondary column
- B4 includes the Generative Agents importance score, rated once per memory by the primary model
- A8 ablation (no context budget) separates packing from the prompt change between F4v1 and F4
- probe contexts reduced to F4 and B1; six attack templates per category; probe intervals clustered on template
- intent-level lawfulness and a canonicalising barrier variant measure rejections caused by display names
- validator differential test: oracle-labelled random proposals, exact binomial intervals
- live sessions: scripted travel is completed by the engine when the model does not commit it; new violations are counted per turn instead of persistent corruption; retrieval and summary diagnostics on live probes
- zero-event proportions reported with Clopper-Pearson intervals
- H1 split into superiority over B1 and B3 (H1a) and non-inferiority to B2 within 5 points (H1b); H6 tested as an additive interaction with a cluster-robust linear probability model
- second contradiction judge (Phi-4-mini) and Cohen's kappa between judges
- after run 4: fresh master seed 20261103
- after run 4: one probe context (F4); the B1 context sent identical prompts and duplicated every probe row
- after run 4: live sessions costed as throughput-bound; the run extends the sample level by level from measured per-job rates until the reserves are reached; the stopping rule uses elapsed time only
- after run 4: a finer ladder; the second backbone and the independent families capped at ladder level 2
- after run 4: hedged recall replies adjudicated by the first independent family as a sensitivity analysis; strict recall remains the confirmatory outcome
- after run 4: contradiction judges scored on control items; R3 uses judge verdicts only from a judge with at least 80% control accuracy
- after run 4: factorial model p values from a t reference with G - 1 degrees of freedom
- after run 4: every stage after the pilot runs under a guard that records failures, so outputs are always packaged

## Limitations of this run

- W3 authorship: notebook author (not independent; see caveat). The article requires an independent author; attach w3_world_seed.json to satisfy it.
- Recall, leaks and the desync proxy are scored automatically (key-word match, secret keywords, refusal/arrival cues); the judge (qwen2.5-7b: 329 items judged, 81% on control items; phi4-mini: 329 items judged, 56% on control items) is an LLM. Human evaluation: pending (no human_ratings_*.csv attached).
- Token cost is reported in tokens only; the models are self-hosted, so no provider list price applies.
- Latency was measured on 2x T4 with vLLM; hosted-endpoint latency is not reproduced.
- F4v1 reuses the corrected reducer, event store and commit node; it differs from F4 in the validator, the prompt builder, the unbudgeted memory assembly and the absence of dialogue repair. A8 separates the budget from the prompt for recall only; the validator and repair differences are not separated in live play.
- Live sessions: when the model does not commit a scripted move, the engine completes it, so all conditions follow one trajectory; model move compliance is reported separately and move turns are excluded from desynchronisation.
- B4 and B5 re-implement the Generative Agents and MemoryBank retrieval rules, not the full systems (no reflection or planning); B4's importance is rated once per memory text by the primary model and reused for the other backbones.
- Teacher-forced recall uses scripted memory summaries; live sessions use the model's own summaries, and the live diagnostics table separates summary loss from retrieval misses.
- The canonicalising barrier is a candidate fix evaluated offline on recorded outputs, not part of the shipped system.
- Intent-level lawfulness maps a reference to an id only by exact display name or slug; looser paraphrases count as unlawful, so intent-level false rejection is a lower bound.
- Recall sessions probe a fact with the NPC who heard it, at that NPC's location, which favours scoping; knowledge updates and lure turns are the only probes where scoping cannot separate the gold memory from competitors.
- Sample size: ladder level 5 of 11 ({'n_rec': 5, 'n_probe': 22, 'n_live': 2}): planned level 3, then 2 extension step(s) chosen by elapsed time only.
- Probes are sent under one context: a probe prompt is the same under every memory condition, so baselines commit the same outputs by direct writes and probe results do not separate the memory baselines.
- Contradiction judges on control items: qwen2.5-7b 81%, phi4-mini 56%; R3 judge rows used (threshold 80%).
- Recall adjudication (sensitivity analysis only): qwen2.5-7b: 1258 of 1258 hedged replies at age 20+ adjudicated.
- Second backbone: run on ['W1', 'W2a', 'W3', 'W4-32'] at ladder level 2. Independent families: {'qwen2.5-7b': "run on ['W1', 'W2a', 'W3', 'W4-32'] (horizon 100, ladder level 2)", 'phi4-mini': "run on ['W1', 'W2a', 'W3', 'W4-32'] (horizon 100, ladder level 2)"}.
