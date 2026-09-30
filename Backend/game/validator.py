"""Validate LLM proposed world updates against canonical state."""

from __future__ import annotations

import logging
from typing import List, Tuple

from schemas.events import Event, EventType
from schemas.llm_output import LLMOutput, WorldUpdateProposal
from schemas.world_state import WorldState

log = logging.getLogger(__name__)

ALLOWED_EVENT_TYPES = {event_type.value for event_type in EventType}


def validate_and_build_events(
    output: LLMOutput,
    world: WorldState,
    turn: int,
) -> Tuple[List[Event], List[str]]:
    """
    Return valid events and validation errors.

    Illegal proposals are dropped; errors are reported without halting the turn.
    """
    valid: List[Event] = []
    errors: List[str] = []

    if output.new_entities:
        log.warning("entity creation blocked", extra={"entities": output.new_entities})
        errors.append(f"LLM attempted entity creation - blocked: {output.new_entities}")

    for proposal in output.world_updates:
        err = _validate_proposal(proposal, world)
        if err:
            log.warning(
                "world update rejected", extra={"type": proposal.type, "reason": err}
            )
            errors.append(f"Rejected {proposal.type}: {err}")
            continue

        try:
            event_type = EventType(proposal.type)
        except ValueError:
            errors.append(f"Unknown event type: {proposal.type}")
            continue

        valid.append(Event(turn=turn, event_type=event_type, payload=proposal.payload))

    return valid, errors


def _validate_proposal(proposal: WorldUpdateProposal, world: WorldState) -> str:
    """Return an error string, or an empty string when the proposal is valid."""
    update_type = proposal.type
    payload = proposal.payload

    if update_type not in ALLOWED_EVENT_TYPES:
        return "unknown type"

    if update_type == "PLAYER_MOVED":
        dest = payload.get("to_location_id")
        if dest not in world.locations:
            return f"destination '{dest}' not in canonical locations"
        src = world.player.current_location_id
        if dest not in world.locations[src].connected_to:
            return f"'{dest}' not connected to current location '{src}'"

    elif update_type == "RELATIONSHIP_CHANGED":
        npc_id = payload.get("npc_id")
        if npc_id not in world.npcs:
            return f"npc_id '{npc_id}' not canonical"
        delta = payload.get("delta", 0)
        if not isinstance(delta, (int, float)) or abs(delta) > 20:
            return f"delta {delta} out of range (max +/-20 per turn)"

    elif update_type == "OBJECT_TAKEN":
        obj_id = payload.get("object_id")
        if obj_id not in world.objects:
            return f"object_id '{obj_id}' not canonical"
        obj = world.objects[obj_id]
        if obj.location_id != world.player.current_location_id:
            return f"object '{obj_id}' not in current location"

    elif update_type == "OBJECT_DROPPED":
        obj_id = payload.get("object_id")
        if obj_id not in world.objects:
            return f"object_id '{obj_id}' not canonical"
        if (
            payload.get("dropped_by") == "player"
            and obj_id not in world.player.inventory
        ):
            return f"player does not carry '{obj_id}'"
        loc_id = payload.get("location_id")
        if loc_id not in world.locations:
            return f"location '{loc_id}' not canonical"

    elif update_type == "LOCATION_STATE_CHANGED":
        if payload.get("location_id") not in world.locations:
            return f"location '{payload.get('location_id')}' not canonical"

    elif update_type == "NPC_STATE_CHANGED":
        npc_id = payload.get("npc_id")
        if npc_id not in world.npcs:
            return f"npc_id '{npc_id}' not canonical"
        if not payload.get("key"):
            return "missing key"

    elif update_type == "PLAYER_FLAG_SET":
        if not payload.get("key"):
            return "missing key"

    elif update_type == "JOURNAL_ENTRY_CREATED":
        if not payload.get("content"):
            return "missing content"

    elif update_type == "CURRENCY_CHANGED":
        delta = payload.get("delta")
        if not isinstance(delta, (int, float)):
            return "delta must be a number"
        if delta < 0 and abs(delta) > world.player.currency:
            return "player does not have enough currency"

    return ""
