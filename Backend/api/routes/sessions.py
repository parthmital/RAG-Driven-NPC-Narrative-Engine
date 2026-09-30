"""Session lifecycle, game metadata, and health routes."""

from __future__ import annotations

import logging
from typing import List

import config
from api.dependencies import get_session, get_session_manager
from api.presenters import build_game_state_response, build_session_info
from api.schemas import (
    CreateSessionRequest,
    GameMetadataResponse,
    GameStateResponse,
    HealthResponse,
    SaveInfo,
    SessionInfo,
)
from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from game.world_loader import load_world_seed
from session.game_session import GameSession
from session.manager import SessionManager

log = logging.getLogger(__name__)

router = APIRouter()


@router.get("/metadata", response_model=GameMetadataResponse)
async def get_metadata():
    """Retrieve top-level game metadata from the seed file."""
    try:
        return load_world_seed(config.WORLD_SEED_PATH).metadata
    except Exception:
        log.exception("world metadata unavailable")
    return GameMetadataResponse()


@router.post("/session", response_model=SessionInfo)
async def create_session(
    req: CreateSessionRequest, sm: SessionManager = Depends(get_session_manager)
):
    """Create a new game session."""
    try:
        session = await sm.create_session(
            name=req.name,
            gender=req.gender,
            age=req.age,
            occupation=req.occupation,
            reset=req.reset,
        )
    except RuntimeError as exc:
        raise HTTPException(429, str(exc)) from exc
    return build_session_info(session)


@router.get("/sessions", response_model=List[SaveInfo])
async def list_sessions(sm: SessionManager = Depends(get_session_manager)):
    """List all saved game sessions."""
    return [SaveInfo(**save) for save in await sm.list_sessions()]


@router.post("/load/{session_id}", response_model=SessionInfo)
async def load_session(
    session_id: str, sm: SessionManager = Depends(get_session_manager)
):
    """Load a specific session."""
    session = await sm.load_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found or corrupt")
    return build_session_info(session)


@router.post("/save/{session_id}")
async def save_game(session_id: str, sm: SessionManager = Depends(get_session_manager)):
    """Manually save game state."""
    if not await sm.save_session(session_id, is_auto=False):
        raise HTTPException(404, "Session not found")
    return {"status": "saved"}


@router.delete("/session/{session_id}")
async def destroy_session(
    session_id: str, sm: SessionManager = Depends(get_session_manager)
):
    """End and clean up a session."""
    if not sm.destroy_session(session_id):
        raise HTTPException(404, "Session not found")
    return {"status": "destroyed", "session_id": session_id}


@router.get("/state/{session_id}", response_model=GameStateResponse)
async def get_game_state(session: GameSession = Depends(get_session)):
    """Retrieve full game state for a session."""
    return build_game_state_response(session)


@router.get("/health", response_model=HealthResponse)
async def health_check(sm: SessionManager = Depends(get_session_manager)):
    llm_ok = False
    try:
        llm_ok = await run_in_threadpool(sm.ping_llm)
    except Exception:
        log.warning("llm health check failed", exc_info=True)
    return HealthResponse(
        status="ok",
        llm_reachable=llm_ok,
        active_sessions=sm.active_session_count,
        ready=sm.is_ready,
    )
