"""LangGraph orchestration for one gameplay turn."""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, List, Optional

import config
from core.event_store import EventStore
from core.reducer import apply_event
from core.snapshot import save_snapshot
from game.validator import validate_and_build_events
from langgraph.graph import END, StateGraph
from llm.groq_client import GroqClient
from llm.prompt_builder import build_prompt
from memory.embedder import Embedder
from memory.faiss_index import FAISSMemory
from memory.short_term import ShortTermMemory
from schemas.events import Event, EventType
from schemas.llm_output import LLMOutput
from schemas.world_state import WorldState
from typing_extensions import TypedDict

log = logging.getLogger(__name__)


class TurnState(TypedDict):
    player_input: str
    active_npc_id: Optional[str]
    world: WorldState
    query_vec: Optional[Any]
    retrieved_memories: List[Any]
    prompt: str
    raw_llm_output: str
    parsed_output: Optional[LLMOutput]
    valid_events: List[Event]
    validation_errors: List[str]
    narration: str
    npc_dialogue: str
    turn_errors: List[str]
    elapsed_ms: float


def node_input(state: TurnState) -> TurnState:
    """Validate presence of required inputs."""
    if not state.get("player_input", "").strip():
        state["player_input"] = "(silence)"
    return state


def make_node_retrieval(
    embedder: Embedder, memory: FAISSMemory, top_k: int = config.TOP_K_RETRIEVAL
):
    def node_retrieval(state: TurnState) -> TurnState:
        started_at = time.perf_counter()
        vec = embedder.embed(state["player_input"])
        state["query_vec"] = vec

        world = state["world"]
        results = memory.search(
            vec,
            top_k=top_k,
            filter_location=world.player.current_location_id,
            filter_npc=state["active_npc_id"] or "",
        )
        if len(results) < config.RETRIEVAL_MIN_CANDIDATES:
            results = memory.search(vec, top_k=top_k)

        state["retrieved_memories"] = results
        log.debug(
            "memories retrieved",
            extra={
                "count": len(results),
                "ms": round((time.perf_counter() - started_at) * 1000),
            },
        )
        return state

    return node_retrieval


def make_node_prompt_assembly(
    short_term: ShortTermMemory, max_chars: int = config.MAX_CONTEXT_CHARS
):
    def node_prompt_assembly(state: TurnState) -> TurnState:
        state["prompt"] = build_prompt(
            world=state["world"],
            active_npc_id=state["active_npc_id"],
            player_input=state["player_input"],
            memories=state["retrieved_memories"],
            history=short_term.format_for_prompt(),
            max_chars=max_chars,
        )
        log.debug("prompt built", extra={"chars": len(state["prompt"])})
        return state

    return node_prompt_assembly


def make_node_llm_generation(client: GroqClient):
    def node_llm_generation(state: TurnState) -> TurnState:
        started_at = time.perf_counter()
        raw = client.generate(
            state["prompt"],
            max_tokens=config.MAX_GENERATION_TOKENS,
            temperature=config.TEMPERATURE,
            stream=False,
        )
        state["raw_llm_output"] = raw
        state["elapsed_ms"] = (time.perf_counter() - started_at) * 1000
        return state

    return node_llm_generation


def node_json_parsing(state: TurnState) -> TurnState:
    raw = state.get("raw_llm_output") or ""
    parsed_dict = GroqClient.extract_json(raw)
    if parsed_dict is None:
        log.warning("llm output is not JSON; using raw text as dialogue")
        state["parsed_output"] = None
        state["turn_errors"] = state.get("turn_errors", []) + ["JSON parse failed"]
        state["npc_dialogue"] = raw.strip() or "..."
        return state

    try:
        output = LLMOutput(**parsed_dict)
        state["parsed_output"] = output
        state["npc_dialogue"] = output.npc_response
        state["narration"] = output.narration
    except Exception as exc:
        log.warning(
            "llm output failed schema validation",
            extra={"error": str(exc).splitlines()[0]},
        )
        state["parsed_output"] = None
        state["npc_dialogue"] = parsed_dict.get("npc_response", raw.strip() or "...")
        state["narration"] = parsed_dict.get("narration", "")
        state["turn_errors"] = state.get("turn_errors", []) + [f"Schema error: {exc}"]

    return state


def make_node_world_validation():
    def node_world_validation(state: TurnState) -> TurnState:
        output = state.get("parsed_output")
        if output is None:
            state["valid_events"] = []
            state["validation_errors"] = ["No parsed output to validate"]
            return state

        turn = state["world"].turn + 1
        valid_events, errors = validate_and_build_events(output, state["world"], turn)
        state["valid_events"] = valid_events
        state["validation_errors"] = errors
        return state

    return node_world_validation


def make_node_event_commit(
    store: EventStore,
    memory: FAISSMemory,
    embedder: Embedder,
    short_term: ShortTermMemory,
    snapshot_path: Optional[Path],
    snapshot_interval: int,
):
    def node_event_commit(state: TurnState) -> TurnState:
        world = state["world"]
        turn = world.turn + 1
        active_npc_id = state["active_npc_id"] or "narrator"

        spoke_event = Event(
            turn=turn,
            event_type=EventType.NPC_SPOKE,
            payload={
                "npc_id": active_npc_id,
                "text": state["npc_dialogue"][: config.DIALOGUE_EVENT_TRUNCATE_CHARS],
            },
        )
        store.append(spoke_event)

        for event in state["valid_events"]:
            store.append(event)
            world = apply_event(world, event)

        world.turn = turn

        short_term.record(
            turn=turn,
            player_input=state["player_input"],
            npc_response=state["npc_dialogue"],
            npc_id=active_npc_id,
        )

        output = state.get("parsed_output")
        summary = (
            output.memory_summary
            if output and output.memory_summary
            else f"Turn {turn}: {state['player_input'][:config.MEMORY_FALLBACK_TRUNCATE_CHARS]}"
        )
        if state.get("query_vec") is not None:
            vec = state["query_vec"]
        else:
            vec = embedder.embed(summary)

        memory.add(
            vec=vec,
            text=summary,
            location_id=world.player.current_location_id,
            npc_id=active_npc_id,
            turn=turn,
        )

        if len(memory) > config.MEMORY_PRUNE_THRESHOLD:
            memory.prune_oldest(
                int(config.MEMORY_PRUNE_THRESHOLD * config.MEMORY_PRUNE_KEEP_RATIO)
            )

        if turn % snapshot_interval == 0:
            if snapshot_path is not None:
                save_snapshot(world, snapshot_path, store.get_last_id())
            memory.save()
            log.debug("periodic snapshot saved", extra={"turn": turn})

        state["world"] = world
        return state

    return node_event_commit


def node_output(state: TurnState) -> TurnState:
    """Log one summary line per turn."""
    log.info(
        "turn complete",
        extra={
            "turn": state["world"].turn,
            "npc": state.get("active_npc_id") or "narrator",
            "llm_ms": round(state.get("elapsed_ms", 0)),
            "memories": len(state.get("retrieved_memories", [])),
            "events": len(state.get("valid_events", [])),
            "rejected": len(state.get("validation_errors", [])),
        },
    )
    return state


def build_graph(
    store: EventStore,
    embedder: Embedder,
    memory: FAISSMemory,
    short_term: ShortTermMemory,
    client: GroqClient,
    snapshot_path: Optional[Path] = None,
    snapshot_interval: int = config.SNAPSHOT_INTERVAL,
):
    """Build and compile the LangGraph execution graph."""
    graph = StateGraph(TurnState)
    graph.add_node("input", node_input)
    graph.add_node("retrieval", make_node_retrieval(embedder, memory))
    graph.add_node("prompt", make_node_prompt_assembly(short_term))
    graph.add_node("llm", make_node_llm_generation(client))
    graph.add_node("parse", node_json_parsing)
    graph.add_node("validate", make_node_world_validation())
    graph.add_node(
        "commit",
        make_node_event_commit(
            store,
            memory,
            embedder,
            short_term,
            snapshot_path,
            snapshot_interval,
        ),
    )
    graph.add_node("output", node_output)

    graph.set_entry_point("input")
    graph.add_edge("input", "retrieval")
    graph.add_edge("retrieval", "prompt")
    graph.add_edge("prompt", "llm")
    graph.add_edge("llm", "parse")
    graph.add_edge("parse", "validate")
    graph.add_edge("validate", "commit")
    graph.add_edge("commit", "output")
    graph.add_edge("output", END)

    return graph.compile()
