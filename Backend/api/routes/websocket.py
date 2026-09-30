"""Real-time WebSocket channel for gameplay events."""

from __future__ import annotations

import json
import logging

from api.dependencies import get_session_manager
from api.realtime import broadcast, ws_message
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

log = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


async def _send(websocket: WebSocket, msg_type: str, payload: dict | None = None):
    await websocket.send_text(ws_message(msg_type, payload).model_dump_json())


@router.websocket("/ws/game/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    Real-time WebSocket for gameplay events.

    Incoming messages:
      - {"type": "action", "payload": {"content": "..."}}
      - {"type": "ping"}
    """
    sm = get_session_manager(websocket)
    session = sm.get_session(session_id)
    if not session:
        await websocket.close(code=4004, reason="Session not found")
        return

    await websocket.accept()
    session.ws_connections.add(websocket)
    log.info("WS connected: session=%s", session_id)

    try:
        active_npc_obj = session.world.npcs.get(session.active_npc_id)
        await _send(
            websocket,
            "connected",
            {
                "session_id": session_id,
                "turn": session.world.turn,
                "active_npc_id": session.active_npc_id,
                "active_npc_name": active_npc_obj.name if active_npc_obj else "",
                "location": session.world.player.current_location_id,
            },
        )
    except Exception as exc:
        log.error("WS init error: %s", exc)

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await _send(websocket, "error", {"message": "Invalid JSON"})
                continue

            msg_type = msg.get("type", "")
            payload = msg.get("payload", {})

            if msg_type == "ping":
                await _send(websocket, "pong")
                continue

            if msg_type != "action":
                continue

            content = payload.get("content", "").strip()
            if not content:
                continue

            try:
                result = await sm.process_action(session, content)
                await broadcast(session, ws_message("npc_response", result))
                await sm.save_session(session_id, is_auto=True)
            except Exception as exc:
                log.error("WS action error: %s", exc, exc_info=True)
                await _send(websocket, "error", {"message": "Game engine error"})

    except WebSocketDisconnect:
        log.info("WS disconnected: session=%s", session_id)
    except Exception as exc:
        log.error("WS error: %s", exc, exc_info=True)
    finally:
        session.ws_connections.discard(websocket)
