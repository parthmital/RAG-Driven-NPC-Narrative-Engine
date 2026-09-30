"""On-disk layout of session saves: snapshots and dialogue history."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

import config

log = logging.getLogger(__name__)

SAVE_TYPES = ("manual", "auto")


def sessions_dir() -> Path:
    return config.DATA_DIR / "sessions"


def session_dir(session_id: str) -> Path:
    return sessions_dir() / session_id


def split_save_id(save_id: str, default_type: str = "manual") -> tuple[str, str]:
    """Split "<session_id>:<save_type>" into its parts."""
    if ":" in save_id:
        session_id, save_type = save_id.split(":", 1)
        return session_id, save_type
    return save_id, default_type


def snapshot_path(data_dir: Path, is_auto: bool) -> Path:
    name = config.SNAPSHOT_AUTO_FILENAME if is_auto else config.SNAPSHOT_FILENAME
    return data_dir / name


def dialogue_path(data_dir: Path, is_auto: bool) -> Path:
    name = config.DIALOGUE_AUTO_FILENAME if is_auto else config.DIALOGUE_FILENAME
    return data_dir / name


def load_dialogue(path: Path) -> list:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        log.warning("corrupt dialogue file skipped", extra={"path": str(path)})
        return []


def save_dialogue(path: Path, history: list) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False)


def list_saves() -> List[Dict[str, Any]]:
    """Summaries of every snapshot on disk, newest first."""
    root = sessions_dir()
    if not root.exists():
        return []

    results = []
    for data_dir in root.iterdir():
        if not data_dir.is_dir():
            continue

        for save_type in SAVE_TYPES:
            path = snapshot_path(data_dir, is_auto=save_type == "auto")
            if not path.exists():
                continue

            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                world = data["world_state"]
                loc_id = world["player"]["current_location_id"]
                loc_name = world["locations"].get(loc_id, {}).get("name", loc_id)

                results.append(
                    {
                        "session_id": f"{data_dir.name}:{save_type}",
                        "player_name": world["player"]["name"],
                        "location_name": loc_name,
                        "turn": world["turn"],
                        "created_at": path.stat().st_mtime,
                        "is_auto": save_type == "auto",
                    }
                )
            except Exception:
                log.warning("corrupt snapshot skipped", extra={"path": str(path)})

    return sorted(results, key=lambda item: item["created_at"], reverse=True)
