"""REST and WebSocket routes for the NPC Engine API."""

from fastapi import APIRouter

from api.routes import gameplay, sessions, websocket, world

router = APIRouter(prefix="/api/game", tags=["game"])
router.include_router(sessions.router)
router.include_router(gameplay.router)
router.include_router(world.router)

ws_router = websocket.router
