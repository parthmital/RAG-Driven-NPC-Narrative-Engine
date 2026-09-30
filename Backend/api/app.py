"""FastAPI application factory."""

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager

import config
from api.routes import router as game_router, ws_router
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from session.manager import SessionManager

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    log.info("NPC Engine API starting...")
    session_manager: SessionManager = app.state.session_manager

    try:
        await session_manager.initialise()
        log.info("Shared resources preloaded successfully.")
    except Exception as exc:
        log.error("Preloading failed during startup: %s", exc, exc_info=True)

    yield

    log.info("NPC Engine API shutting down...")
    await session_manager.shutdown()


def create_app() -> FastAPI:
    app = FastAPI(
        title="NPC Engine API",
        description="Real-time game engine API for the LLM-driven NPC dialogue system.",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.state.session_manager = SessionManager()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        started_at = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        log.info(
            "%s %s -> %d (%.0fms)",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )
        return response

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        log.error("Unhandled error on %s: %s", request.url.path, exc, exc_info=True)
        content = {"error": "Internal server error"}
        if config.DEBUG_ERRORS:
            content["detail"] = str(exc)
        return JSONResponse(status_code=500, content=content)

    app.include_router(game_router)
    app.include_router(ws_router)

    @app.get("/health")
    async def root_health():
        return {"status": "ok", "ready": app.state.session_manager.is_ready}

    return app
