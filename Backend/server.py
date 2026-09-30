#!/usr/bin/env python3
"""NPC Engine API server entry point. Configuration comes from config.py."""

from __future__ import annotations

import logging
import sys

import config
from log_config import configure_logging


def main():
    configure_logging(config.LOG_LEVEL, config.LOG_FORMAT)
    try:
        import uvicorn
    except ImportError:
        logging.getLogger("server").error(
            "uvicorn is not installed; run npm run dev to set up the environment"
        )
        sys.exit(1)

    uvicorn.run(
        "api.app:create_app",
        factory=True,
        host=config.API_HOST,
        port=config.API_PORT,
        reload=False,
        log_config=None,
        access_log=False,
    )


if __name__ == "__main__":
    main()
