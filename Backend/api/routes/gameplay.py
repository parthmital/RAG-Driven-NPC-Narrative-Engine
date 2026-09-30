"""Player action and NPC conversation routes."""

from __future__ import annotations

import logging

from api.dependencies import get_session, get_session_manager
from api.presenters import build_npc_info
from api.realtime import broadcast, ws_message
from api.schemas import ActionResponse, NPCListResponse, PlayerActionRequest
from fastapi import APIRouter, Depends, HTTPException, Query
from llm import LLMError
from session.dialogue import turn_entries
from session.game_session import GameSession
from session.manager import SessionManager

log = logging.getLogger(__name__)

router = APIRouter()

BROADCAST_FIELDS = (
    "npc_dialogue",
    "narration",
    "npc_id",
    "npc_name",
    "turn",
    "trust_change",
    "events",
)


@router.post("/action/{session_id}", response_model=ActionResponse)
async def submit_action(
    req: PlayerActionRequest,
    session: GameSession = Depends(get_session),
    sm: SessionManager = Depends(get_session_manager),
):
    """Submit a player action and return the NPC response."""
    content = req.content.strip()

    try:
        result = await sm.process_action(session, content, req.npc_id)
    except Exception as exc:
        if isinstance(exc, LLMError):
            log.error("turn failed; llm unavailable", extra={"error": str(exc)})
        else:
            log.exception("turn failed")
        raise HTTPException(500, "Game engine error") from exc

    session.dialogue_history.extend(turn_entries(content, result))

    payload = {key: result[key] for key in BROADCAST_FIELDS}
    await broadcast(session, ws_message("npc_response", payload))
    await sm.save_session(session.session_id, is_auto=True)

    return ActionResponse(**result)


@router.get("/npcs/{session_id}", response_model=NPCListResponse)
async def list_npcs(
    location_only: bool = Query(True), session: GameSession = Depends(get_session)
):
    """List NPCs for the session."""
    world = session.world
    npcs = [
        build_npc_info(session, npc)
        for npc in world.npcs.values()
        if npc.alive
        and (not location_only or npc.location_id == world.player.current_location_id)
    ]
    return NPCListResponse(npcs=npcs, active_npc_id=session.active_npc_id)


@router.post("/npc/{session_id}/{npc_id}")
async def switch_npc(npc_id: str, session: GameSession = Depends(get_session)):
    """Switch the active NPC for a session."""
    world = session.world
    if npc_id not in world.npcs:
        raise HTTPException(404, f"NPC '{npc_id}' not found")

    npc = world.npcs[npc_id]
    if npc.location_id != world.player.current_location_id:
        raise HTTPException(400, f"{npc.name} is not in this location")

    if not npc.alive:
        raise HTTPException(400, f"{npc.name} is no longer available")

    session.active_npc_id = npc_id
    npc_info = build_npc_info(session, npc).model_dump()
    await broadcast(session, ws_message("npc_switched", npc_info))

    return {"status": "switched", "npc": npc_info}
