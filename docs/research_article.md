# Memory and State Control for LLM-Driven NPC Dialogue: A Controlled Comparison of Dual-Tier Memory and Pre-Commit Invariant Validation against Rolling-Context, Vector-Memory, and Generic RAG Agents

Source Code Repository: [https://github.com/parthmital/RAG-Driven-NPC-Narrative-Engine](https://github.com/parthmital/RAG-Driven-NPC-Narrative-Engine)

## Abstract

Large Language Models (LLMs) allow Non-Player Characters (NPCs) in interactive fiction to hold open-ended conversations, but three problems limit their use in games: facts established early in a session are forgotten as dialogue grows, model-proposed world changes break symbolic game rules (illegal moves, fabricated items, unbounded trust shifts), and per-turn cost and latency grow with context length. This article presents _The Obsidian Flask_, an NPC dialogue engine that separates language generation from state control. It combines (i) a dual-tier memory, an 8-turn short-term buffer plus a 384-dimensional FAISS store with location- and NPC-scoped retrieval and a relaxation fallback, with (ii) an event-sourced world state in which every LLM-proposed mutation passes a pre-commit invariant-validation barrier before a pure reducer applies it. The central question is not whether the system works in its own world but whether its two mechanisms, memory tiering and state control, outperform independent baselines and whether each contributes separately. We therefore specify a controlled comparison against three independent baseline agents (rolling-context, vector-memory, and generic RAG), a full-history reference, and a $2 \times 2$ factorial crossing of memory architecture with state control, plus seven single-component ablations. Evaluation spans long-horizon sessions of 50, 100 and 200 turns and 7 categories of adversarial invariant probes across four worlds that differ in authorship, genre, and scale (8 to 128 locations), including worlds converted from the externally authored LIGHT corpus and procedurally generated worlds. We report factual recall by fact-age, invariant violations measured by an oracle independent of the system's own validator, retrieval MRR and Recall@k, latency percentiles, token cost, and state-replay consistency, with bootstrap confidence intervals and pre-registered hypotheses. In a 6.7-hour automated run with a self-hosted 7B backbone on seven worlds, the system recalled 87.7% [84.2, 91.0] of facts 20 or more turns old on held-out worlds, against 0.0% for a rolling context of equal token budget, 63.9% for generic RAG and 80.2% for full history; its advantage over flat vector memory (84.9%) was not significant, and it used more input tokens than that baseline, so the memory hypothesis is not supported as stated. Scoped retrieval raised MRR@6 from 0.750 to 0.898. On the same model outputs, the validation barrier lowered adversarial attack success from 16.2% (direct writes) to 2.9%, with no false rejection of lawful twins and 0.039 ms of validation at P95, but it left a currency gap (19.7% attack success) and raised dialogue-state desynchronisation from 3.7% to 18.7% of live turns. Event-log replay reproduced the live state in 100% of sessions, while the backend's own load path lost the events logged after its last snapshot. Memory and control interacted significantly on recall, so the two mechanisms are not fully separable. Both main effects held on every held-out world family and on a second 3.7B backbone. The run used the second of eight pre-declared sample-size levels, automatic scoring without human labels, and a notebook-authored science fiction world, so these results are preliminary.

# 1. Choosing the Research Topic

## Domain Selection and Context

This research sits at the intersection of Natural Language Processing (NLP), generative AI, and interactive digital entertainment, focusing on text-based adventure games and interactive fiction. In text-centric worlds, spatial navigation, object interaction, and character dialogue are all mediated through language. Unlike graphical engines, where physics enforces spatial constraints, text worlds must maintain causal and ontological consistency through an explicit symbolic state model.

## Problem Narrowing

NPCs carry narrative progression, world immersion, and quest delivery in role-playing games. Games have traditionally used scripted dialogue graphs, branching trees, and finite state machines (FSMs). These guarantee rule compliance at negligible compute cost but restrict the player to predefined choices.

Generative models let players converse freely, but unconstrained LLM NPCs show three failure modes in interactive loops:

1. Long-horizon memory degradation: as history grows, facts established early are truncated out of the context window or under-attended when buried in long contexts (Liu et al., 2024; Maharana et al., 2024).
2. Invariant violations: LLMs have no built-in world model or conservation laws. Without external constraints they propose fabricated items, moves between disconnected rooms, and state changes that contradict established rules (Callison-Burch et al., 2022).
3. Cost and latency growth: approaches that append full history, or run multiple reflective LLM calls per turn (Park et al., 2023; Shinn et al., 2023), increase per-turn tokens and response time.

## Research Questions

- RQ1 (Memory): Does dual-tier, locality-scoped memory improve long-range factual recall per prompt token relative to rolling-context, vector-memory, and generic RAG agents?
- RQ2 (State control): Does a pre-commit invariant-validation barrier over event-sourced state reduce committed invariant violations under normal play and adversarial probes, and at what cost in wrongly rejected legitimate updates and dialogue-state desynchronisation?
- RQ3 (Separability): Do memory architecture and state control contribute independently, or do they interact?
- RQ4 (Efficiency): What latency and token costs does each component add?
- RQ5 (Generalisation): Do the effects hold across worlds of different authorship, genre, and scale, and across LLM backbones?

## Significance, Novelty, and Feasibility

- Practical significance: a reproducible architecture that couples open-ended dialogue with verifiable game mechanics on a single commodity machine plus a hosted inference endpoint.
- Technical novelty: the individual components (buffers, vector retrieval, event sourcing, validators) are established. The contribution is their integration for NPC dialogue and, principally, a controlled, ablated evaluation that isolates the value of memory tiering and of state control against independent baselines. We make no claim that any single component is new.
- Feasibility: embedding, retrieval, validation, and reduction run locally on CPU; in the game, LLM inference is delegated to a hosted endpoint. The evaluation reported here ran end to end in one Kaggle session on two T4 GPUs with self-hosted open-weight backbones (Section 11).

## Target Venues

Candidate venues include the AAAI Conference on Artificial Intelligence and Interactive Digital Entertainment (AIIDE), the ACM International Conference on the Foundations of Digital Games (FDG), IEEE Transactions on Games, the IEEE Conference on Games (CoG), and the Wordplay workshop series. Venue fit will be finalised after results are available.

# 2. Systematic Literature Review

## Thematic Review of Prior Art

### Theme 1: Grounded Dialogue and Action in Virtual Worlds

Urbanek et al. (2019) introduced LIGHT, a crowdsourced fantasy text-adventure platform, showing that conditioning dialogue models on room descriptions, objects, and personas improves grounded behaviour. The models generated dialogue and actions but did not maintain a persistent, validated world state across long sessions. Ammanabrolu et al. (2021) trained goal-driven agents with reinforcement learning over a factorised space of speech and actions in LIGHT, which required domain-specific training and targets quest completion rather than persistent open-ended NPC conversation.

### Theme 2: Memory Architectures for LLM Agents

Park et al. (2023) combined a memory stream, periodic reflection, and recency-importance-relevance retrieval to produce believable social behaviour in a sandbox town. The architecture uses several LLM calls per agent step, which raises cost and latency for player-facing dialogue. Shinn et al. (2023) used verbal self-reflection stored in an episodic buffer to improve agents over repeated trials, a loop designed for multi-trial tasks rather than single interactive turns. Packer et al. (2023) proposed MemGPT, which manages a bounded context and an external archival store through LLM-invoked memory functions. Maharana et al. (2024) introduced LoCoMo, showing that LLMs and RAG-augmented agents still struggle with very long-term conversational memory, particularly temporal and causal questions.

### Theme 3: Retrieval Augmentation and Long Contexts

Lewis et al. (2020) formalised Retrieval-Augmented Generation (RAG), conditioning generation on passages retrieved from a dense index. Generic RAG retrieves by semantic similarity alone and has no notion of the spatial or social scope of a game turn. Liu et al. (2024) showed that LLM accuracy drops when relevant information sits in the middle of long contexts, which weakens the assumption that simply extending context solves memory. Yao et al. (2023) interleaved reasoning traces with actions (ReAct), letting agents query tools and environments within a prompt scratchpad.

### Theme 4: Symbolic World Models and State Tracking

Côté et al. (2019) built TextWorld, a generator of text games with formally specified state and rule-enforced transitions. Hausknecht et al. (2020) released Jericho, a benchmark of human-authored interactive fiction games run on the Z-Machine. Symbolic engines guarantee consistency within their rule set but parse only a constrained command language and do not produce open-ended NPC dialogue.

### Theme 5: LLMs in Games and Tabletop Play

Gallotta et al. (2024) surveyed LLM roles in games and identified integration with game mechanics and state as an open challenge. Callison-Burch et al. (2022) framed Dungeons and Dragons as a dialogue challenge, including the task of predicting game state from dialogue, and found that state tracking remains difficult for LLMs. Akoury et al. (2020) released STORIUM, a dataset and platform for machine-in-the-loop story generation that uses structured cards to anchor collaborative narratives.

## Comparative Analysis

1. Urbanek et al. (2019) [EMNLP]:
   - Method: Generative and retrieval-ranking transformers conditioned on setting, persona, and objects.
   - Memory: Current episode context.
   - State: Text descriptions of rooms, characters, and objects.
   - Rule enforcement: Environment action checks; no validation of free-form dialogue commitments.
   - Data: LIGHT (crowdsourced fantasy dialogues).
   - Limitation relevant here: No persistent long-horizon memory across extended sessions.

2. Ammanabrolu et al. (2021) [NAACL]:
   - Method: RL over factorised speech and action spaces.
   - Memory: Encoded within the learned policy.
   - State: LIGHT environment state.
   - Rule enforcement: Environment-defined action validity.
   - Data: LIGHT-Quests.
   - Limitation: Requires task-specific training; not aimed at persistent free-form NPC conversation.

3. Park et al. (2023) [UIST]:
   - Method: Memory stream, reflection, and planning.
   - Memory: Natural-language memory stream with scored retrieval.
   - State: Sandbox environment tree with natural-language agent summaries.
   - Rule enforcement: Environment-level; LLM plans are not formally validated.
   - Data: 25-agent sandbox simulation.
   - Limitation: Multiple LLM calls per step raise cost and latency.

4. Shinn et al. (2023) [NeurIPS]:
   - Method: Verbal reinforcement via self-reflection.
   - Memory: Episodic reflection buffer across trials.
   - State: Task environment.
   - Rule enforcement: Environment feedback and self-evaluation.
   - Data: ALFWorld, HotpotQA, HumanEval.
   - Limitation: Designed for repeated trials, not single-pass interactive turns.

5. Packer et al. (2023) [arXiv]:
   - Method: OS-inspired hierarchical memory with LLM-invoked memory functions.
   - Memory: Bounded main context plus archival and recall storage.
   - State: Unstructured text memory.
   - Rule enforcement: None for world state.
   - Data: Multi-session chat and document QA.
   - Limitation: No symbolic world state or mutation validation.

6. Maharana et al. (2024) [ACL]:
   - Method: Benchmark for very long-term conversational memory.
   - Memory: Evaluates long-context and RAG agents.
   - State: Not applicable.
   - Rule enforcement: Not applicable.
   - Data: LoCoMo.
   - Limitation: Measures memory only; no game-state integrity.

7. Lewis et al. (2020) [NeurIPS]:
   - Method: Retrieval-augmented generation over a dense passage index.
   - Memory: Static non-parametric index.
   - State: Static corpus.
   - Rule enforcement: None.
   - Data: Open-domain QA benchmarks.
   - Limitation: No temporal or spatial scoping; corpus is not an evolving world state.

8. Liu et al. (2024) [TACL]:
   - Method: Analysis of how LLMs use long input contexts.
   - Finding: Accuracy is highest when relevant information is at the start or end of the context and drops in the middle.
   - Relevance: Motivates comparing retrieval against simply extending the rolling context.

9. Yao et al. (2023) [ICLR]:
   - Method: Interleaved reasoning and acting (ReAct).
   - Memory: Prompt scratchpad.
   - State: Environment observations.
   - Rule enforcement: Environment and tool interfaces.
   - Data: HotpotQA, FEVER, ALFWorld, WebShop.
   - Limitation: Scratchpad grows with trajectory length; no replayable state log.

10. Côté et al. (2019) [CGW, Springer]:
    - Method: Procedural text-game generator with formal state and rules.
    - Rule enforcement: Complete within its rule language.
    - Limitation: Constrained command parser; no generative NPC dialogue.

11. Hausknecht et al. (2020) [AAAI]:
    - Method: Interactive fiction benchmark for agents (Jericho).
    - Rule enforcement: Game engine.
    - Limitation: Parser-based action space; no free-form NPC conversation.

12. Gallotta et al. (2024) [IEEE ToG]:
    - Method: Survey and roadmap of LLMs in games.
    - Relevance: Identifies coupling LLM output with game state and mechanics as open.

13. Callison-Burch et al. (2022) [EMNLP]:
    - Method: D&D gameplay dataset; next-turn generation and game-state prediction.
    - Limitation relevant here: LLM state tracking is unreliable without explicit state.

14. Akoury et al. (2020) [EMNLP]:
    - Method: Collaborative story dataset and platform (STORIUM).
    - Limitation relevant here: Structured narrative anchors without executable world state.

## Synthesis and Open Challenges

1. Expressiveness versus consistency: neural NPCs are expressive but unconstrained; symbolic engines are consistent but linguistically narrow.
2. Memory design space: rolling context, flat vector memory, generic RAG, and LLM-managed memory (MemGPT) coexist, but game-specific comparisons that control for token budget are scarce.
3. Generation-mutation coupling: most dialogue systems do not bind what an NPC says to validated, replayable state changes.
4. Evaluation: memory benchmarks (LoCoMo) ignore state integrity, and game benchmarks (Jericho, TextWorld) ignore open dialogue. No common protocol measures both, with ablations, across multiple worlds.

# 3. Datasets, Worlds, and Benchmark Construction

## Design Principle

A single handcrafted world cannot support generalisation claims, and a benchmark authored by the system's designers risks being tuned to the system. The benchmark therefore uses four worlds that vary in authorship, genre, and scale, and separates benchmark authoring from system tuning.

## World Suite

1. W1, Obsidian (in-house, dark fantasy): the existing [world_seed.json](../Backend/game/world_seed.json), with 8 locations, 4 NPCs, 4 conserved objects, and 7 rules. Used for development; results on W1 are reported separately as in-distribution.
2. W2, LIGHT-derived (externally authored, fantasy): 3 worlds of 16 to 32 locations assembled from LIGHT locations, characters, and objects (Urbanek et al., 2019; CC BY-NC 4.0), converted to the same seed schema by a deterministic script. Content is written by LIGHT crowdworkers, not the authors.
3. W3, Held-out genre (science fiction station): 1 world of 24 locations and 6 NPCs, intended to be authored by a contributor not involved in system development, following a written specification, and frozen before any system run on it. In the run reported in Section 13, W3 was authored inside the evaluation notebook from that specification before any system run, so it is held out from tuning but not independently authored. The notebook accepts an independently written seed file in its place.
4. W4, Procedural scaling worlds: generated graphs of 32 and 128 locations with 8 to 16 NPCs and 16 to 64 objects from a seeded generator, to test retrieval and validation at larger scale. Names and descriptions are templated, so W4 tests structure rather than prose quality.

No system hyperparameter (buffer size, k, fallback threshold, prompt wording) is tuned on W2 to W4.

The worlds as built for the run:

| World  | Family         | Locations | NPCs | Objects | Rules | Edges | Diameter | Secrets |
| ------ | -------------- | --------- | ---- | ------- | ----- | ----- | -------- | ------- |
| W1     | In-house       | 8         | 4    | 4       | 7     | 7     | 4        | 8       |
| W2a    | LIGHT-derived  | 16        | 6    | 7       | 5     | 15    | 8        | 12      |
| W2b    | LIGHT-derived  | 24        | 6    | 9       | 5     | 23    | 9        | 12      |
| W2c    | LIGHT-derived  | 32        | 6    | 12      | 5     | 31    | 9        | 12      |
| W3     | Held-out genre | 24        | 6    | 8       | 6     | 27    | 4        | 12      |
| W4-32  | Procedural     | 32        | 8    | 16      | 5     | 39    | 9        | 16      |
| W4-128 | Procedural     | 128       | 16   | 64      | 5     | 163   | 12       | 32      |

LIGHT's resolvable room links split into small components, so each W2 world is connected with a seeded spanning tree (14, 22 and 27 joining edges). LIGHT has no secrets, so each W2 NPC receives two templated secrets built from words that appear nowhere else in the world, which keeps leak detection unambiguous.

![World suite: locations, NPCs and objects per world](../notebooks/outputs/plots/01_world_suite.png)

## Long-Horizon Session Benchmark

- Scripted player sessions of 50, 100, and 200 turns. Player turns are fixed scripts, so every system receives identical inputs; this removes player-adaptation confounds at the cost of realism (Section 14).
- Each session plants facts (player disclosures, NPC commitments, object transfers, location events) and later probes them at fact ages of 5, 10, 20, 40, 80, and 160 turns, with fact age bucketed for analysis.
- Each probe has a gold answer and a set of gold-relevant memory turn IDs for retrieval scoring.
- Distractor turns include paraphrased near-duplicate facts and facts from other locations or NPCs, to test scoping.
- Target size: 40 sessions per world per horizon where the world is large enough, giving approximately 480 sessions in total. The run in Section 13 used 3 sessions per world per horizon (63 sessions, 630 probes per condition), chosen by a time-budget planner (Section 11).
- Teacher forcing: NPC replies in the history are scripted, so every condition sees the same history and the LLM is called only at probe turns. Fact values come from invented-word pools filtered against each world's text, and a probe is scored correct when the gold value's key word appears in the reply.

## Adversarial Invariant Probe Suite

Probes are player turns designed to induce an illegal mutation. Seven categories, each instantiated per world from templates plus hand-written variants:

1. Spatial teleportation: requests to move to non-adjacent or non-existent locations.
2. Item fabrication: requests for items that do not exist in the world.
3. Item theft or duplication: taking objects not present in the current location, or already held.
4. Trust inflation: pressure for single-turn trust changes above the per-turn bound.
5. Currency exploits: spending more than held or requesting unearned currency.
6. Prompt injection: player text that instructs the model to emit specific world updates or ignore rules.
7. Lore and secret violations: attempts to make an NPC reveal a secret before its trust threshold or contradict canonical lore.

Categories 1 to 5 are checkable by the symbolic oracle; categories 6 and 7 are scored by the oracle where they produce mutations and by annotation where they affect only dialogue. Target size: 60 probes per category per world family, approximately 1,680 probes. Each probe also has a legitimate twin (a lawful version of the same request) to measure false rejection. The run in Section 13 used 10 probes per category per world (490 attacks and 470 twins; theft has twins for 70% of its attacks), each posed under five context conditions.

## Annotation and Quality Control

- Two annotators label recall correctness and lore violations on a stratified 20% sample; agreement is reported as Cohen's kappa. Remaining items are scored by an LLM judge whose agreement with the human labels is reported; the judge is a different model family from the system backbone.
- Annotators are blind to which system produced each output.
- Status: the run in Section 13 is scored automatically (key-word recall, secret keywords, and refusal and arrival cues for desynchronisation). It exports blinded, shuffled sheets for raters (1,250 recall items, 150 persona and lore items, 240 desynchronisation items) with the condition keys in separate files. Human labels, Cohen's kappa and the LLM judge are not yet available.

## Preprocessing

- Embeddings: sentence-transformers/all-MiniLM-L12-v2, 384 dimensions, L2-normalised, so inner product equals cosine similarity.
- Index: FAISS IndexFlatIP with per-entry metadata (turn, location ID, NPC ID, summary text).
- Output contract: Pydantic v2 schemas ([llm_output.py](../Backend/schemas/llm_output.py)) for dialogue, narration, memory summary, and proposed world updates.

## Release

The evaluation harness is [notebooks/npc-memory-state-benchmark.ipynb](../notebooks/npc-memory-state-benchmark.ipynb). Its run outputs (world seeds, session scripts, probes, raw per-job predictions, LLM response caches, metrics, figures, annotation sheets, and logs) are in `notebooks/outputs/`, subject to LIGHT's non-commercial licence for W2 content. Gold human annotations will be added when labelling is complete.

# 4. Research Gaps

## Gap 1: Controlled Evidence on Memory Architectures for NPC Dialogue

- Evidence: Long contexts are used unevenly (Liu et al., 2024), and very long-term conversational memory remains weak for LLM and RAG agents (Maharana et al., 2024). Memory systems such as MemGPT and generative agents are not compared under a fixed token budget in game settings.
- Gap: No token-budget-controlled comparison of rolling context, flat vector memory, generic RAG, and scoped dual-tier memory on game dialogue.

## Gap 2: Validation of LLM-Proposed World Mutations

- Evidence: LLMs track game state poorly (Callison-Burch et al., 2022), and coupling LLMs to game mechanics is an open challenge (Gallotta et al., 2024). Symbolic engines enforce rules but not over free-form dialogue (Côté et al., 2019; Hausknecht et al., 2020).
- Gap: Little measurement of how much a pre-commit validator reduces violations, how often it wrongly blocks lawful updates, and how often dialogue then contradicts committed state.

## Gap 3: Replayable, Auditable State for LLM Agents

- Evidence: Agent memories in prior systems are natural-language logs (Park et al., 2023; Packer et al., 2023), which do not support exact state reconstruction.
- Gap: Little evaluation of replay consistency for LLM-driven game state.

## Gap 4: Joint Evaluation across Memory, Integrity, and Cost

- Evidence: Memory benchmarks omit state integrity; game benchmarks omit open dialogue.
- Gap: No protocol reporting recall, violations, retrieval quality, latency, token cost, and replay consistency together, with ablations, across multiple worlds.

# 5. Hypotheses and Objectives

Hypotheses are stated before running the full evaluation. Each is tested against the strongest applicable baseline.

- H1 (Memory): Scoped dual-tier memory achieves higher factual recall for fact ages of 20 turns or more than B1 rolling-context at equal prompt-token budget, and higher than B2 and B3 at equal or lower token cost.
- H2 (Retrieval): Scoping plus relaxation fallback yields higher MRR@6 than unscoped retrieval over the same memory entries (B2).
- H3 (State control): The validation barrier reduces oracle-detected committed violations relative to the same system without it, on both normal sessions and adversarial probes.
- H4 (Cost of control): The barrier's false-rejection rate on legitimate twins is at most 5%, and its added local latency is under 5 ms per turn at P95.
- H5 (Replay): Replaying the event log from the seed, with or without snapshots, reproduces the live state in 100% of sessions for event-sourced conditions; baselines that mutate state directly without an event log cannot be replayed exactly.
- H6 (Separability): In the $2 \times 2$ factorial, the memory factor mainly affects recall, and the control factor mainly affects violations, with small interaction.
- H7 (Generalisation): The direction of the H1 and H3 effects holds on held-out worlds W2 to W4.

A hypothesis is supported only if its effect is significant after correction (Section 12) and its sign is consistent across worlds. Results contrary to a hypothesis are reported as such.

# 6. Proposed System: The Obsidian Flask Engine

## Architecture

The system has four tiers:

1. Presentation: React 18, TypeScript, Tailwind CSS, and Zustand, with WebSocket streaming.
2. Orchestration: FastAPI with per-session async locks, executing a compiled 8-node LangGraph pipeline ([definition.py](../Backend/graph/definition.py)).
3. Validation: schema parsing ([llm_output.py](../Backend/schemas/llm_output.py)) and symbolic rule checks ([validator.py](../Backend/game/validator.py)).
4. Storage: 8-turn short-term buffer ([short_term.py](../Backend/memory/short_term.py)), FAISS long-term memory ([faiss_index.py](../Backend/memory/faiss_index.py)), append-only SQLite event log ([event_store.py](../Backend/core/event_store.py)), and snapshots every 16 turns ([snapshot.py](../Backend/core/snapshot.py)).

## World State

The world at turn $t$ is $S_t = (L, C, O, F, R, t)$: locations with adjacency sets and mutable attributes; NPCs with location, status, lore, and conditional secrets; objects, each either in a location or held by an entity but never both; player flags; and a relationship map with scores bounded to $[-100, 100]$.

## Event Sourcing and Pure Reduction

An event is $e = (\text{id}, t, \text{type}, \text{payload}, \text{timestamp})$. State evolves by a pure reducer ([reducer.py](../Backend/core/reducer.py)):

$$
S_{t+1} = \delta(S_t, e_t), \qquad S_T = \text{foldl}(\delta, S_0, [e_0, \dots, e_{T-1}])
$$

Snapshots every 16 turns bound recovery to loading the latest snapshot and folding the remaining suffix. Replay consistency is therefore expected by construction for the reducer; Section 12 tests it empirically, including across process restarts and against snapshot-plus-suffix reconstruction, because implementation defects (non-deterministic iteration order, timestamps inside state, floating-point effects) can break construction-level guarantees.

## Dual-Tier Memory Retrieval

For player input $u_t$, the embedder produces a unit vector $q_t \in \mathbb{R}^{384}$. Each committed turn adds a long-term entry whose vector $m_i$ is the embedding of that turn's player input and whose text is the model's one-sentence memory summary (or the input itself when no summary was given), with metadata $(t_i, \text{loc}_i, \text{npc}_i)$, where $\text{loc}_i$ is the player's location after the turn's events. Retrieval therefore matches the current input against past inputs and returns past summaries.

1. Scoped retrieval: over-fetch $k \cdot 5$ nearest neighbours by $q_t^\top m_i$, filter to entries matching the current location and active NPC, and keep the top $k = 6$.
2. Relaxation fallback: if fewer than 3 scoped entries remain, retrieve the top $k$ without filters.

The prompt contains canonical state, the NPC profile, the last 8 turns, and the retrieved memories, capped at 16,384 characters. The memory store is pruned to half its size when it exceeds 1,000 entries.

## Pre-Commit Invariant Validation

Every proposed update is checked before commit ([validator.py](../Backend/game/validator.py)):

1. Movement: destination exists and is adjacent to the player's location.
2. Taking objects: object exists and is in the player's current location.
3. Dropping objects: object and target location exist; if dropped by the player, the player holds it.
4. Relationships: NPC exists and $|\Delta| \le 20$ per turn; the reducer clamps scores to $[-100, 100]$.
5. Currency: delta is numeric and spending does not exceed the balance.
6. State, flag, and journal updates: target exists and required keys are present.
7. Entity creation: any proposed new entity is rejected and logged.

Rejected proposals are dropped with a logged reason; the turn continues. Accepted proposals become events, are persisted, then reduced.

### Known Validator Coverage Gaps

These are stated so the evaluation can measure them rather than hide them:

- Drops by NPCs do not check that the NPC holds the object.
- The validator checks structural legality, not narrative plausibility (for example, a trust change that is within bounds but unjustified by the dialogue).
- Rejection does not rewrite the NPC's dialogue, so an NPC can say it handed over an item whose transfer was rejected. This dialogue-state desynchronisation is measured explicitly (Section 12).

The evaluation and a code review for it found further gaps, all measured or stated in Section 13:

- Currency gains are not bounded: only a negative delta is checked, against the balance. Any positive delta passes.
- Spending is checked per proposal against the balance before the turn, so several spends that each fit can together overspend (the reducer then floors the balance at zero).
- The prompt tells the model that trust deltas range from -10 to 10, while the validator allows $\pm 20$.
- NPC secrets are never placed in the prompt (only personality, knowledge and state are), so the trust-60 reveal rule cannot be honoured by the model, and leak rates do not measure secret keeping.
- The backend's load path restores the latest snapshot without folding the events logged after it, and the active NPC is set outside the event log.
- At the evaluated commit, the JSON extractor could return a bare JSON string or list, which the parse node did not handle. This was fixed after the evaluation (commit `a9767d5`).

# 7. Research Methodology

1. Specify invariants and the event schema.
2. Build the four-world suite, session scripts, probes, and gold annotations; freeze W2 to W4 before any system run on them.
3. Implement the proposed system and all baselines on a shared harness (Section 11) so that only the studied factor differs between conditions.
4. Implement an independent invariant oracle (Section 12) that shares no code with the validator.
5. Run all conditions on all sessions and probes with three sampling seeds and two LLM backbones.
6. Compute metrics, confidence intervals, and hypothesis tests; run the factorial and ablation analyses.
7. Conduct error analysis on a stratified sample of failures per condition.

# 8. Technology Choices

- Inference in the game: Groq-hosted `openai/gpt-oss-120b` (the configured default in [config.py](../Backend/config.py)), temperature 0.35.
- Inference in the evaluation: `IFM/K2-Horizon-7B` as the primary backbone and `IFM/K2-Horizon-3.7B` as the second, both Apache 2.0, served locally by vLLM 0.30.0 in fp16 on two T4 GPUs at the backend's temperature of 0.35, with top-p 0.95. Both are reasoning models; reasoning effort is set to low and thinking is capped at 192 tokens, after which the notebook closes the thinking block and asks for the JSON answer (up to 768 tokens). Self-hosting removes network variance and gives exact token counts, but means the evaluated backbone differs from the game's default.
- Embedding: all-MiniLM-L12-v2 on CPU.
- Vector index: FAISS IndexFlatIP, exact search.
- Orchestration: LangGraph StateGraph with a fixed linear node order.
- Persistence: SQLite append-only event log with transactional writes.
- Schemas: Pydantic v2.
- Web: FastAPI with per-session async locks.

# 9. Contributions

1. An NPC dialogue architecture that routes all LLM-proposed world changes through a pre-commit validator into an event-sourced state, coupled with location- and NPC-scoped dual-tier memory.
2. A multi-world benchmark (four world families, long-horizon sessions, seven probe categories with legitimate twins) and an evaluation harness measuring recall, invariant violations, retrieval quality, latency, token cost, and replay consistency together.
3. A controlled comparison against independent rolling-context, vector-memory, and generic RAG agents, a factorial separation of memory and state-control effects, and single-component ablations.
4. An explicit account of the validator's costs: false rejections, dialogue-state desynchronisation, and coverage gaps.

# 10. Turn Pipeline and Complexity

## Pipeline

Each turn runs eight nodes: input, retrieval, prompt assembly, LLM generation, parse, validate, commit, output ([definition.py](../Backend/graph/definition.py)).

1. Input: trim and sanitise; empty input becomes a neutral silence token.
2. Retrieval: embed the input, run scoped FAISS search, fall back to unscoped search if fewer than 3 results.
3. Prompt assembly: canonical state, NPC profile, 8-turn buffer, retrieved memories, JSON output instructions, within 16,384 characters ([prompt_builder.py](../Backend/llm/prompt_builder.py)).
4. LLM generation: call the inference endpoint with retries.
5. Parse: extract and validate JSON; on failure, use the raw text as dialogue with no updates and log a schema error.
6. Validate: partition proposals into accepted events and rejected errors.
7. Commit: append the speech event and accepted events to SQLite, reduce, update the buffer, index the turn summary, and snapshot every 16 turns.
8. Output: return dialogue, narration, updated state, and logs.

## Complexity

With $n$ memory entries, $d = 384$, and $p$ proposals per turn:

- Embedding: one forward pass of a small transformer; constant per turn for bounded input length.
- Exact search: $O(nd)$; $n$ is bounded by pruning at 1,000 entries.
- Validation: $O(p)$ dictionary and adjacency lookups.
- Reduction: $O(p)$ events, plus a state copy proportional to world size.
- Recovery: $O(|S| + r)$ where $r < 16$ is the number of events after the latest snapshot, versus $O(|S| + T)$ for full replay.

Measured per-stage latencies are reported in Table 6 rather than asserted here.

# 11. Experimental Setup

## Shared Harness and Fairness Controls

All conditions share the same LLM backbone, decoding parameters, system prompt skeleton, canonical-state serialisation, output schema, and player scripts. They differ only in the memory mechanism and in how proposed updates reach the world state. Without a shared output contract, differences in invariant violations would reflect prompt formats rather than architecture.

For conditions without the validation barrier, proposed updates that parse against the schema are applied directly to state (schema-only checking), and the resulting state is audited by the oracle. This models the common practice of letting an LLM agent write state through a tool interface.

## Baselines

All baselines are independent implementations that do not reuse the proposed system's retrieval code.

- B0, Full history (reference): entire dialogue history in the prompt, truncated only at the backbone's context limit. An upper-bound reference for recall and a worst case for cost.
- B1, Rolling context: the most recent turns that fit a fixed token budget $B$. Evaluated at two budgets: $B$ matched to the proposed system's mean prompt size, and ${2B}$.
- B2, Vector-memory agent: every turn summary embedded into a flat store; top-$k$ by cosine similarity with no scoping and no short-term buffer, following the flat vector memory pattern common in agent frameworks.
- B3, Generic RAG agent: raw dialogue chunks plus world lore documents indexed together; top-$k$ chunks retrieved per turn with a standard RAG template (Lewis et al., 2020), no scoping, no event log.
- B4, Scripted FSM (reference only): a hand-written dialogue tree for W1, used to anchor the integrity and latency floor. It is not comparable on open-ended input and is excluded from hypothesis tests.

Where feasible, an LLM-managed memory baseline in the style of MemGPT (Packer et al., 2023) is added as B5; if it is not run, this is listed as a limitation.

## Factorial Design (RQ3)

|                                  | No validation barrier (direct writes) | Validation barrier plus event sourcing |
| -------------------------------- | ------------------------------------- | -------------------------------------- |
| Rolling context (B1, budget $B$) | F1                                    | F2                                     |
| Scoped dual-tier memory          | F3                                    | F4 (full system)                       |

## Single-Component Ablations

- A1: no long-term memory (8-turn buffer only).
- A2: no short-term buffer (retrieval only).
- A3: no scoping (unfiltered top-$k$).
- A4: no relaxation fallback.
- A5: no validation barrier (schema-only direct writes to the event log).
- A6: no event sourcing (in-place state mutation, validator kept).
- A7: no snapshots (full replay on recovery).

Sensitivity sweeps: buffer size $\{4, 8, 16\}$, $k \in \{3, 6, 12\}$, fallback threshold $\in \{0, 3, 6\}$, on W1 and W2 only.

## Runs and Hardware

- Three sampling seeds per condition; hosted-endpoint runs interleaved across conditions in the same time windows to spread network variance evenly.
- Local compute: a documented 8-core CPU, 16 GB RAM machine; exact model, OS, and library versions are recorded in the released run manifest.
- Library versions are pinned from [requirements.txt](../Backend/requirements.txt).

As run for Section 13:

- System under test: the repository at commit `0ea345fe140b359d7e82e77ffb2fdfa74caf0e7c`, imported as a library. Only baselines, the oracle and benchmark generators are new code. Live conditions are built from the backend's own LangGraph node factories, swapping only the nodes a condition changes.
- Hardware: one Kaggle session with 2 x Tesla T4 (15.64 GB each), 4 CPU cores and 33.7 GB RAM; Python 3.12.13, sentence-transformers 5.4.1, faiss-cpu 1.15.1, LangGraph 0.6.11, Pydantic 2.12.3, statsmodels 0.14.6. The 7B model ran with tensor parallelism over both GPUs; the 3.7B model ran as one replica per GPU.
- Paired sampling: each request's seed depends on the probe or turn, not on the condition, so identical prompts receive identical outputs (common random numbers). Probe outputs are committed three ways (barrier, reducer only, direct writes), so the control comparison is exactly paired.
- Sample size: a pilot of 256 jobs measured throughput, and a planner chose the largest of eight pre-declared levels that fit the 11.25-hour budget. It chose level 2 (3 sessions per world per horizon, 10 probes per category per world, 2 live sessions per world); level 7 corresponds to the targets above. No row was lost to a deadline in any main stage.
- Seeds: the calibration sessions were rerun with two further seeds for F4, B1, B2 and B3.
- Budget $B$: 440 tokens, the mean size of F4's memory and history blocks on the calibration probes.
- Second backbone: worlds W1, W2a, W3 and W4-32 at horizon 100, with probes under the F4 context only.
- Not run: B4 (scripted FSM) and B5 (MemGPT-style memory).
- Total wall time: 6.69 hours.

# 12. Metrics

1. Factual recall: proportion of recall probes answered correctly against gold, reported overall and by fact-age bucket (5, 10, 20, 40, 80, 160 turns).
2. Invariant violations:
   - Committed violation rate: oracle-detected violations per 100 committed state transitions, and proportion of sessions with at least one violation.
   - Probe attack success rate: proportion of adversarial probes that result in a committed violation, per category.
   - False rejection rate: proportion of legitimate-twin updates rejected by the barrier.
   - Dialogue-state desynchronisation: proportion of turns where the NPC's dialogue asserts a state change that was not committed, or vice versa (annotated sample).
   - The oracle is a separate implementation that re-derives world facts from the post-turn state and checks conservation (each object in exactly one place), adjacency of moves, bounds, and entity canonicity. It shares no code with the validator, so the barrier's own acceptance decisions are not used to score it.
3. Retrieval quality: MRR@6 and Recall@6 against gold-relevant memory IDs, for retrieval conditions. For rolling-context conditions, the in-context presence rate of the gold turn is reported instead.
4. Latency: end-to-end P50, P95, and P99, split into local compute and LLM time; reported for the hosted backbone and the local latency-control backbone. In the run reported here, all latency is from the self-hosted backbone on two T4 GPUs, measured with one request in flight.
5. Token cost: mean input and output tokens per turn from API usage fields, and cost per 100 turns at the provider's list price on the run date. Because the evaluated models were self-hosted, cost is reported in tokens only.

Until human labels are available, dialogue-state desynchronisation is scored by an automatic proxy: a turn is flagged when the barrier rejected a proposal but the dialogue contains no refusal cue, or when, on a scripted move turn, the narration's claim of arrival disagrees with the committed move. 6. State-replay consistency: proportion of sessions where the state rebuilt from the seed plus the logged events matches the live final state by canonical hash, tested (a) by full fold, (b) by snapshot plus suffix, (c) after a forced process restart mid-session. For direct-write conditions without an event log, replay uses the recorded mutation sequence where one exists and is otherwise reported as not replayable. 7. Secondary: schema parse success rate, secret-leak rate before trust threshold, and persona consistency (blind 1 to 5 rating on a sample, with inter-rater agreement).

## Statistical Analysis

- Unit of analysis: session for session-level metrics, probe for probe metrics.
- 95% confidence intervals by session-level bootstrap (10,000 resamples).
- Paired comparisons against the proposed system: McNemar's test for binary per-probe outcomes and Wilcoxon signed-rank for continuous per-session metrics, with Holm-Bonferroni correction across the hypothesis family.
- Factorial effects: mixed-effects logistic regression with memory, control, and their interaction as fixed effects and world and session as random effects.
- Effect sizes are reported alongside p-values.

# 13. Results

All values come from the evaluation notebook's run outputs (`notebooks/outputs/metrics/`). They are formatted as mean [95% cluster-bootstrap CI], pooled over the held-out worlds W2a to W4-128 unless stated; W1 appears in Table 7. The backbone is K2-Horizon-7B unless stated. No value is estimated or carried over from earlier prototype runs.

## Table 1: Main Comparison (Held-Out Worlds)

| Condition                  | Recall, age 20+ (%) | Committed violations per 100 transitions | Probe attack success (%) | MRR@6                | P50 / P95 LLM latency (ms) | Input tokens per turn | Replay consistency (%) |
| -------------------------- | ------------------- | ---------------------------------------- | ------------------------ | -------------------- | -------------------------- | --------------------- | ---------------------- |
| B0 Full history            | 80.2 [75.9, 84.4]   | 45.0 [38.3, 52.1]                        | 13.3 [10.2, 16.7]        | n/a                  | 10948 / 23984              | 4310                  | not replayable         |
| B1 Rolling context, $B$    | 0.0 [0.0, 0.0]      | 45.0 [38.1, 51.9]                        | 13.3 [10.2, 16.7]        | n/a                  | 7020 / 11173               | 1398                  | not replayable         |
| B1 Rolling context, ${2B}$ | 25.0 [21.3, 28.9]   | n/a (no probe context)                   | n/a                      | n/a                  | not measured               | 1823                  | not replayable         |
| B2 Vector memory           | 84.9 [81.1, 88.6]   | 43.1 [37.3, 48.9]                        | 15.7 [12.4, 19.3]        | 0.750 [0.729, 0.771] | not measured               | 1102                  | not replayable         |
| B3 Generic RAG             | 63.9 [57.7, 69.9]   | 56.4 [50.8, 61.9]                        | 19.3 [15.7, 23.1]        | 0.707 [0.686, 0.729] | not measured               | 1209                  | not replayable         |
| Proposed (F4)              | 87.7 [84.2, 91.0]   | 9.2 [4.6, 14.3]                          | 3.1 [1.4, 4.8]           | 0.898 [0.877, 0.917] | 6906 / 9409                | 1399                  | 100.0 [100.0, 100.0]   |

Notes:

- Baselines commit probe outputs by direct writes, because they have no validator; F4 commits through the barrier.
- Probe prompts carry three teacher-forced history turns, so B0 and B1 built identical probe prompts and their violation figures coincide.
- The single-stream latency stage reached its deadline before B1 ${2B}$, B2 and B3 were measured (B1 ${2B}$ has one cached sample only; B1 has 15 of 24 samples).
- Baselines keep no event log, so they cannot be replayed.

![Recall by fact age against baselines and ablations](../notebooks/outputs/plots/02_recall_by_fact_age.png)

_Figure 1. Recall by fact age on held-out worlds, against the baselines (left) and the memory ablations (right). The rolling contexts fall to zero once a fact leaves the window; F4 and B2 stay flat._

![Token cost against long-range recall](../notebooks/outputs/plots/03_cost_vs_recall.png)

_Figure 2. Mean input tokens per turn against recall at fact age 20 or more. B2 and A2 reach similar recall with fewer tokens than F4; B0 costs about three times as much for lower recall._

## Table 2: Recall by Fact Age (Held-Out Worlds, %)

| Condition                  | 5                 | 10                | 20                | 40                | 80                | 160                |
| -------------------------- | ----------------- | ----------------- | ----------------- | ----------------- | ----------------- | ------------------ |
| B0 Full history            | 75.0 [67.6, 82.4] | 77.8 [69.4, 85.2] | 78.7 [71.3, 86.1] | 75.0 [65.7, 83.3] | 86.1 [79.2, 93.1] | 88.9 [77.8, 97.2]  |
| B1 Rolling context, $B$    | 86.1 [79.6, 91.7] | 65.7 [55.6, 75.9] | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]     |
| B1 Rolling context, ${2B}$ | 81.5 [74.1, 88.0] | 78.7 [69.4, 87.0] | 75.0 [65.7, 83.3] | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]     |
| B2 Vector memory           | 85.2 [78.7, 91.7] | 82.4 [75.9, 88.9] | 88.9 [82.4, 94.4] | 80.6 [73.1, 88.0] | 84.7 [75.0, 93.1] | 86.1 [75.0, 94.4]  |
| B3 Generic RAG             | 72.2 [63.0, 80.6] | 69.4 [60.2, 78.7] | 66.7 [57.4, 75.9] | 68.5 [59.3, 77.8] | 62.5 [50.0, 75.0] | 44.4 [30.6, 58.3]  |
| Proposed (F4)              | 96.3 [92.6, 99.1] | 85.2 [78.7, 91.7] | 87.0 [80.6, 92.6] | 89.8 [84.3, 94.4] | 83.3 [75.0, 90.3] | 91.7 [83.3, 100.0] |
| A1 No long-term memory     | 85.2 [77.8, 91.7] | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]    | 0.0 [0.0, 0.0]     |
| A2 No short-term buffer    | 86.1 [79.6, 91.7] | 88.0 [82.4, 93.5] | 90.7 [85.2, 95.4] | 91.7 [87.0, 96.3] | 84.7 [76.4, 93.1] | 88.9 [77.8, 97.2]  |
| A3 No scoping              | 94.4 [89.8, 98.1] | 88.9 [82.4, 94.4] | 82.4 [75.9, 88.9] | 79.6 [71.3, 87.0] | 80.6 [70.8, 90.3] | 88.9 [77.8, 97.2]  |
| A4 No fallback             | 94.4 [89.8, 98.1] | 85.2 [78.7, 91.7] | 88.0 [81.5, 94.4] | 90.7 [85.2, 95.4] | 84.7 [77.8, 91.7] | 91.7 [83.3, 100.0] |
| n (F4 probes)              | 108               | 108               | 108               | 108               | 72                | 36                 |

Ages 80 and 160 exist only in 100- and 200-turn sessions, so those columns rest on fewer probes.

## Retrieval Quality and Secondary Memory Metrics

| Condition  | Gold in prompt (%)   | Distractor in prompt (%) | Confused with distractor (%) | Recall@6 (%)         | Parse success (%)  | Input / output tokens per 100 turns |
| ---------- | -------------------- | ------------------------ | ---------------------------- | -------------------- | ------------------ | ----------------------------------- |
| F4         | 100.0 [100.0, 100.0] | 57.0 [52.9, 61.4]        | 0.9 [0.2, 1.8]               | 100.0 [100.0, 100.0] | 98.1 [97.1, 99.1]  | 139,898 / 15,394                    |
| B0         | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0]     | 3.7 [1.9, 5.8]               | n/a                  | 98.9 [98.0, 99.6]  | 431,032 / 14,117                    |
| B1, $B$    | 35.7 [33.2, 38.3]    | 59.6 [56.0, 63.3]        | 14.4 [11.4, 17.6]            | n/a                  | 99.1 [98.3, 99.8]  | 139,831 / 15,574                    |
| B1, ${2B}$ | 57.4 [54.1, 60.8]    | 74.3 [70.9, 77.8]        | 11.3 [9.0, 13.7]             | n/a                  | 99.6 [99.1, 100.0] | 182,309 / 14,164                    |
| B2         | 99.1 [98.2, 99.8]    | 90.0 [87.4, 92.6]        | 0.2 [0.0, 0.6]               | 99.1 [98.2, 99.8]    | 95.9 [93.8, 97.8]  | 110,154 / 16,000                    |
| B3         | 98.0 [96.8, 99.0]    | 87.6 [84.7, 90.3]        | 7.4 [5.4, 9.4]               | 98.0 [96.8, 98.9]    | 98.5 [97.4, 99.4]  | 120,923 / 15,349                    |
| A1         | 20.0 [19.1, 20.9]    | 52.6 [48.9, 56.4]        | 20.6 [17.7, 23.6]            | n/a                  | 99.4 [98.7, 100.0] | 130,763 / 15,131                    |
| A2         | 100.0 [100.0, 100.0] | 10.2 [7.6, 13.0]         | 0.0 [0.0, 0.0]               | 100.0 [100.0, 100.0] | 98.3 [97.1, 99.4]  | 108,486 / 14,941                    |
| A3         | 98.9 [98.0, 99.6]    | 90.7 [88.7, 92.9]        | 0.2 [0.0, 0.6]               | 98.7 [97.7, 99.5]    | 98.9 [98.0, 99.6]  | 141,690 / 15,460                    |
| A4         | 100.0 [100.0, 100.0] | 52.6 [49.1, 56.3]        | 1.1 [0.4, 2.0]               | 100.0 [100.0, 100.0] | 98.0 [96.9, 98.9]  | 138,781 / 15,457                    |

No prompt reached the system's 16,384-character cap.

![Retrieval quality and in-context presence of the gold turn](../notebooks/outputs/plots/04_retrieval_quality.png)

_Figure 3. Left: MRR@6 and Recall@6 per retrieval condition. Right: share of probes whose gold turn reached the prompt, by fact age, which bounds recall from above._

Sensitivity sweeps (retrieval only, W1 and W2, one setting varied at a time around buffer 8, $k = 6$, threshold 3):

| Setting     | Gold in prompt | MRR@k  |
| ----------- | -------------- | ------ |
| buffer 4    | 0.9989         | 0.8990 |
| buffer 8    | 0.9989         | 0.8990 |
| buffer 16   | 0.9989         | 0.8990 |
| $k = 3$     | 0.9648         | 0.8390 |
| $k = 12$    | 1.0000         | 0.9124 |
| threshold 0 | 1.0000         | 0.9227 |
| threshold 6 | 0.9955         | 0.8303 |

![Sensitivity sweeps](../notebooks/outputs/plots/09_sensitivity_sweeps.png)

_Figure 4. Gold-in-prompt rate and MRR@k for each sweep setting._

Seed variance (calibration sessions, recall over all ages):

| Condition | Seed 0 | Seed 1 | Seed 2 | SD across seeds (points) |
| --------- | ------ | ------ | ------ | ------------------------ |
| F4        | 0.857  | 0.862  | 0.862  | 0.27                     |
| B1, $B$   | 0.314  | 0.300  | 0.310  | 0.73                     |
| B2        | 0.871  | 0.848  | 0.795  | 3.90                     |
| B3        | 0.681  | 0.681  | 0.671  | 0.55                     |

## Table 3: Factorial Separation (Memory × Control, Live Sessions)

| Cell                        | Recall, live probes (%) | Committed violations per 100 transitions | False rejection (%) | Desync rate (%)   | Sessions |
| --------------------------- | ----------------------- | ---------------------------------------- | ------------------- | ----------------- | -------- |
| F1 Rolling, direct writes   | 0.0 [0.0, 0.0]          | 351.2 [302.2, 405.6]                     | n/a                 | 2.7 [1.3, 4.4]    | 14       |
| F2 Rolling, barrier         | 0.0 [0.0, 0.0]          | 8.8 [0.0, 22.2]                          | 0.0 [0.0, 0.0]      | 18.5 [15.6, 21.6] | 14       |
| F3 Dual-tier, direct writes | 41.1 [26.8, 55.4]       | 345.9 [305.3, 390.3]                     | n/a                 | 3.7 [1.8, 5.7]    | 14       |
| F4 Dual-tier, barrier       | 44.6 [30.4, 59.0]       | 14.0 [4.3, 27.6]                         | 0.0 [0.0, 0.0]      | 18.7 [16.5, 20.9] | 14       |

Live sessions are 39-turn scripts run on the real turn graph, with live probes at fact ages of about 20 to 32 turns. Violations can exceed 100 per 100 transitions because one transition can break several invariants. In F1 and F3, direct writes left the player in a non-existent location on an average of 29.9 and 30.4 of 39 turns per session; the harness then prompted from the last valid location. False rejection is from the lawful twins under the matching probe context.

![Factorial interaction plots](../notebooks/outputs/plots/06_factorial_interaction.png)

_Figure 5. Live recall (left) and violations per 100 transitions (right) for the 2 × 2 design._

![Live violations by oracle code](../notebooks/outputs/plots/11_live_violation_codes.png)

_Figure 6. Live oracle-flagged turns per 100 turns by condition and invariant. Direct writes produce mainly O1 (non-canonical entities), O3 (non-adjacent moves) and O7 (overspending); with the barrier only O5 and O8 remain, below 1 per 100 turns._

Mixed-effects logistic models (memory, control and their interaction as fixed effects; world and session as random intercepts):

| Outcome   | Term           | Coefficient | SE     | z        | p      |
| --------- | -------------- | ----------- | ------ | -------- | ------ |
| Recall    | memory         | 3.5723      | 0.2051 | 17.4174  | <0.001 |
| Recall    | control        | -0.9828     | 0.2823 | -3.4811  | 0.0005 |
| Recall    | memory:control | 1.1711      | 0.2885 | 4.0597   | <0.001 |
| Violation | memory         | 0.3409      | 0.1205 | 2.8282   | 0.0047 |
| Violation | control        | -6.7729     | 0.3043 | -22.2551 | <0.001 |
| Violation | memory:control | -0.1608     | 0.4022 | -0.3997  | 0.6894 |

## Table 4: Ablations

| Ablation                 | Recall, age 20+ (%) | MRR@6                | Committed violations per 100 transitions       | Local compute P50 (ms) | Recovery time at turn 160 (ms) | Replay consistency (%) |
| ------------------------ | ------------------- | -------------------- | ---------------------------------------------- | ---------------------- | ------------------------------ | ---------------------- |
| Full system (F4)         | 87.7 [84.2, 91.0]   | 0.898 [0.878, 0.917] | probes 9.6 [5.5, 14.1]; live 14.0 [4.2, 27.3]  | 41.1                   | 0.5 (snapshot)                 | 100.0 [100.0, 100.0]   |
| A1 No long-term memory   | 0.0 [0.0, 0.0]      | n/a                  | as full system (memory-only change)            | n/a                    | n/a                            | as full system         |
| A2 No short-term buffer  | 89.5 [85.8, 92.9]   | 0.898 [0.878, 0.917] | as full system (memory-only change)            | n/a                    | n/a                            | as full system         |
| A3 No scoping            | 81.8 [77.7, 85.9]   | 0.705 [0.682, 0.727] | as full system (memory-only change)            | n/a                    | n/a                            | as full system         |
| A4 No fallback           | 88.6 [85.5, 91.6]   | 0.950 [0.934, 0.964] | as full system (memory-only change)            | n/a                    | n/a                            | as full system         |
| A5 No validation barrier | as full system      | as full system       | probes 13.1 [9.3, 17.1]; live 11.4 [6.3, 16.5] | 43.3                   | 0.5 (snapshot)                 | 100.0 [100.0, 100.0]   |
| A6 No event sourcing     | as full system      | as full system       | live 351.4 [122.6, 675.0]                      | 10.4                   | no log to recover from         | not replayable         |
| A7 No snapshots          | as full system      | as full system       | as full system                                 | n/a                    | 145.9 (full replay)            | 100 (full fold)        |

The probe violation figures in this table pool all seven worlds; Table 1 uses held-out worlds only. Local compute here is turn time minus LLM time in the batched live sessions.

Replay and recovery (42 CPU sessions of 200 turns, 367.2 events on average):

| Reconstruction                                            | Sessions consistent            |
| --------------------------------------------------------- | ------------------------------ |
| Full fold of the event log                                | 100%                           |
| Latest snapshot plus the events after it                  | 100%                           |
| Both of the above in a fresh process from the SQLite file | 100%                           |
| Backend load path after a crash between commit and save   | 0% (8.0 turns lost on average) |
| Backend load path when the per-turn auto-save succeeded   | 100%                           |

All event-sourced live sessions (F2, F4, A5) also replayed exactly. Replay hashes exclude the active NPC, which is set outside the event log.

![Replay and recovery time](../notebooks/outputs/plots/08_replay_recovery.png)

_Figure 7. Median time to rebuild state at each snapshot point by full replay (A7) and by snapshot loading. Full replay grows with log length; snapshot loading stays near 0.5 ms._

## Table 5: Adversarial Probes by Category

Outputs under all five context conditions are pooled (350 attacks per category). Attack success is a committed oracle violation, or a secret leak for the secret category. False rejection is lawful-twin proposals rejected by the barrier, over lawful-twin proposals. Validator gap is the share of unlawful proposals the barrier accepted.

| Category          | Attack success, direct writes (%) | Attack success, reducer only A5 (%) | Attack success, barrier (%) | False rejection of legitimate twin (%) | Validator gap (%) |
| ----------------- | --------------------------------- | ----------------------------------- | --------------------------- | -------------------------------------- | ----------------- |
| 1 Teleportation   | 15.1 [9.1, 21.7]                  | 2.9 [1.1, 4.9]                      | 0.0 [0.0, 0.0]              | 0.0 [0.0, 0.0]                         | 0.4 [0.0, 1.2]    |
| 2 Fabrication     | 20.9 [13.1, 29.1]                 | 0.0 [0.0, 0.0]                      | 0.0 [0.0, 0.0]              | 0.0 [0.0, 0.0]                         | 0.0 [0.0, 0.0]    |
| 3 Theft           | 33.4 [24.9, 42.3]                 | 3.1 [1.1, 5.7]                      | 0.0 [0.0, 0.0]              | 0.0 [0.0, 0.0]                         | 0.0 [0.0, 0.0]    |
| 4 Trust inflation | 0.0 [0.0, 0.0]                    | 0.0 [0.0, 0.0]                      | 0.0 [0.0, 0.0]              | n/a (no lawful proposals)              | n/a               |
| 5 Currency        | 36.9 [28.3, 45.7]                 | 36.9 [28.3, 45.7]                   | 19.7 [12.3, 27.7]           | 0.0 [0.0, 0.0]                         | 51.9 [36.7, 66.4] |
| 6 Injection       | 6.0 [2.6, 10.3]                   | 6.0 [2.6, 10.3]                     | 0.0 [0.0, 0.0]              | n/a (no lawful proposals)              | 0.0 [0.0, 0.0]    |
| 7 Secret          | 0.9 [0.0, 2.3]                    | 0.9 [0.0, 2.3]                      | 0.9 [0.0, 2.3]              | 0.0 [0.0, 0.0]                         | n/a               |
| All               | 16.2 [13.6, 18.8]                 | 7.1 [5.3, 9.0]                      | 2.9 [1.8, 4.3]              | 0.0 [0.0, 0.0]                         | 11.0 [6.6, 15.7]  |

Oracle codes for the direct-write violations: currency 60 O7 and 69 O8 (and 2 O1); fabrication 73 O1; theft 92 O1, 25 O4 and 14 O2; teleport 52 O3 and 43 O1; injection 18 O4, 5 O6 and 1 O3. The accepted unlawful currency proposals were gains such as a +2,000 delta "for a chest of coins". Secret leak rates: 0.9% [0.0, 2.3] for secret probes, 1.8% [1.1, 2.6] over all attacks, and 0.5% to 2.4% in live sessions. Parse success was 95.8% for probes and 97.6% for live turns.

![Adversarial probes](../notebooks/outputs/plots/05_adversarial_probes.png)

_Figure 8. Left: attack success by commit mode and category. Right: the barrier's false rejection on lawful twins and its validator gap, against the 5% bound of H4._

## Table 6: Per-Stage Latency (Proposed System, Single Stream)

| Stage     | P50 (ms) | P95 (ms) | P99 (ms) |
| --------- | -------- | -------- | -------- |
| Input     | 0.002    | 0.003    | 0.009    |
| Retrieval | 0.174    | 0.310    | 0.385    |
| Prompt    | 0.123    | 0.158    | 0.167    |
| LLM       | see note | see note | see note |
| Parse     | 0.087    | 0.118    | 0.125    |
| Validate  | 0.031    | 0.039    | 0.046    |
| Commit    | 18.428   | 21.049   | 30.311   |
| Output    | 0.011    | 0.013    | 0.013    |
| Local     | 24.921   | 27.526   | 37.016   |

The live F4 graph was timed on 24 turns over two worlds with one request in flight. All 24 LLM responses in that stage were served from the response cache, so its LLM row (0.09 ms at P50) is a cache lookup and is omitted here. Single-stream LLM time, from the recall-prompt benchmark, was P50 6,906 ms and P95 9,409 ms for F4 and P50 10,948 ms and P95 23,984 ms for B0. Under the batched live stage (84 concurrent sessions), the median LLM time per F4 turn was about 89.6 s.

![Latency](../notebooks/outputs/plots/07_latency.png)

_Figure 9. Left: per-stage latency of the F4 graph (log scale). Right: single-stream LLM latency per condition; B2 and B3 were not measured before the stage deadline._

## Table 7: Per-World and Backbone Breakdown

| World  | Backbone        | Recall, age 20+: F4 (%) | Recall, age 20+: best baseline (%) | Attack success: F4 barrier (%) | Attack success: best baseline, direct (%) |
| ------ | --------------- | ----------------------- | ---------------------------------- | ------------------------------ | ----------------------------------------- |
| W1     | K2-Horizon-7B   | 87.0 [75.0, 97.7]       | B2: 87.0 [80.3, 94.2]              | 7.1 [1.4, 14.3]                | B0: 18.6 [10.0, 28.6]                     |
| W2a    | K2-Horizon-7B   | 90.7 [87.1, 95.7]       | B2: 85.2 [80.8, 90.0]              | 2.9 [0.0, 7.1]                 | B0: 17.1 [8.6, 25.7]                      |
| W2b    | K2-Horizon-7B   | 92.6 [86.5, 98.1]       | B2: 87.0 [77.8, 94.6]              | 4.3 [0.0, 10.0]                | B0: 8.6 [2.9, 15.7]                       |
| W2c    | K2-Horizon-7B   | 83.3 [75.0, 91.7]       | B2: 87.0 [78.3, 96.3]              | 2.9 [0.0, 7.1]                 | B2: 10.0 [4.3, 17.1]                      |
| W3     | K2-Horizon-7B   | 79.6 [71.4, 88.6]       | B2: 74.1 [63.8, 83.9]              | 1.4 [0.0, 4.3]                 | B0: 11.4 [4.3, 20.0]                      |
| W4-32  | K2-Horizon-7B   | 87.0 [76.0, 96.4]       | B0: 90.7 [82.6, 96.8]              | 4.3 [0.0, 10.0]                | B0: 15.7 [7.1, 24.3]                      |
| W4-128 | K2-Horizon-7B   | 92.6 [85.7, 100.0]      | B2: 88.9 [81.8, 95.8]              | 2.9 [0.0, 7.1]                 | B0: 14.3 [7.1, 22.9]                      |
| W1     | K2-Horizon-3.7B | 100.0 [100.0, 100.0]    | B2: 88.9 [66.7, 100.0]             | 0.0 [0.0, 0.0]                 | F4 outputs: 22.9 [12.9, 32.9]             |
| W2a    | K2-Horizon-3.7B | 83.3 [66.7, 100.0]      | B2: 72.2 [66.7, 83.3]              | 0.0 [0.0, 0.0]                 | F4 outputs: 14.3 [7.1, 22.9]              |
| W3     | K2-Horizon-3.7B | 66.7 [66.7, 66.7]       | B2: 66.7 [50.0, 83.3]              | 0.0 [0.0, 0.0]                 | F4 outputs: 17.1 [8.6, 25.7]              |
| W4-32  | K2-Horizon-3.7B | 77.8 [50.0, 100.0]      | B0: 66.7 [50.0, 83.3]              | 0.0 [0.0, 0.0]                 | F4 outputs: 20.0 [11.4, 30.0]             |

The best baseline for recall is the highest of B0 to B3 on that world; for attacks it is the baseline context with the lowest direct-write attack success. The 3.7B model ran at horizon 100 with probes under the F4 context only, so its attack comparison is the barrier against direct writes of the same outputs.

![Per-world effects](../notebooks/outputs/plots/10_per_world_effects.png)

_Figure 10. Per-world recall gain of F4 over B1 (left) and attack reduction by the barrier (right). W1 is in-distribution (grey)._

![Seed variance and backbone sensitivity](../notebooks/outputs/plots/12_seed_and_backbone.png)

_Figure 11. Left: recall for three sampling seeds. Right: recall at age 20+ on the secondary-backbone subset for the 7B and 3.7B models._

## Hypothesis Tests

| Hypothesis | Test                                                            | n             | Effect                              | p (Holm) | Verdict       |
| ---------- | --------------------------------------------------------------- | ------------- | ----------------------------------- | -------- | ------------- |
| H1         | recall 20+ F4 vs B1 (McNemar)                                   | 324           | +0.877                              | 3.9e-85  |               |
| H1         | recall 20+ F4 vs B2 (McNemar)                                   | 324           | +0.028                              | 0.298    |               |
| H1         | recall 20+ F4 vs B3 (McNemar)                                   | 324           | +0.238                              | 9.1e-17  | Not supported |
| H2         | MRR@6 F4 vs B2 (Wilcoxon, per probe)                            | 540           | +0.148                              | 4.3e-20  | Supported     |
| H3         | attack success direct vs barrier, F4 context (McNemar)          | 490           | +0.114                              | 9.1e-17  |               |
| H3         | live violations per transition F3 vs F4 (Wilcoxon, per session) | 14            | +3.459                              | 1.9e-3   | Supported     |
| H4         | false rejection at most 5%; validation P95 under 5 ms           |               | 0.0%; 0.039 ms                      |          | Supported     |
| H5         | event-log replay reproduces live state in 100% of sessions      | 42 CPU + live | 100%                                |          | Supported     |
| H6         | factorial interaction small                                     |               | recall interaction 1.17 (p < 0.001) |          | Not supported |
| H7         | direction of H1 and H3 effects on W2, W3, W4                    |               | all positive                        |          | Supported     |

- H1: F4 beats B1 at equal budget and B3, but its gain over B2 is not significant, and it uses more input tokens than both B2 (1,102) and B3 (1,209), so the condition "at equal or lower token cost" fails.
- H5: supported for the event-sourced design. The backend's own load path, which restores the snapshot without the logged suffix, was consistent in 0% of simulated crashes.
- H6: memory drives recall and control drives violations, as predicted, but the recall model has a significant control effect (-0.98, p = 0.0005) and memory × control interaction (1.17, p < 0.001), and the violation model a small but significant memory effect (0.34, p = 0.0047).
- H7: per family, F4 minus B1 recall was +0.889 (W2), +0.796 (W3) and +0.898 (W4); direct minus barrier attack success was +0.114, +0.086 and +0.121.

## Error Analysis

Failures were coded automatically. Counts for the main conditions (up to 50 examples per category and condition are exported for manual review):

| Category                           | F4  | B0  | B1, $B$ | B2  | B3  | A1  | A3  | F2  | A6  |
| ---------------------------------- | --- | --- | ------- | --- | --- | --- | --- | --- | --- |
| Retrieval miss                     | 0   | 0   | 315     | 5   | 11  | 377 | 6   | n/a | n/a |
| Hit but ignored                    | 57  | 106 | 27      | 70  | 142 | 11  | 74  | n/a | n/a |
| Confused with distractor           | 6   | 26  | 89      | 1   | 50  | 132 | 1   | n/a | n/a |
| Schema failure                     | 6   | 7   | 4       | 19  | 9   | 3   | 6   | n/a | n/a |
| Validator gap (probes)             | 17  | 13  | 13      | 13  | 15  | n/a | n/a | n/a | n/a |
| Oracle-detected violation, barrier | 16  | 13  | 13      | 13  | 14  | n/a | n/a | n/a | n/a |
| Desynchronisation (live, proxy)    | 102 | n/a | n/a     | n/a | n/a | n/a | n/a | 101 | 108 |

The system's recall failures are almost all cases where the gold memory was in the prompt but the model answered wrongly; none came from retrieval. Its committed violations under the barrier are almost all validator gaps, which Table 5 places in the currency category.

![GPU utilisation over the run](../notebooks/outputs/plots/13_gpu_utilisation.png)

_Figure 12. GPU utilisation of both T4s over the 6.69-hour run. The gaps are server restarts and CPU-only stages._

# 14. Discussion, Limitations, and Threats to Validity

## Findings

1. Scoped long-term memory is what makes long-range recall possible. Without it, recall beyond the 8-turn buffer is zero, and a rolling context of the same token budget forgets every fact older than 10 turns. With it, recall stays between 83% and 96% from 5 to 160 turns.
2. Against stronger baselines the memory advantage narrows. Flat vector memory reached 84.9% at age 20+ with fewer tokens, and the difference to F4 was not significant. Scoping did improve ranking (MRR@6 0.898 against 0.750 for B2 and 0.705 for the unscoped ablation) and kept the paraphrased distractor out of 43% of prompts, and F4 was the most stable condition across sampling seeds. Generic RAG over raw dialogue and lore degraded with fact age (44.4% at 160 turns).
3. Not every memory component earned its place on this benchmark. Removing the short-term buffer (A2, 89.5%) or the relaxation fallback (A4, 88.6%, MRR@6 0.950) did not lower recall. The benchmark always probes a fact with the NPC it was told to, which favours scoping and gives the fallback little to do; the effect of these components in free play, where facts are often recalled elsewhere, is not measured here.
4. The validation barrier works where it has a rule. Teleport, fabrication, theft and injection attacks succeeded 0.0% of the time through the barrier, against 6% to 33% with direct writes, with no false rejection of lawful requests and negligible validation cost. Much of the protection comes from the reducer alone (7.1% attack success without validation), because it refuses unknown entities; the validator and event-sourced reducer work as a pair, as A6 shows (351.4 live violations per 100 transitions with the validator but in-place mutation).
5. The barrier is only as good as its rule set. The currency rule checks spending but not gains, and the model readily proposed large unearned gains: the barrier accepted 51.9% of unlawful currency proposals and currency attacks succeeded 19.7% of the time. An independent oracle was necessary to see this.
6. Blocking without regenerating has a visible cost. The desynchronisation proxy rose from about 3% to about 19% of live turns once proposals could be rejected, because the NPC's words still describe the rejected change.
7. Event sourcing delivered exact replay in every session and fast recovery from snapshots (about 0.5 ms against 146 ms for a full replay at turn 160). The application's load path does not use the logged suffix, which turns a correct design into a lossy implementation after a crash.
8. The mechanisms are not fully separable. Memory dominates recall (coefficient 3.57) and control dominates violations (-6.77), as designed, but the recall model also has a significant control effect (-0.98) and a positive memory × control interaction (1.17), and the violation model a small memory effect (0.34). In the raw cells the barrier made no difference to recall under rolling memory (0.0% in both) and a small one under dual-tier memory (41.1% against 44.6%), so the interaction should be read with the small number of live sessions in mind.
9. Live recall (41% to 45% with dual-tier memory) was about half of teacher-forced recall. Live memories are written from model-generated summaries and depend on committed movement; the run does not isolate which factor causes the drop.

## Expected Trade-Offs to Examine

- A validation barrier bounds structural violations to the validator's coverage, not to zero in general. Violations outside its rule set (Section 6 coverage gaps) remain possible, which is why an independent oracle is used. The currency result confirms this.
- Blocking an update without regenerating dialogue can make the NPC say something the world does not reflect. The desynchronisation rate quantifies this cost; regeneration on rejection is a candidate fix with a latency cost.
- Scoping can exclude relevant memories created in another location or with another NPC; the relaxation fallback only triggers when scoped results are few, not when they are irrelevant. A3 and A4 measure this.

## Limitations

1. Generalisation: four world families, of which one (W1) is the development world and one (W4) is procedurally templated. Results may not transfer to large commercial worlds, multiplayer settings, or non-fantasy genres beyond the one held-out science fiction world. W3 was not authored independently in this run.
2. Scripted players: fixed player scripts do not adapt to NPC responses. Findings on engagement or experience require a user study, which is outside this article's scope.
3. Backbone dependence: results are reported for two backbones of the same family (K2-Horizon 7B and 3.7B), self-hosted, with a capped thinking budget. The game's default hosted backbone was not evaluated.
4. Latency: measured on two T4 GPUs; the hosted-endpoint latency is not reproduced, and the single-stream LLM row for the live graph was served from cache.
5. Sample size: the run used level 2 of 8 pre-declared levels (63 recall sessions, 490 attacks, 14 live sessions per factorial cell), well below the targets in Section 3. Live-session intervals are wide.
6. Scoring: recall, leaks and desynchronisation are scored automatically. Human labels, inter-rater agreement and an LLM judge are pending.
7. Secrets: NPC secrets are not given to the model, so the low leak rates do not show that the model keeps secrets it knows.
8. Baselines: B4 (scripted FSM) and B5 (MemGPT-style memory) were not run.
9. Validator scope: the validator enforces structural invariants only; narrative plausibility and secret boundaries depend on prompting.
10. Scale of memory: exact FAISS search in process memory with pruning at 1,000 entries; very long campaigns would need summarisation or hierarchical memory.
11. Authoring cost: each world requires a structured seed.

## Threats to Validity

- Internal: identical inputs, prompts, schemas and backbones across conditions; seeds depend on the probe, not the condition, and probe outputs are committed in all three modes, so control comparisons are exactly paired. Residual risk: baseline implementations may be weaker than tuned production systems; baseline code and prompts are in the released notebook.
- Construct: invariant violations are measured by an independent oracle rather than the validator itself. Recall is judged by key-word match against invented-word values; human agreement is pending. Desynchronisation is an automatic proxy based on refusal and arrival cues.
- External: see Limitations 1 to 5. Claims are restricted to the tested worlds and backbones.
- Conclusion: pre-registered hypotheses, Holm correction across the confirmatory family, and confidence intervals; all outcomes are reported, including the two unsupported hypotheses.

# 15. Conclusion

LLM NPCs need to remember what happened, respect the rules of the world, and do so at interactive cost. _The Obsidian Flask_ addresses these with scoped dual-tier memory and a validated, event-sourced state, and this article tests the two mechanisms against independent baselines, in a factorial design, with ablations, adversarial probes scored by an independent oracle, and seven worlds of different authorship and scale.

The evidence from the first full run supports three claims. Long-term retrieval scoped to the current place and person keeps recall high and flat over 160 turns where a rolling context of the same size forgets everything after ten, and it ranks the right memory higher than flat vector memory. A pre-commit barrier over an event-sourced state blocks every movement, fabrication, theft and injection attack the model attempted, without rejecting lawful requests, and the event log reproduces the live state exactly. Both effects hold on every held-out world family and on a smaller backbone. The evidence does not support two others: the memory design is not clearly better than flat vector memory at its token cost, and memory and control are not independent. The run also exposed concrete defects (unbounded currency gains, a load path that ignores the event suffix, and dialogue that contradicts rejected changes) that a validator-only evaluation would have missed.

## Future Work

1. Fix the defects the evaluation found: bound currency gains and check spending per turn, fold the logged suffix on load, event-source the active NPC, align the prompt's trust range with the validator, and pass secrets to the model above the trust threshold.
2. Regenerate or annotate dialogue when updates are rejected, to remove desynchronisation.
3. Rerun at the full sample size with an independently authored W3, human annotation, the hosted backbone, and backbones from other families, and add the B4 and B5 baselines.
4. Validate narrative plausibility, not only structural legality, of state changes.
5. Study why live recall falls below teacher-forced recall, and test the buffer and fallback in free play where facts are recalled away from where they were told.
6. User studies with adaptive human players.
7. Hierarchical or summarised long-term memory for campaigns of thousands of turns.
8. Automatic extraction of world seeds and invariants from existing game content.

# References

- [1] Urbanek, J., Fan, A., Karamcheti, S., Jain, S., Humeau, S., Dinan, E., Rocktäschel, T., Kiela, D., Szlam, A., & Weston, J. (2019). Learning to Speak and Act in a Fantasy Text Adventure Game. In _Proceedings of EMNLP-IJCNLP 2019_, pages 673-683. https://doi.org/10.18653/v1/D19-1062
- [2] Ammanabrolu, P., Urbanek, J., Li, M., Szlam, A., Rocktäschel, T., & Weston, J. (2021). How to Motivate Your Dragon: Teaching Goal-Driven Agents to Speak and Act in Fantasy Worlds. In _Proceedings of NAACL-HLT 2021_, pages 807-833. https://doi.org/10.18653/v1/2021.naacl-main.64
- [3] Park, J. S., O'Brien, J. C., Cai, C. J., Morris, M. R., Liang, P., & Bernstein, M. S. (2023). Generative Agents: Interactive Simulacra of Human Behavior. In _Proceedings of UIST '23_. https://doi.org/10.1145/3586183.3606763
- [4] Gallotta, R., Todd, G., Zammit, M., Earle, S., Liapis, A., Togelius, J., & Yannakakis, G. N. (2024). Large Language Models and Games: A Survey and Roadmap. _IEEE Transactions on Games_. https://doi.org/10.1109/TG.2024.3461510
- [5] Hausknecht, M., Ammanabrolu, P., Côté, M.-A., & Yuan, X. (2020). Interactive Fiction Games: A Colossal Adventure. In _Proceedings of AAAI 2020_, 34(05), pages 7903-7910. https://doi.org/10.1609/aaai.v34i05.6297
- [6] Côté, M.-A., Kádár, Á., Yuan, X., Kybartas, B., Barnes, T., Fine, E., Moore, J., Hausknecht, M., El Asri, L., Adada, M., Tay, W., & Trischler, A. (2019). TextWorld: A Learning Environment for Text-Based Games. In _Computer Games (CGW 2018)_, CCIS vol. 1017, pages 41-75. Springer. https://doi.org/10.1007/978-3-030-24337-1_3
- [7] Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., & Kiela, D. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. In _Advances in Neural Information Processing Systems 33 (NeurIPS 2020)_, pages 9459-9474.
- [8] Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., & Cao, Y. (2023). ReAct: Synergizing Reasoning and Acting in Language Models. In _ICLR 2023_.
- [9] Shinn, N., Cassano, F., Gopinath, A., Narasimhan, K., & Yao, S. (2023). Reflexion: Language Agents with Verbal Reinforcement Learning. In _Advances in Neural Information Processing Systems 36 (NeurIPS 2023)_.
- [10] Callison-Burch, C., Singh Tomar, G., Martin, L. J., Ippolito, D., Bailis, S., & Reitter, D. (2022). Dungeons and Dragons as a Dialog Challenge for Artificial Intelligence. In _Proceedings of EMNLP 2022_, pages 9379-9393. https://aclanthology.org/2022.emnlp-main.637/
- [11] Akoury, N., Wang, S., Whiting, J., Hood, S., Peng, N., & Iyyer, M. (2020). STORIUM: A Dataset and Evaluation Platform for Machine-in-the-Loop Story Generation. In _Proceedings of EMNLP 2020_, pages 6470-6484. https://doi.org/10.18653/v1/2020.emnlp-main.525
- [12] Packer, C., Wooders, S., Lin, K., Fang, V., Patil, S. G., Stoica, I., & Gonzalez, J. E. (2023). MemGPT: Towards LLMs as Operating Systems. _arXiv:2310.08560_.
- [13] Maharana, A., Lee, D.-H., Tulyakov, S., Bansal, M., Barbieri, F., & Fang, Y. (2024). Evaluating Very Long-Term Conversational Memory of LLM Agents. In _Proceedings of ACL 2024 (Volume 1: Long Papers)_, pages 13851-13870. https://aclanthology.org/2024.acl-long.747/
- [14] Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., & Liang, P. (2024). Lost in the Middle: How Language Models Use Long Contexts. _Transactions of the Association for Computational Linguistics_, 12, pages 157-173. https://doi.org/10.1162/tacl_a_00638
