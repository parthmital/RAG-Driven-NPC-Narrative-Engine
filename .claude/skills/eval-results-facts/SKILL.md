---
name: eval-results-facts
description: Source of truth and known pitfalls for the evaluation numbers and engine behaviour cited in docs/paper, docs/research_article.md and README.md. Use whenever writing, checking or changing any metric, table, hypothesis verdict, sample size or claim about how the backend works.
---

# Evaluation facts

**Trust order:** `notebooks/outputs/predictions/` (raw) > `notebooks/outputs/metrics/*.csv` > `metrics/article_tables.md` > prose. Recompute before quoting:
`.venv/Scripts/python .claude/skills/eval-results-facts/scripts/recompute_paper_metrics.py --outputs notebooks/outputs`
Point estimates must match exactly; bootstrap CIs agree only to resampling noise.

## Scope traps

- Held-out worlds (W2a to W4-128): Tables 1 and 2, H1, H2, recall and token figures.
- All 7 worlds: H3 probe test (n=490, F4 context), Table 5 (5 contexts pooled, 350 attacks per category), and ablation probe rates.
- Live: 14 sessions per cell, 39 turns each, 56 live probes per cell.

## Easy-to-misstate facts

- Sample size: ladder level 2 of levels 0 to 7, so the third of eight, not the second.
- Live probes: recorded fact ages are 30 to 34 turns (`LIVE_FACT_AGES` in the config is unused).
- Theft twins: 50 of 70 in the run (71%); 294 of 420 (70%) in the full generated suite.
- Violations per 100 transitions can exceed 100 because the numerator counts flagged turns, and persistent corruption is re-flagged on every later turn.
- The factorial model is `BinomialBayesMixedGLM.fit_vb`: SE is a posterior SD and p is a posterior-z tail, not a Wald test.
- Trust attacks never exceeded +/-20, but injection outputs triggered O6 five times.
- Latency: B1 has 15 of 24 single-stream samples; B1x2 has 1; B2 and B3 were not measured. The live single-stream "llm" stage is a cache lookup.

## Backend facts (evaluated commit 0ea345f; only `llm/groq_client.py` changed since)

- The validator checks each proposal against the pre-turn state. Currency gains are unbounded. NPC `location_id` changes are accepted, and only the reducer ignores non-canonical ones.
- Retrieval post-filters the global top 5k, treats empty metadata as a wildcard, and the fallback below 3 results replaces the list rather than extending it.
- `SessionManager.load_session` drops the event suffix after the snapshot, and `active_npc_id` is set outside the event log.

## Sync rule

After changing any number or claim, grep `docs/paper/main.tex`, `docs/research_article.md` and `README.md` and update all three. README's "Repository metrics" counts go stale on every commit.
