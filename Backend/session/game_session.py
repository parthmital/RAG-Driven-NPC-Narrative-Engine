"""Mutable runtime state for one game session."""

from __future__ import annotations

import asyncio
import logging
import time
from pathlib import Path
from typing import Any, Optional, Set

from core.event_store import EventStore
from memory.faiss_index import FAISSMemory
from memory.short_term import ShortTermMemory

log = logging.getLogger(__name__)


class GameSession:
    """All mutable runtime state for a single game session."""

    __slots__ = (
        "session_id",
        "created_at",
        "world",
        "graph",
        "store",
        "faiss_mem",
        "short_term",
        "active_npc_id",
        "data_dir",
        "lock",
        "ws_connections",
        "dialogue_history",
    )

    def __init__(
        self,
        session_id: str,
        world: Any,
        graph: Any,
        store: EventStore,
        faiss_mem: FAISSMemory,
        short_term: ShortTermMemory,
        active_npc_id: Optional[str],
        data_dir: Path,
        dialogue_history: Optional[list] = None,
    ):
        self.session_id = session_id
        self.created_at = time.time()
        self.world = world
        self.graph = graph
        self.store = store
        self.faiss_mem = faiss_mem
        self.short_term = short_term
        self.active_npc_id = active_npc_id
        self.data_dir = data_dir
        self.lock = asyncio.Lock()
        self.ws_connections: Set[Any] = set()
        self.dialogue_history: list = dialogue_history or []

    def close(self) -> None:
        """Persist and release session resources."""
        try:
            self.faiss_mem.save()
            self.store.close()
        except Exception as exc:
            log.error("Error closing session %s: %s", self.session_id, exc)
