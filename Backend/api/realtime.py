"""WebSocket message construction and fan-out."""

from __future__ import annotations

import time
from typing import Any, Dict

from api.schemas import WSOutMessage
from session.game_session import GameSession


def ws_message(msg_type: str, payload: Dict[str, Any] | None = None) -> WSOutMessage:
    return WSOutMessage(type=msg_type, payload=payload or {}, timestamp=time.time())


async def broadcast(session: GameSession, msg: WSOutMessage) -> None:
    """Send a message to all WebSocket connections for a session."""
    dead = set()
    data = msg.model_dump_json()
    for ws in session.ws_connections:
        try:
            await ws.send_text(data)
        except Exception:
            dead.add(ws)
    session.ws_connections -= dead
