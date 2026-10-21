"""Recover the latest committed world state from a snapshot and the event log."""

from __future__ import annotations

import logging
from pathlib import Path

from core.event_store import EventStore
from core.reducer import rebuild_state, replay
from core.snapshot import load_snapshot
from schemas.world_state import WorldState

log = logging.getLogger(__name__)


def recover_state(
    seed: WorldState, store: EventStore, snapshot_path: Path
) -> WorldState:
    """Snapshot plus every event logged after it; a full replay when no usable snapshot exists.

    Equal to rebuild_state(seed, store.load_all()) by the replay property, but
    reads only the log suffix written after the snapshot.
    """
    snap = load_snapshot(snapshot_path)
    if snap is None:
        return rebuild_state(seed, store.load_all())
    state, last_event_id = snap
    if last_event_id > store.get_last_id():
        log.warning(
            "snapshot is ahead of the event log; replaying the log in full",
            extra={"path": str(snapshot_path), "last_event_id": last_event_id},
        )
        return rebuild_state(seed, store.load_all())
    return replay(state, store.load_after(last_event_id))
