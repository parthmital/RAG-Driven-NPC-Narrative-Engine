"""Validate LLM proposed world updates against canonical state.

Proposals are checked in order against the state the accepted ones produce, so
limits that span a turn hold for the turn as a whole: one move, the trust step
per NPC, total spending against the opening balance, and the currency-gain cap.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import config
from core.reducer import apply_event
from schemas.events import Event, EventType
from schemas.llm_output import LLMOutput, WorldUpdateProposal
from schemas.world_state import WorldState

log = logging.getLogger(__name__)

ALLOWED_EVENT_TYPES = {event_type.value for event_type in EventType}
# Written by the engine itself, never proposed by the model
SYSTEM_ONLY_EVENT_TYPES = {
    EventType.SESSION_START.value,
    EventType.SESSION_END.value,
    EventType.NPC_SPOKE.value,
}


@dataclass
class TurnLedger:
    """What the turn's accepted proposals have done so far."""

    start: WorldState
    state: WorldState
    moved: bool = False
    spent: int = 0
    trust: Dict[Tuple[str, str], int] = field(default_factory=dict)

    @classmethod
    def open(cls, world: WorldState) -> "TurnLedger":
        return cls(start=world, state=world)

    def accept(self, proposal: WorldUpdateProposal, event: Event) -> None:
        payload = proposal.payload
        if proposal.type == "PLAYER_MOVED":
            self.moved = True
        elif proposal.type == "RELATIONSHIP_CHANGED":
            key = (payload["npc_id"], payload.get("target_id", "player"))
            self.trust[key] = self.trust.get(key, 0) + int(payload["delta"])
        elif proposal.type == "CURRENCY_CHANGED" and payload["delta"] < 0:
            self.spent += -int(payload["delta"])
        self.state = apply_event(self.state, event)


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

    ledger = TurnLedger.open(world)
    for proposal in output.world_updates:
        err = _validate_proposal(proposal, world, ledger)
        if err:
            log.warning(
                "world update rejected", extra={"type": proposal.type, "reason": err}
            )
            errors.append(f"Rejected {proposal.type}: {err}")
            continue

        event = Event(
            turn=turn, event_type=EventType(proposal.type), payload=proposal.payload
        )
        ledger.accept(proposal, event)
        valid.append(event)

    return valid, errors


def _is_int(value) -> bool:
    """An integral number that is not a bool (JSON true would pass isinstance int)."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return float(value).is_integer()


def _validate_proposal(
    proposal: WorldUpdateProposal,
    world: WorldState,
    ledger: Optional[TurnLedger] = None,
) -> str:
    """Return an error string, or an empty string when the proposal is valid.

    Without a ledger the proposal is judged as the only one in its turn.
    """
    ledger = ledger or TurnLedger.open(world)
    state = ledger.state
    update_type = proposal.type
    payload = proposal.payload
    here = state.player.current_location_id

    if update_type not in ALLOWED_EVENT_TYPES:
        return "unknown type"
    if update_type in SYSTEM_ONLY_EVENT_TYPES:
        return "event type is written by the engine, not proposed"

    if update_type == "PLAYER_MOVED":
        dest = payload.get("to_location_id")
        if not isinstance(dest, str) or dest not in state.locations:
            return f"destination '{dest}' not in canonical locations"
        if ledger.moved:
            return "the player can move only once per turn"
        if dest not in state.locations[here].connected_to:
            return f"'{dest}' not connected to current location '{here}'"

    elif update_type == "RELATIONSHIP_CHANGED":
        npc_id = payload.get("npc_id")
        if npc_id not in state.npcs:
            return f"npc_id '{npc_id}' not canonical"
        target = payload.get("target_id", "player")
        if target != "player" and target not in state.npcs:
            return f"target_id '{target}' not canonical"
        delta = payload.get("delta")
        if not _is_int(delta):
            return "delta must be an integer"
        limit = config.MAX_TRUST_DELTA_PER_TURN
        total = ledger.trust.get((npc_id, target), 0) + int(delta)
        if abs(total) > limit:
            return f"trust change {total} this turn out of range (max +/-{limit})"

    elif update_type == "OBJECT_TAKEN":
        obj_id = payload.get("object_id")
        if obj_id not in state.objects:
            return f"object_id '{obj_id}' not canonical"
        taker = payload.get("taken_by", "player")
        if taker != "player" and taker not in state.npcs:
            return f"taken_by '{taker}' not canonical"
        if ledger.moved:
            return "objects can only change hands before the player moves"
        obj = state.objects[obj_id]
        if obj_id in state.player.inventory:
            return f"player already carries '{obj_id}'"
        if taker != "player" and state.npcs[taker].location_id != here:
            return f"'{taker}' is not at the player's location"
        held_here = (
            obj.location_id is None
            and obj.owner_id in state.npcs
            and obj.owner_id != taker
            and state.npcs[obj.owner_id].location_id == here
        )
        if obj.location_id != here and not held_here:
            return f"object '{obj_id}' not in current location"

    elif update_type == "OBJECT_DROPPED":
        obj_id = payload.get("object_id")
        if obj_id not in state.objects:
            return f"object_id '{obj_id}' not canonical"
        loc_id = payload.get("location_id")
        if loc_id not in state.locations:
            return f"location '{loc_id}' not canonical"
        if loc_id != here or ledger.moved:
            return "objects can only be dropped where the player started the turn"
        dropper = payload.get("dropped_by", "player")
        obj = state.objects[obj_id]
        if dropper == "player":
            if obj_id not in state.player.inventory:
                return f"player does not carry '{obj_id}'"
        elif dropper not in state.npcs:
            return f"dropped_by '{dropper}' not canonical"
        elif obj.owner_id != dropper or obj.location_id is not None:
            return f"'{dropper}' does not hold '{obj_id}'"
        elif state.npcs[dropper].location_id != here:
            return f"'{dropper}' is not at the player's location"

    elif update_type == "LOCATION_STATE_CHANGED":
        if payload.get("location_id") not in state.locations:
            return f"location '{payload.get('location_id')}' not canonical"
        if not payload.get("key"):
            return "missing key"

    elif update_type == "NPC_STATE_CHANGED":
        npc_id = payload.get("npc_id")
        if npc_id not in state.npcs:
            return f"npc_id '{npc_id}' not canonical"
        key, value = payload.get("key"), payload.get("value")
        if not key:
            return "missing key"
        if key == "alive" and not isinstance(value, bool):
            return "alive must be true or false"
        if key == "location_id":
            src = state.npcs[npc_id].location_id
            if value not in state.locations:
                return f"location '{value}' not canonical"
            if value != src and not (
                value in state.locations[src].connected_to
                or src in state.locations[value].connected_to
            ):
                return f"NPCs move one connection at a time ('{src}' to '{value}')"

    elif update_type == "PLAYER_FLAG_SET":
        if not payload.get("key"):
            return "missing key"

    elif update_type == "JOURNAL_ENTRY_CREATED":
        if not payload.get("content"):
            return "missing content"

    elif update_type == "CLUE_DISCOVERED":
        if not payload.get("clue_id"):
            return "missing clue_id"

    elif update_type == "CLUE_LINKED":
        if (
            payload.get("id1") not in state.clues
            or payload.get("id2") not in state.clues
        ):
            return "both clues must exist"

    elif update_type == "CURRENCY_CHANGED":
        delta = payload.get("delta")
        if not _is_int(delta):
            return "delta must be an integer"
        delta = int(delta)
        if delta < 0 and (
            -delta > state.player.currency
            or ledger.spent - delta > ledger.start.player.currency
        ):
            return "player does not have enough currency"
        gain = state.player.currency + delta - ledger.start.player.currency
        if delta > 0 and gain > config.MAX_CURRENCY_GAIN_PER_TURN:
            return (
                f"currency gain {gain} this turn exceeds the cap of "
                f"{config.MAX_CURRENCY_GAIN_PER_TURN}"
            )

    return ""
