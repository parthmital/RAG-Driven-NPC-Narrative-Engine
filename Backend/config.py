"""Central configuration for backend runtime tunables."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_csv(name: str, default: str) -> list[str]:
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]


def _env_choice(name: str, default: str, choices: set[str]) -> str:
    value = os.getenv(name, default).strip().lower()
    if value not in choices:
        raise ValueError(f"{name} must be one of {sorted(choices)}, got {value!r}")
    return value


# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Session filenames
EVENTS_DB_FILENAME = "events.db"
FAISS_INDEX_FILENAME = "faiss.index"
FAISS_META_FILENAME = "faiss_meta.json"
SNAPSHOT_FILENAME = "snapshot.json"
SNAPSHOT_AUTO_FILENAME = "snapshot_auto.json"
DIALOGUE_FILENAME = "dialogue.json"
DIALOGUE_AUTO_FILENAME = "dialogue_auto.json"

WORLD_SEED_PATH = BASE_DIR / "game" / "world_seed.json"
EMBED_CACHE_PATH = DATA_DIR / "embed_cache.db"

# Groq LLM
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MODEL_NAME = "openai/gpt-oss-120b"

TEMPERATURE = 0.35
MAX_GENERATION_TOKENS = 4096
REQUEST_TIMEOUT = 30
LLM_MAX_RETRIES = 3
LLM_RETRY_BACKOFF = 1.0

# Embedding
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L12-v2"
EMBEDDING_DIM = 384
EMBEDDING_WARMUP_TEXT = "warm up sentence"

# Memory
MAX_SHORT_TERM_TURNS = 8
TOP_K_RETRIEVAL = 6
FAISS_OVERFETCH_FACTOR = 5
SNAPSHOT_INTERVAL = 16
MEMORY_PRUNE_THRESHOLD = 1000
MEMORY_PRUNE_KEEP_RATIO = 0.5
RETRIEVAL_MIN_CANDIDATES = 3

# Truncation
DIALOGUE_EVENT_TRUNCATE_CHARS = 4096
MEMORY_FALLBACK_TRUNCATE_CHARS = 512

# Game logic
INITIAL_MORAL_ALIGNMENT = 50

# Prompt and context
MAX_CONTEXT_CHARS = 16384

# API server
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8080")
CORS_ORIGINS = _env_csv("CORS_ORIGINS", FRONTEND_URL)
DEBUG_ERRORS = _env_bool("DEBUG_ERRORS", False)
SESSION_SECRET = os.getenv("SESSION_SECRET", os.urandom(32).hex())
WS_HEARTBEAT_INTERVAL = 30
MAX_CONCURRENT_SESSIONS = 50

# Logging
LOG_LEVEL = _env_choice(
    "LOG_LEVEL", "info", {"debug", "info", "warning", "error"}
).upper()
LOG_FORMAT = _env_choice("LOG_FORMAT", "text", {"text", "json"})
