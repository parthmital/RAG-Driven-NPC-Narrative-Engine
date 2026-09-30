"""Process-wide logging: one format, request and session context, quiet dependencies.

Modules log with the standard library and pass structured fields through
``extra``::

    log.info("session created", extra={"session": sid, "player": name})

``LOG_FORMAT=text`` (default) renders ``time LEVEL logger message key=value``.
``LOG_FORMAT=json`` renders one JSON object per line for log shippers.
"""

from __future__ import annotations

import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime, timezone
from enum import Enum

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
session_id_var: ContextVar[str | None] = ContextVar("session_id", default=None)

# Dependencies that log routine progress at INFO; only their warnings matter here.
QUIET_LOGGERS = (
    "uvicorn",
    "uvicorn.error",
    "httpx",
    "httpcore",
    "groq",
    "sentence_transformers",
    "transformers",
    "huggingface_hub",
    "faiss",
    "urllib3",
    "langgraph",
)

_RECORD_ATTRS = set(vars(logging.makeLogRecord({}))) | {
    "message",
    "asctime",
    "color_message",
    "taskName",
}


def _context(record: logging.LogRecord) -> dict:
    """Structured fields: ``extra`` values, then request and session context."""
    fields = {
        key: value.value if isinstance(value, Enum) else value
        for key, value in vars(record).items()
        if key not in _RECORD_ATTRS and not key.startswith("_")
    }
    request_id = request_id_var.get()
    session_id = session_id_var.get()
    if request_id:
        fields.setdefault("req", request_id)
    if session_id:
        fields.setdefault("session", session_id)
    return fields


def _logfmt_value(value) -> str:
    text = value if isinstance(value, str) else json.dumps(value, default=str)
    if not text or any(char in text for char in ' ="'):
        return json.dumps(text)
    return text


class TextFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S.%f")[:-3]
        line = (
            f"{timestamp} {record.levelname:<7} {record.name:<20} "
            f"{record.getMessage()}"
        )
        fields = _context(record)
        if fields:
            line += "  " + " ".join(
                f"{key}={_logfmt_value(value)}" for key, value in fields.items()
            )
        if record.exc_info:
            line += "\n" + self.formatException(record.exc_info)
        return line


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "ts": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            **_context(record),
        }
        if record.exc_info:
            entry["exc"] = self.formatException(record.exc_info)
        return json.dumps(entry, default=str)


# Warnings raised inside dependencies that this code cannot act on.
# langchain installs its own warning filters, so a logging filter is the reliable place.
KNOWN_DEPENDENCY_WARNINGS = ("The default value of `allowed_objects`",)


def _drop_known_dependency_warnings(record: logging.LogRecord) -> bool:
    message = record.getMessage()
    return not any(known in message for known in KNOWN_DEPENDENCY_WARNINGS)


def configure_logging(level: str, fmt: str) -> None:
    """Install the single root handler. Call once, before importing the app."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter() if fmt == "json" else TextFormatter())

    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level)

    for name in QUIET_LOGGERS:
        logger = logging.getLogger(name)
        logger.handlers.clear()
        logger.propagate = True
        logger.setLevel(max(logging.WARNING, root.level))

    logging.captureWarnings(True)
    logging.getLogger("py.warnings").addFilter(_drop_known_dependency_warnings)
