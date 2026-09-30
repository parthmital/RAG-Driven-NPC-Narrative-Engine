"""Session lifecycle and orchestration for isolated game instances."""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import config
from core.event_store import EventStore
from core.reducer import apply_event, rebuild_state
from core.snapshot import load_snapshot, save_snapshot
from game.world_loader import load_world_seed
from graph.definition import TurnState, build_graph
from llm.groq_client import GroqClient
from memory.embedder import Embedder
from memory.faiss_index import FAISSMemory
from memory.short_term import ShortTermMemory
from schemas.events import Event, EventType
from schemas.world_state import WorldState
from session import save_files
from session.dialogue import narration_entry
from session.game_session import GameSession

log = logging.getLogger(__name__)


class SessionManager:
    """Creates, stores, retrieves, and destroys game sessions."""

    def __init__(self):
        self._sessions: Dict[str, GameSession] = {}
        self._embedder: Optional[Embedder] = None
        self._client: Optional[GroqClient] = None
        self._seed: Optional[WorldState] = None
        self._initialised = False
        self._init_lock = asyncio.Lock()

    async def initialise(self) -> None:
        """Load the world seed, embedding model, and LLM client once."""
        if self._initialised:
            return
        async with self._init_lock:
            if self._initialised:
                return

            self._seed = await asyncio.to_thread(
                load_world_seed, config.WORLD_SEED_PATH
            )
            self._embedder = await asyncio.to_thread(
                Embedder,
                config.EMBEDDING_MODEL,
                config.EMBED_CACHE_PATH,
                config.EMBEDDING_DIM,
            )
            self._client = GroqClient(
                model=config.MODEL_NAME,
                api_key=config.GROQ_API_KEY,
                timeout=config.REQUEST_TIMEOUT,
            )
            await asyncio.to_thread(self._embedder.embed, config.EMBEDDING_WARMUP_TEXT)
            self._initialised = True

    def _open_session(
        self,
        session_id: str,
        data_dir: Path,
        store: EventStore,
        world: WorldState,
        active_npc_id: Optional[str],
        dialogue_history: Optional[list] = None,
    ) -> GameSession:
        """Wire per-session memory and the turn graph around a world state."""
        faiss_mem = FAISSMemory(
            data_dir / config.FAISS_INDEX_FILENAME,
            data_dir / config.FAISS_META_FILENAME,
            config.EMBEDDING_DIM,
        )
        short_term = ShortTermMemory(config.MAX_SHORT_TERM_TURNS)
        graph = build_graph(
            store,
            self._embedder,
            faiss_mem,
            short_term,
            self._client,
            snapshot_path=save_files.snapshot_path(data_dir, is_auto=True),
        )
        return GameSession(
            session_id=session_id,
            world=world,
            graph=graph,
            store=store,
            faiss_mem=faiss_mem,
            short_term=short_term,
            active_npc_id=active_npc_id,
            data_dir=data_dir,
            dialogue_history=dialogue_history,
        )

    async def create_session(
        self,
        name: str,
        gender: str,
        age: int,
        occupation: str,
        reset: bool = False,
    ) -> GameSession:
        await self.initialise()

        if len(self._sessions) >= config.MAX_CONCURRENT_SESSIONS:
            raise RuntimeError(
                f"Maximum concurrent sessions ({config.MAX_CONCURRENT_SESSIONS}) reached"
            )

        session_id = str(uuid.uuid4())
        data_dir = save_files.session_dir(session_id)
        data_dir.mkdir(parents=True, exist_ok=True)

        def _create():
            store = EventStore(data_dir / config.EVENTS_DB_FILENAME)
            world = self._seed.model_copy(deep=True)

            world.player.name = name
            world.player.gender = gender
            world.player.age = age
            world.player.occupation = occupation
            world.player.moral_alignment = config.INITIAL_MORAL_ALIGNMENT
            world.active_npc_id = None

            store.append(Event(turn=0, event_type=EventType.SESSION_START, payload={}))
            return self._open_session(session_id, data_dir, store, world, None)

        session = await asyncio.to_thread(_create)
        self._sessions[session_id] = session

        if self._seed and self._seed.metadata.initial_narrator_message:
            session.dialogue_history.append(
                narration_entry(
                    f"init_{int(time.time() * 1000)}",
                    self._seed.metadata.initial_narrator_message,
                )
            )

        await self.save_session(session_id, is_auto=True)

        log.info("session created", extra={"session": session_id, "player": name})
        return session

    async def list_sessions(self) -> List[Dict[str, Any]]:
        """List all sessions saved on disk."""
        return save_files.list_saves()

    async def load_session(self, save_id: str) -> Optional[GameSession]:
        """Load a session save ("<id>" or "<id>:<manual|auto>") from disk."""
        session_id, save_type = save_files.split_save_id(save_id)
        is_auto = save_type != "manual"

        if session_id in self._sessions:
            self._sessions.pop(session_id).close()

        await self.initialise()
        data_dir = save_files.session_dir(session_id)
        if not data_dir.exists():
            return None

        def _load():
            store = EventStore(data_dir / config.EVENTS_DB_FILENAME)
            snap = load_snapshot(save_files.snapshot_path(data_dir, is_auto))
            if snap:
                world, _last_id = snap
            else:
                world = rebuild_state(
                    self._seed.model_copy(deep=True), store.load_all()
                )

            npc_id = world.active_npc_id or next(iter(world.npcs.keys()), None)
            dialogue_history = save_files.load_dialogue(
                save_files.dialogue_path(data_dir, is_auto)
            )
            return self._open_session(
                session_id, data_dir, store, world, npc_id, dialogue_history
            )

        try:
            session = await asyncio.to_thread(_load)
        except Exception:
            log.exception("session load failed", extra={"save": save_id})
            return None
        self._sessions[session_id] = session
        log.info("session loaded", extra={"save": save_id, "turn": session.world.turn})
        return session

    def get_session(self, save_id: str) -> Optional[GameSession]:
        return self._sessions.get(save_files.split_save_id(save_id)[0])

    def destroy_session(self, save_id: str) -> bool:
        session_id = save_files.split_save_id(save_id)[0]
        session = self._sessions.pop(session_id, None)
        if session is None:
            return False
        session.close()
        log.info("session closed", extra={"session": session_id})
        return True

    async def save_session(self, session_id: str, is_auto: bool = False) -> bool:
        """Persist session state to disk."""
        session = self.get_session(session_id)
        if not session:
            return False

        def _save():
            session.faiss_mem.save()
            save_snapshot(
                session.world,
                save_files.snapshot_path(session.data_dir, is_auto),
                session.store.get_last_id(),
            )
            save_files.save_dialogue(
                save_files.dialogue_path(session.data_dir, is_auto),
                session.dialogue_history,
            )

        await asyncio.to_thread(_save)
        if not is_auto:
            log.info("game saved", extra={"session": session_id})
        return True

    async def commit_event(
        self, session: GameSession, event: Event, advance_turn: bool = False
    ) -> None:
        """Append a player-driven event, reduce it, and auto-save."""
        session.store.append(event)
        session.world = apply_event(session.world, event)
        if advance_turn:
            session.world.turn = event.turn
        await self.save_session(session.session_id, is_auto=True)

    async def process_action(
        self, session: GameSession, player_input: str, npc_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a player action through the LangGraph pipeline."""
        async with session.lock:
            active_npc = npc_id or session.active_npc_id

            turn_state: TurnState = {
                "player_input": player_input,
                "active_npc_id": active_npc,
                "world": session.world,
                "query_vec": None,
                "retrieved_memories": [],
                "prompt": "",
                "raw_llm_output": "",
                "parsed_output": None,
                "valid_events": [],
                "validation_errors": [],
                "narration": "",
                "npc_dialogue": "",
                "turn_errors": [],
                "elapsed_ms": 0.0,
            }

            result = await asyncio.to_thread(session.graph.invoke, turn_state)

            session.world = result["world"]
            session.active_npc_id = result.get("active_npc_id", active_npc)
            session.world.active_npc_id = session.active_npc_id

            trust_change = 0
            events_out = []
            for event in result.get("valid_events", []):
                events_out.append(
                    {
                        "type": event.event_type.value,
                        "payload": event.payload,
                    }
                )
                if (
                    event.event_type == EventType.RELATIONSHIP_CHANGED
                    and event.payload.get("target_id") == "player"
                ):
                    trust_change += int(event.payload.get("delta", 0))

            parsed = result.get("parsed_output")
            speaker_id = active_npc or "narrator"
            if parsed and parsed.speaker_id:
                speaker_id = parsed.speaker_id

            npc_obj = session.world.npcs.get(speaker_id)
            if speaker_id == "narrator":
                npc_name = "Narrator"
            else:
                npc_name = npc_obj.name if npc_obj else speaker_id

            return {
                "npc_dialogue": result.get("npc_dialogue", "").strip(),
                "narration": result.get("narration", "").strip(),
                "npc_id": speaker_id,
                "npc_name": npc_name,
                "turn": session.world.turn,
                "trust_change": trust_change,
                "validation_errors": result.get("validation_errors", []),
                "elapsed_ms": result.get("elapsed_ms", 0.0),
                "events": events_out,
            }

    @property
    def active_session_count(self) -> int:
        return len(self._sessions)

    @property
    def is_ready(self) -> bool:
        return self._initialised

    def ping_llm(self) -> bool:
        if self._client:
            return self._client.ping()
        return False

    async def shutdown(self) -> None:
        """Close all sessions on server shutdown."""
        for session_id in list(self._sessions.keys()):
            self.destroy_session(session_id)
        if self._embedder:
            self._embedder.close()
        log.info("shutdown complete")
