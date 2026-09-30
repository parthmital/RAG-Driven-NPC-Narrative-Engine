"""FastAPI dependencies shared by HTTP and WebSocket routes."""

from __future__ import annotations

from fastapi import Depends, HTTPException
from log_config import session_id_var
from starlette.requests import HTTPConnection

from session.game_session import GameSession
from session.manager import SessionManager


def get_session_manager(connection: HTTPConnection) -> SessionManager:
    return connection.app.state.session_manager


async def get_session(
    session_id: str, sm: SessionManager = Depends(get_session_manager)
) -> GameSession:
    session = sm.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    # Async so the binding reaches the route; request middleware scopes it.
    session_id_var.set(session.session_id)
    return session
