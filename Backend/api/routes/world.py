"""Location, movement, clue, and inventory routes."""

from __future__ import annotations

from typing import Any, Dict, List

from api.dependencies import get_session, get_session_manager
from api.presenters import build_game_state_response, build_location_info
from api.schemas import GameStateResponse, LinkCluesRequest, LocationInfo, MoveRequest
from fastapi import APIRouter, Depends, HTTPException
from schemas.events import Event, EventType
from session.game_session import GameSession
from session.manager import SessionManager

router = APIRouter()


def _location_name(world: Any, location_id: str) -> str:
    location = world.locations.get(location_id)
    return location.name if location else location_id.replace("_", " ").title()


async def _commit(
    sm: SessionManager,
    session: GameSession,
    event_type: EventType,
    payload: Dict[str, Any],
    advance_turn: bool = False,
) -> GameStateResponse:
    turn = session.world.turn + 1 if advance_turn else session.world.turn
    event = Event(turn=turn, event_type=event_type, payload=payload)
    await sm.commit_event(session, event, advance_turn=advance_turn)
    return build_game_state_response(session)


@router.get("/location/{session_id}", response_model=LocationInfo)
async def get_location(session: GameSession = Depends(get_session)):
    """Get current location data."""
    loc_info = build_location_info(session)
    if not loc_info:
        raise HTTPException(404, "Location not found")
    return loc_info


@router.get("/locations/{session_id}", response_model=List[LocationInfo])
async def list_locations(session: GameSession = Depends(get_session)):
    """List all locations in the world."""
    return [
        loc_info
        for loc in session.world.locations.values()
        if (loc_info := build_location_info(session, loc.id)) is not None
    ]


@router.post("/move/{session_id}", response_model=GameStateResponse)
async def move_player(
    req: MoveRequest,
    session: GameSession = Depends(get_session),
    sm: SessionManager = Depends(get_session_manager),
):
    """Directly move the player to a connected location."""
    world = session.world
    current_loc_id = world.player.current_location_id
    current_loc = world.locations.get(current_loc_id)

    if not current_loc or req.location_id not in current_loc.connected_to:
        raise HTTPException(
            400,
            f"Cannot travel to {_location_name(world, req.location_id)} "
            f"from {_location_name(world, current_loc_id)}",
        )

    return await _commit(
        sm,
        session,
        EventType.PLAYER_MOVED,
        {"to_location_id": req.location_id},
        advance_turn=True,
    )


@router.post("/clue/link/{session_id}", response_model=GameStateResponse)
async def link_clues(
    req: LinkCluesRequest,
    session: GameSession = Depends(get_session),
    sm: SessionManager = Depends(get_session_manager),
):
    """Link two clues logically in the player's journal."""
    if req.id1 not in session.world.clues or req.id2 not in session.world.clues:
        raise HTTPException(400, "One or both clues not found")

    return await _commit(
        sm, session, EventType.CLUE_LINKED, {"id1": req.id1, "id2": req.id2}
    )


@router.post("/pickup/{session_id}/{object_id}", response_model=GameStateResponse)
async def pickup_object(
    object_id: str,
    session: GameSession = Depends(get_session),
    sm: SessionManager = Depends(get_session_manager),
):
    """Pick up an object from the current location into inventory."""
    world = session.world
    if object_id not in world.objects:
        raise HTTPException(404, f"Object '{object_id}' not found")

    obj = world.objects[object_id]
    if obj.location_id != world.player.current_location_id:
        raise HTTPException(400, f"{obj.name} is not in this location")

    if object_id in world.player.inventory:
        raise HTTPException(400, f"You already have {obj.name}")

    return await _commit(
        sm,
        session,
        EventType.OBJECT_TAKEN,
        {"object_id": object_id, "taken_by": "player"},
    )


@router.post("/drop/{session_id}/{object_id}", response_model=GameStateResponse)
async def drop_object(
    object_id: str,
    session: GameSession = Depends(get_session),
    sm: SessionManager = Depends(get_session_manager),
):
    """Drop an object from inventory at current location."""
    world = session.world
    if object_id not in world.player.inventory:
        raise HTTPException(400, "Object not in inventory")

    return await _commit(
        sm,
        session,
        EventType.OBJECT_DROPPED,
        {
            "object_id": object_id,
            "dropped_by": "player",
            "location_id": world.player.current_location_id,
        },
    )
