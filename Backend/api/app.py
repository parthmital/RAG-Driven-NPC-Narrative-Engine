"""FastAPI application factory."""

from __future__ import annotations

import logging
import time
import uuid
from contextlib import asynccontextmanager

import config
from api.routes import router as game_router, ws_router
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from log_config import request_id_var
from session.manager import SessionManager

log = logging.getLogger(__name__)
http_log = logging.getLogger("api.http")

REQUEST_ID_HEADER = "X-Request-ID"
# Polled by the launcher and browsers; logged only at DEBUG.
QUIET_PATHS = {"/health"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    started_at = time.perf_counter()
    log.info(
        "starting",
        extra={
            "host": config.API_HOST,
            "port": config.API_PORT,
            "cors": ",".join(config.CORS_ORIGINS),
        },
    )
    if not config.GROQ_API_KEY:
        log.warning("GROQ_API_KEY is not set; NPC replies will fail")

    session_manager: SessionManager = app.state.session_manager
    try:
        await session_manager.initialise()
        log.info(
            "ready",
            extra={
                "url": f"http://localhost:{config.API_PORT}",
                "startup_ms": round((time.perf_counter() - started_at) * 1000),
            },
        )
    except Exception:
        log.exception("startup failed; /health will report ready=false")

    yield

    log.info("shutting down")
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
        expose_headers=[REQUEST_ID_HEADER],
    )

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        request_id = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex[:8]
        token = request_id_var.set(request_id[:64])
        started_at = time.perf_counter()
        try:
            try:
                response = await call_next(request)
            except Exception as exc:
                log.exception("unhandled error", extra={"path": request.url.path})
                content = {"error": "Internal server error"}
                if config.DEBUG_ERRORS:
                    content["detail"] = str(exc)
                response = JSONResponse(status_code=500, content=content)

            response.headers[REQUEST_ID_HEADER] = request_id_var.get()
            quiet = request.method == "OPTIONS" or request.url.path in QUIET_PATHS
            http_log.log(
                logging.DEBUG if quiet else logging.INFO,
                "%s %s",
                request.method,
                request.url.path,
                extra={
                    "status": response.status_code,
                    "ms": round((time.perf_counter() - started_at) * 1000),
                },
            )
            return response
        finally:
            request_id_var.reset(token)

    app.include_router(game_router)
    app.include_router(ws_router)

    @app.get("/health")
    async def root_health():
        return {"status": "ok", "ready": app.state.session_manager.is_ready}

    return app
