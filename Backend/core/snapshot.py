"""Snapshot cache — persists WorldState to avoid full replay on startup."""

from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Optional, Tuple

from schemas.world_state import WorldState

log = logging.getLogger(__name__)


def save_snapshot(state: WorldState, path: Path, last_event_id: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "last_event_id": last_event_id,
        "world_state": state.model_dump(),
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    log.debug(
        "snapshot saved", extra={"turn": state.turn, "last_event_id": last_event_id}
    )


def load_snapshot(path: Path) -> Optional[Tuple[WorldState, int]]:
    """Returns (WorldState, last_event_id) or None if not found / invalid."""
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        state = WorldState(**data["world_state"])
        last_event_id = int(data["last_event_id"])
        log.debug(
            "snapshot loaded",
            extra={"turn": state.turn, "last_event_id": last_event_id},
        )
        return state, last_event_id
    except Exception as exc:
        log.warning(
            "corrupt snapshot ignored", extra={"path": str(path), "error": str(exc)}
        )
        return None
