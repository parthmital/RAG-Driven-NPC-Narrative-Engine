"""FastAPI dependencies shared by HTTP and WebSocket routes."""

from __future__ import annotations

from fastapi import Depends, HTTPException
from starlette.requests import HTTPConnection

from session.game_session import GameSession
from session.manager import SessionManager


def get_session_manager(connection: HTTPConnection) -> SessionManager:
    return connection.app.state.session_manager


def get_session(
    session_id: str, sm: SessionManager = Depends(get_session_manager)
) -> GameSession:
    session = sm.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    return session
