"""Display dialogue history entries shown by the client."""

from __future__ import annotations

import time
from typing import Any, Dict, List


def _now_ms() -> float:
    return time.time() * 1000


def narration_entry(entry_id: str, content: str) -> Dict[str, Any]:
    return {
        "id": entry_id,
        "type": "narration",
        "speaker": "Narrator",
        "content": content,
        "timestamp": _now_ms(),
    }


def turn_entries(player_input: str, result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """History entries for one player action and its processed result."""
    base_id = int(_now_ms())
    narration = result["narration"]
    dialogue = result["npc_dialogue"]
    entries: List[Dict[str, Any]] = [
        {
            "id": str(base_id),
            "type": "player",
            "content": player_input,
            "timestamp": _now_ms(),
        }
    ]

    if result["npc_id"] == "narrator":
        merged = (
            f"{narration}\n\n{dialogue}"
            if narration and dialogue
            else narration or dialogue
        )
        if merged:
            entries.append(narration_entry(str(base_id + 1), merged))
        return entries

    if narration:
        entries.append(narration_entry(str(base_id + 1), narration))
    if dialogue:
        entries.append(
            {
                "id": str(base_id + 2),
                "type": "npc",
                "speaker": result["npc_name"],
                "content": dialogue,
                "timestamp": _now_ms() + 1,
                "trustChange": result.get("trust_change"),
            }
        )
    return entries
