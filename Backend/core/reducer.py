"""Deterministic event reducer for WorldState."""

from __future__ import annotations

import logging
from typing import List

from schemas.events import Event, EventType
from schemas.world_state import Clue, JournalEntry, WorldState

log = logging.getLogger(__name__)


def apply_event(state: WorldState, event: Event) -> WorldState:
    """Return a new WorldState after applying one event."""
    next_state = state.model_copy(deep=True)
    payload = event.payload
    event_type = event.event_type

    try:
        if event_type == EventType.SESSION_START:
            pass

        elif event_type == EventType.PLAYER_MOVED:
            destination = payload.get("to_location_id")
            if destination and destination in next_state.locations:
                next_state.player.current_location_id = destination
                next_state.turn = event.turn
            else:
                log.warning(
                    "move to unknown location ignored",
                    extra={"location": destination},
                )

        elif event_type == EventType.RELATIONSHIP_CHANGED:
            npc_id = payload.get("npc_id")
            target_id = payload.get("target_id", "player")
            delta = int(payload.get("delta", 0))
            if npc_id and npc_id in next_state.npcs:
                rel = next_state.relationships.setdefault(npc_id, {})
                current = rel.get(target_id, 0)
                rel[target_id] = max(-100, min(100, current + delta))

        elif event_type == EventType.OBJECT_TAKEN:
            obj_id = payload.get("object_id")
            taken_by = payload.get("taken_by", "player")
            if obj_id and obj_id in next_state.objects:
                obj = next_state.objects[obj_id]
                obj.location_id = None
                if taken_by == "player":
                    if obj_id not in next_state.player.inventory:
                        next_state.player.inventory.append(obj_id)
                else:
                    obj.owner_id = taken_by

        elif event_type == EventType.OBJECT_DROPPED:
            obj_id = payload.get("object_id")
            loc_id = payload.get("location_id")
            dropped_by = payload.get("dropped_by", "player")
            if (
                obj_id
                and obj_id in next_state.objects
                and loc_id in next_state.locations
            ):
                obj = next_state.objects[obj_id]
                obj.location_id = loc_id
                obj.owner_id = None
                if dropped_by == "player" and obj_id in next_state.player.inventory:
                    next_state.player.inventory.remove(obj_id)

        elif event_type == EventType.LOCATION_STATE_CHANGED:
            loc_id = payload.get("location_id")
            key = payload.get("key")
            value = payload.get("value")
            if loc_id and loc_id in next_state.locations and key:
                next_state.locations[loc_id].state[key] = value

        elif event_type == EventType.NPC_STATE_CHANGED:
            npc_id = payload.get("npc_id")
            key = payload.get("key")
            value = payload.get("value")
            if npc_id and npc_id in next_state.npcs and key:
                npc = next_state.npcs[npc_id]
                if key == "alive":
                    npc.alive = bool(value)
                elif key == "location_id" and str(value) in next_state.locations:
                    npc.location_id = str(value)
                else:
                    npc.state[key] = value

        elif event_type == EventType.PLAYER_FLAG_SET:
            key = payload.get("key")
            if key:
                next_state.player.flags[key] = payload.get("value")

        elif event_type == EventType.NPC_SPOKE:
            pass

        elif event_type == EventType.JOURNAL_ENTRY_CREATED:
            entry = JournalEntry(
                id=str(event.id or f"je_{int(event.timestamp)}"),
                turn=event.turn,
                content=payload.get("content", ""),
                timestamp=event.timestamp,
            )
            next_state.journal.append(entry)

        elif event_type == EventType.CLUE_DISCOVERED:
            clue_id = payload.get("clue_id")
            if clue_id:
                if clue_id in next_state.clues:
                    next_state.clues[clue_id].discovered = True
                else:
                    next_state.clues[clue_id] = Clue(
                        id=clue_id,
                        title=payload.get("title", clue_id.replace("_", " ").title()),
                        description=payload.get("description", ""),
                        discovered=True,
                    )

        elif event_type == EventType.CLUE_LINKED:
            id1 = payload.get("id1")
            id2 = payload.get("id2")
            if id1 in next_state.clues and id2 in next_state.clues:
                if id2 not in next_state.clues[id1].linked_clues:
                    next_state.clues[id1].linked_clues.append(id2)
                if id1 not in next_state.clues[id2].linked_clues:
                    next_state.clues[id2].linked_clues.append(id1)

        elif event_type == EventType.CURRENCY_CHANGED:
            delta = int(payload.get("delta", 0))
            next_state.player.currency = max(0, next_state.player.currency + delta)

        else:
            log.warning("unhandled event type", extra={"type": event_type})

    except Exception:
        log.exception(
            "event could not be applied; state unchanged",
            extra={"event_id": event.id, "type": event_type},
        )

    return next_state


def rebuild_state(seed: WorldState, events: List[Event]) -> WorldState:
    """Replay all events from seed to current state."""
    state = seed.model_copy(deep=True)
    for event in events:
        state = apply_event(state, event)
    if events:
        state.turn = max(event.turn for event in events)
    return state
