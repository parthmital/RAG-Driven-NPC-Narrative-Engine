# Human evaluation protocol

This protocol goes with the blinded sheets that the evaluation notebook writes to `annotation/` (notebook section 11.1). It answers the Review-03 requirement for blinded human ratings of coherence, persona fidelity and state consistency, and it validates the two automatic scorers the paper relies on: the key-word recall scorer and the LLM contradiction judge.

## Raters

- Two raters, working independently. Neither may have built the engine or seen the key files.
- Each rater fills a separate copy of every sheet. Do not discuss items until both have finished.

## Blinding

The sheets list items in a shuffled order with no condition names. The mapping from `item` to condition is only in the `*_key.csv` files, which raters must not open. The notebook joins the keys back after rating.

## Sheets and scales

The third Review-03 run (24 to 25 October 2026) exported 200 dialogue-quality, 194 contradiction and 1,560 recall items to [`notebooks/outputs/annotation/`](../notebooks/outputs/annotation/). None has been rated yet.

### `dialogue_quality_sheet.csv`

One live game turn per row: the NPC's name and persona, what the player said, the game's reply, and the changes the engine committed and rejected that turn. Rate three columns from 1 (worst) to 5 (best):

| Column                   | Question                                                                                              | 1                                    | 5                                        |
| ------------------------ | ----------------------------------------------------------------------------------------------------- | ------------------------------------ | ---------------------------------------- |
| `coherence_1to5`         | Does the reply make sense as an answer to what the player said?                                       | Unrelated or self-contradictory      | A natural, relevant answer               |
| `persona_fidelity_1to5`  | Does the NPC sound like the persona described?                                                        | Out of character                     | Clearly this character                   |
| `state_consistency_1to5` | Does the reply agree with the committed changes, and avoid claiming a rejected or uncommitted change? | Claims something that did not happen | Fully consistent with what was committed |

`comment` is optional free text.

### `contradiction_sheet.csv`

One reply per row with the committed and rejected changes. Answer `contradiction_yes_no` with `yes` if the reply claims or clearly implies that a rejected change happened, or describes a change to the world (movement, items, money, trust) that is not among the committed changes. Refusals, offers, plans, questions and hypotheticals are not claims.

### `recall_sheet.csv`

One recall answer per row with the gold value. Answer `correct_yes_no` with `yes` if the answer states the gold value, even if worded differently.

## Returning the ratings

1. Add a `rater` column with the rater's initials on every row.
2. Save each sheet as `human_ratings_<sheet>_<rater>.csv`, for example `human_ratings_dialogue_quality_AB.csv`. Keep the `item` column unchanged.
3. Upload the files as a Kaggle dataset, attach it to the notebook together with the run's `llm_cache_*.jsonl` files, and rerun with `CACHE_ONLY=True`.

## What the notebook reports

- Per condition, the mean of each 1-to-5 scale with a bootstrap interval over items (`metrics/human_eval.csv`).
- Inter-rater agreement: quadratic-weighted Cohen's kappa for the 1-to-5 scales and Cohen's kappa for the yes/no labels (`metrics/human_agreement.csv`).
- The judge's agreement with the human majority on the contradiction items, and the key-word scorer's agreement with the human recall labels.

No human result is imputed: until rating files are attached, the notebook reports the human evaluation as pending.
