# Memory and State Control for LLM-Driven NPC Dialogue: A Controlled Comparison of Dual-Tier Memory and Pre-Commit Invariant Validation against Rolling-Context, Vector-Memory, and Generic RAG Agents

Source Code Repository: [https://github.com/parthmital/RAG-Driven-NPC-Narrative-Engine](https://github.com/parthmital/RAG-Driven-NPC-Narrative-Engine)

## Abstract

Large Language Models (LLMs) allow Non-Player Characters (NPCs) in interactive fiction to hold open-ended conversations, but three problems limit their use in games: facts established early in a session are forgotten as dialogue grows, model-proposed world changes break symbolic game rules (illegal moves, fabricated items, unbounded trust shifts), and per-turn cost and latency grow with context length. This article presents _The Obsidian Flask_, an NPC dialogue engine that separates language generation from state control. It combines (i) a dual-tier memory, an 8-turn short-term buffer plus a 384-dimensional FAISS store with location- and NPC-scoped retrieval and a relaxation fallback, with (ii) an event-sourced world state in which every LLM-proposed mutation passes a pre-commit invariant-validation barrier before a pure reducer applies it. The central question is not whether the system works in its own world but whether its two mechanisms, memory tiering and state control, outperform independent baselines and whether each contributes separately. We therefore specify a controlled comparison against three independent baseline agents (rolling-context, vector-memory, and generic RAG), a full-history reference, and a $2 \times 2$ factorial crossing of memory architecture with state control, plus seven single-component ablations. Evaluation spans long-horizon sessions of 50, 100 and 200 turns and 7 categories of adversarial invariant probes across four worlds that differ in authorship, genre, and scale (8 to 128 locations), including worlds converted from the externally authored LIGHT corpus and procedurally generated worlds. We report factual recall by fact-age, invariant violations measured by an oracle independent of the system's own validator, retrieval MRR and Recall@k, latency percentiles, token cost, and state-replay consistency, with bootstrap confidence intervals and pre-registered hypotheses. Quantitative results from the protocol are reported in Section 13; cells not yet populated by the evaluation harness are marked as pending rather than estimated.

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
- Feasibility: embedding, retrieval, validation, and reduction run locally on CPU; LLM inference is delegated to a hosted endpoint, with a local open-weight backbone used as a latency control (Section 11).

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
3. W3, Held-out genre (science fiction station): 1 world of 24 locations and 6 NPCs, authored by a contributor not involved in system development, following a written specification. Frozen before any system run on it.
4. W4, Procedural scaling worlds: generated graphs of 32 and 128 locations with 8 to 16 NPCs and 16 to 64 objects from a seeded generator, to test retrieval and validation at larger scale. Names and descriptions are templated, so W4 tests structure rather than prose quality.

No system hyperparameter (buffer size, k, fallback threshold, prompt wording) is tuned on W2 to W4.

## Long-Horizon Session Benchmark

- Scripted player sessions of 50, 100, and 200 turns. Player turns are fixed scripts, so every system receives identical inputs; this removes player-adaptation confounds at the cost of realism (Section 14).
- Each session plants facts (player disclosures, NPC commitments, object transfers, location events) and later probes them at fact ages of 5, 10, 20, 40, 80, and 160 turns, with fact age bucketed for analysis.
- Each probe has a gold answer and a set of gold-relevant memory turn IDs for retrieval scoring.
- Distractor turns include paraphrased near-duplicate facts and facts from other locations or NPCs, to test scoping.
- Target size: 40 sessions per world per horizon where the world is large enough, giving approximately 480 sessions in total.

## Adversarial Invariant Probe Suite

Probes are player turns designed to induce an illegal mutation. Seven categories, each instantiated per world from templates plus hand-written variants:

1. Spatial teleportation: requests to move to non-adjacent or non-existent locations.
2. Item fabrication: requests for items that do not exist in the world.
3. Item theft or duplication: taking objects not present in the current location, or already held.
4. Trust inflation: pressure for single-turn trust changes above the per-turn bound.
5. Currency exploits: spending more than held or requesting unearned currency.
6. Prompt injection: player text that instructs the model to emit specific world updates or ignore rules.
7. Lore and secret violations: attempts to make an NPC reveal a secret before its trust threshold or contradict canonical lore.

Categories 1 to 5 are checkable by the symbolic oracle; categories 6 and 7 are scored by the oracle where they produce mutations and by annotation where they affect only dialogue. Target size: 60 probes per category per world family, approximately 1,680 probes. Each probe also has a legitimate twin (a lawful version of the same request) to measure false rejection.

## Annotation and Quality Control

- Two annotators label recall correctness and lore violations on a stratified 20% sample; agreement is reported as Cohen's kappa. Remaining items are scored by an LLM judge whose agreement with the human labels is reported; the judge is a different model family from the system backbone.
- Annotators are blind to which system produced each output.

## Preprocessing

- Embeddings: sentence-transformers/all-MiniLM-L12-v2, 384 dimensions, L2-normalised, so inner product equals cosine similarity.
- Index: FAISS IndexFlatIP with per-entry metadata (turn, location ID, NPC ID, summary text).
- Output contract: Pydantic v2 schemas ([llm_output.py](../Backend/schemas/llm_output.py)) for dialogue, narration, memory summary, and proposed world updates.

## Release

World seeds, session scripts, probes, gold annotations, raw logs, and the evaluation harness will be released with the paper, subject to LIGHT's non-commercial licence for W2 content.

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
S_{t+1} = \delta(S_t, e_t), \qquad S_T = \operatorname{foldl}(\delta, S_0, [e_0, \dots, e_{T-1}])
$$

Snapshots every 16 turns bound recovery to loading the latest snapshot and folding the remaining suffix. Replay consistency is therefore expected by construction for the reducer; Section 12 tests it empirically, including across process restarts and against snapshot-plus-suffix reconstruction, because implementation defects (non-deterministic iteration order, timestamps inside state, floating-point effects) can break construction-level guarantees.

## Dual-Tier Memory Retrieval

For player input $u_t$, the embedder produces a unit vector $q_t \in \mathbb{R}^{384}$. Long-term entries $m_i$ are unit vectors of past turn summaries with metadata $(t_i, \text{loc}_i, \text{npc}_i)$.

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

# 7. Research Methodology

1. Specify invariants and the event schema.
2. Build the four-world suite, session scripts, probes, and gold annotations; freeze W2 to W4 before any system run on them.
3. Implement the proposed system and all baselines on a shared harness (Section 11) so that only the studied factor differs between conditions.
4. Implement an independent invariant oracle (Section 12) that shares no code with the validator.
5. Run all conditions on all sessions and probes with three sampling seeds and two LLM backbones.
6. Compute metrics, confidence intervals, and hypothesis tests; run the factorial and ablation analyses.
7. Conduct error analysis on a stratified sample of failures per condition.

# 8. Technology Choices

- Inference: Groq-hosted `openai/gpt-oss-120b` (the configured default in [config.py](../Backend/config.py)), temperature 0.35. A second backbone (an open-weight model of a different family) tests backbone sensitivity; a locally hosted model gives a network-free latency control.
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

# 12. Metrics

1. Factual recall: proportion of recall probes answered correctly against gold, reported overall and by fact-age bucket (5, 10, 20, 40, 80, 160 turns).
2. Invariant violations:
   - Committed violation rate: oracle-detected violations per 100 committed state transitions, and proportion of sessions with at least one violation.
   - Probe attack success rate: proportion of adversarial probes that result in a committed violation, per category.
   - False rejection rate: proportion of legitimate-twin updates rejected by the barrier.
   - Dialogue-state desynchronisation: proportion of turns where the NPC's dialogue asserts a state change that was not committed, or vice versa (annotated sample).
   - The oracle is a separate implementation that re-derives world facts from the post-turn state and checks conservation (each object in exactly one place), adjacency of moves, bounds, and entity canonicity. It shares no code with the validator, so the barrier's own acceptance decisions are not used to score it.
3. Retrieval quality: MRR@6 and Recall@6 against gold-relevant memory IDs, for retrieval conditions. For rolling-context conditions, the in-context presence rate of the gold turn is reported instead.
4. Latency: end-to-end P50, P95, and P99, split into local compute and LLM time; reported for the hosted backbone and the local latency-control backbone.
5. Token cost: mean input and output tokens per turn from API usage fields, and cost per 100 turns at the provider's list price on the run date.
6. State-replay consistency: proportion of sessions where the state rebuilt from the seed plus the logged events matches the live final state by canonical hash, tested (a) by full fold, (b) by snapshot plus suffix, (c) after a forced process restart mid-session. For direct-write conditions without an event log, replay uses the recorded mutation sequence where one exists and is otherwise reported as not replayable.
7. Secondary: schema parse success rate, secret-leak rate before trust threshold, and persona consistency (blind 1 to 5 rating on a sample, with inter-rater agreement).

## Statistical Analysis

- Unit of analysis: session for session-level metrics, probe for probe metrics.
- 95% confidence intervals by session-level bootstrap (10,000 resamples).
- Paired comparisons against the proposed system: McNemar's test for binary per-probe outcomes and Wilcoxon signed-rank for continuous per-session metrics, with Holm-Bonferroni correction across the hypothesis family.
- Factorial effects: mixed-effects logistic regression with memory, control, and their interaction as fixed effects and world and session as random effects.
- Effect sizes are reported alongside p-values.

# 13. Results

This section reports results from the protocol above. Cells marked "Pending" are not yet produced by the harness. No value in this section is estimated, extrapolated, or carried over from earlier prototype runs, which used a different configuration and are superseded.

Values are formatted as mean [95% CI] pooled over held-out worlds W2 to W4 unless stated; W1 results appear in the per-world table.

## Table 1: Main Comparison (Held-Out Worlds)

| Condition                  | Recall, age 20+ | Committed violations per 100 transitions | Probe attack success | MRR@6   | P50 / P95 latency (ms) | Input tokens per turn | Replay consistency |
| -------------------------- | --------------- | ---------------------------------------- | -------------------- | ------- | ---------------------- | --------------------- | ------------------ |
| B0 Full history            | Pending         | Pending                                  | Pending              | n/a     | Pending                | Pending               | Pending            |
| B1 Rolling context, $B$    | Pending         | Pending                                  | Pending              | n/a     | Pending                | Pending               | Pending            |
| B1 Rolling context, ${2B}$ | Pending         | Pending                                  | Pending              | n/a     | Pending                | Pending               | Pending            |
| B2 Vector memory           | Pending         | Pending                                  | Pending              | Pending | Pending                | Pending               | Pending            |
| B3 Generic RAG             | Pending         | Pending                                  | Pending              | Pending | Pending                | Pending               | Pending            |
| Proposed (F4)              | Pending         | Pending                                  | Pending              | Pending | Pending                | Pending               | Pending            |

## Table 2: Recall by Fact Age

| Condition    | 5       | 10      | 20      | 40      | 80      | 160     |
| ------------ | ------- | ------- | ------- | ------- | ------- | ------- |
| B0 to B3, F4 | Pending | Pending | Pending | Pending | Pending | Pending |

## Table 3: Factorial Separation (Memory × Control)

| Cell                        | Recall, age 20+ | Committed violations per 100 transitions | False rejection | Desync rate |
| --------------------------- | --------------- | ---------------------------------------- | --------------- | ----------- |
| F1 Rolling, direct writes   | Pending         | Pending                                  | n/a             | Pending     |
| F2 Rolling, barrier         | Pending         | Pending                                  | Pending         | Pending     |
| F3 Dual-tier, direct writes | Pending         | Pending                                  | n/a             | Pending     |
| F4 Dual-tier, barrier       | Pending         | Pending                                  | Pending         | Pending     |

## Table 4: Ablations

| Ablation    | Recall, age 20+ | MRR@6   | Committed violations | P50 latency | Recovery time at turn 160 | Replay consistency |
| ----------- | --------------- | ------- | -------------------- | ----------- | ------------------------- | ------------------ |
| Full system | Pending         | Pending | Pending              | Pending     | Pending                   | Pending            |
| A1 to A7    | Pending         | Pending | Pending              | Pending     | Pending                   | Pending            |

## Table 5: Adversarial Probes by Category

| Category          | Attack success, direct writes | Attack success, barrier | False rejection of legitimate twin |
| ----------------- | ----------------------------- | ----------------------- | ---------------------------------- |
| Categories 1 to 7 | Pending                       | Pending                 | Pending                            |

## Table 6: Per-Stage Latency (Proposed System)

| Stage                                                          | P50 (ms) | P95 (ms) |
| -------------------------------------------------------------- | -------- | -------- |
| Input, retrieval, prompt, LLM, parse, validate, commit, output | Pending  | Pending  |

## Table 7: Per-World and Backbone Breakdown

| World    | Backbone           | Recall, age 20+ (F4 vs best baseline) | Committed violations (F4 vs best baseline) |
| -------- | ------------------ | ------------------------------------- | ------------------------------------------ |
| W1 to W4 | Primary, secondary | Pending                               | Pending                                    |

## Error Analysis

For each condition, 50 failures per metric are sampled and coded into categories (retrieval miss, retrieval hit but ignored by the model, scoping excluded the gold memory, schema failure, validator gap, oracle-detected violation, desynchronisation). Pending.

# 14. Discussion, Limitations, and Threats to Validity

## Expected Trade-Offs to Examine

- A validation barrier bounds structural violations to the validator's coverage, not to zero in general. Violations outside its rule set (Section 6 coverage gaps) remain possible, which is why an independent oracle is used.
- Blocking an update without regenerating dialogue can make the NPC say something the world does not reflect. The desynchronisation rate quantifies this cost; regeneration on rejection is a candidate fix with a latency cost.
- Scoping can exclude relevant memories created in another location or with another NPC; the relaxation fallback only triggers when scoped results are few, not when they are irrelevant. A3 and A4 measure this.

## Limitations

1. Generalisation: four world families, of which one (W1) is the development world and one (W4) is procedurally templated. Results may not transfer to large commercial worlds, multiplayer settings, or non-fantasy genres beyond the one held-out science fiction world.
2. Scripted players: fixed player scripts do not adapt to NPC responses. Findings on engagement or experience require a user study, which is outside this article's scope.
3. Backbone dependence: results are reported for two backbones; behaviour on other models may differ.
4. Hosted-endpoint latency: network and provider load affect latency; the local backbone control mitigates but does not eliminate this.
5. Validator scope: the validator enforces structural invariants only; narrative plausibility and secret boundaries depend on prompting.
6. Scale of memory: exact FAISS search in process memory with pruning at 1,000 entries; very long campaigns would need summarisation or hierarchical memory.
7. Authoring cost: each world requires a structured seed.

## Threats to Validity

- Internal: identical inputs, prompts, schemas, and backbones across conditions; seeds and interleaved scheduling reduce run-order effects. Residual risk: baseline implementations may be weaker than tuned production systems; baseline code and prompts are released for scrutiny.
- Construct: invariant violations are measured by an independent oracle rather than the validator itself; recall is judged against gold facts with human agreement reported; the LLM judge is validated against human labels.
- External: see Limitations 1 to 3. Claims are restricted to the tested worlds and backbones.
- Conclusion: pre-registered hypotheses, multiple-comparison correction, and confidence intervals; all outcomes reported, including null or negative results.

# 15. Conclusion

LLM NPCs need to remember what happened, respect the rules of the world, and do so at interactive cost. _The Obsidian Flask_ addresses these with scoped dual-tier memory and a validated, event-sourced state. This revision reframes the work as a controlled test of those two mechanisms: independent rolling-context, vector-memory, and generic RAG baselines; a factorial separation of memory and state control; single-component ablations; adversarial probes scored by an independent oracle; and a four-family world suite that tests generalisation beyond the development world. The claims of the article are limited to what the results in Section 13 support once populated.

## Future Work

1. Regenerating dialogue when updates are rejected, to remove desynchronisation.
2. Validating narrative plausibility, not only structural legality, of state changes.
3. User studies with adaptive human players.
4. Hierarchical or summarised long-term memory for campaigns of thousands of turns.
5. Automatic extraction of world seeds and invariants from existing game content.

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
