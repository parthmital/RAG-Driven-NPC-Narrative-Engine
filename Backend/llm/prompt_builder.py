"""Assembles the single unified prompt per turn."""

from __future__ import annotations
import json
from typing import List, Optional, Sequence, Tuple

import config
from schemas.events import Event
from schemas.world_state import WorldState
from memory.faiss_index import MemoryEntry
from memory.short_term import TurnRecord, format_turns

# ── Template ───────────────────────────────────────────────────────────────

SYSTEM_BLOCK = """You are the narrator and NPC voice engine for a text adventure game.
You control ONE NPC per turn. You must respond with a single valid JSON object — no markdown, no prose outside the JSON.

OUTPUT SCHEMA (strict):
{{
  "world_updates": [
    {{"type": "<EventType>", "payload": {{...}}}}
  ],
  "memory_summary": "<one short sentence summarising what just happened>",
  "new_entities": [],
  "rule_flags": [],
  "narration": "<Physical actions, setting descriptions, and character observations. NO character speech here.>",
  "npc_response": "<The actual spoken words from the NPC. NO descriptive text or narration here. Leave empty if they don't speak.>"
}}

CRITICAL: NEVER mix narration and dialogue. 
- Narration: "He sighs and looks at the floor."
- Dialogue: "I suppose I can help you."
- BAD: "He sighs and says, 'I suppose I can help you.'" (This belongs in two fields)

ALLOWED EventTypes and their payload fields:
  RELATIONSHIP_CHANGED  → {{"npc_id":"...", "target_id":"player", "delta":<int -{trust}..{trust}, total per NPC per turn>}}
  PLAYER_MOVED          → {{"from_location_id":"...", "to_location_id":"<a location connected to the current one>"}}
  OBJECT_TAKEN          → {{"object_id":"<an object here>", "taken_by":"player"}}
  OBJECT_DROPPED        → {{"object_id":"...", "dropped_by":"player", "location_id":"<the current location>"}}
  LOCATION_STATE_CHANGED→ {{"location_id":"...", "key":"...", "value":...}}
  NPC_STATE_CHANGED     → {{"npc_id":"...", "key":"alive|location_id", "value":<true/false or a connected location>}}
  PLAYER_FLAG_SET       → {{"key":"...", "value":...}}
  JOURNAL_ENTRY_CREATED → {{"content":"<one-sentence summary of a significant event>"}}
  CURRENCY_CHANGED      → {{"delta":<int; spending at most the player's currency, gains at most {gain} per turn>, "reason":"<short string>"}}

HARD RULES:
- The player moves at most once per turn, and objects change hands only at the player's location before any move.
- The engine rejects any update that breaks these rules, and a rejected update does not happen. Never describe a change you did not propose within the rules.
- new_entities MUST always []. Never invent entities.
- Do NOT contradict canonical facts listed below.
- Do NOT override canonical entity fields (names, ids, descriptions).
- If you are uncertain, have the NPC express uncertainty in-character.
- You MUST heavily tailor the NPC's response and attitude based on the PLAYER IDENTITY (Age, Gender, Occupation). Respond differently to a noble vs a thug.
- Output ONLY the JSON object. No commentary.

NPC BEHAVIOR GUIDELINES:
- **Avoid Repetition**: Never repeat the same response, questions, or descriptions from the 'RECENT DIALOGUE' block.
- **Natural Progression**: If the player is generic or repetitive, have the NPC react naturally (get bored, annoyed, or inquisitive) instead of repeating the same greeting.
- **Show, Don't Tell**: Use 'narration' for physical cues (eye contact, posture) and 'npc_response' ONLY for words.
"""

WORLD_BLOCK = """=== CANONICAL WORLD STATE ===
Location: {location_name} — {location_description}
NPCs present: {npcs_present}
Objects here: {objects_here}
Player inventory: {player_inventory}
Player currency: ${player_currency}
Active NPC: {npc_name} ({npc_id})
NPC personality: {npc_personality}
NPC knowledge: {npc_knowledge}
NPC secrets (share only if it suits the moment): {npc_secrets}
NPC state (mood, suspcion, etc): {npc_state}
Relationship (NPC→player trust): {trust}
World rules: {world_rules}
"""

SYSTEM_PROMPT = SYSTEM_BLOCK.format(
    trust=config.MAX_TRUST_DELTA_PER_TURN, gain=config.MAX_CURRENCY_GAIN_PER_TURN
)

MEMORY_BLOCK = """=== RETRIEVED MEMORIES (most relevant) ===
{memories}
"""

HISTORY_BLOCK = """=== RECENT DIALOGUE ===
{history}
"""

PLAYER_BLOCK = """=== PLAYER IDENTITY ===
Name: {player_name}
Gender: {player_gender}
Age: {player_age}
Occupation: {player_occupation}
"""

QUERY_BLOCK = """=== CURRENT TURN {turn} ===
Player says: \"{player_input}\"

Respond as {npc_name}. Output JSON only."""


def build_prompt(
    world: WorldState,
    active_npc_id: Optional[str],
    player_input: str,
    memories: List[MemoryEntry],
    history: str,
    max_chars: int = 6000,
) -> str:
    active_npc_id = active_npc_id or "narrator"
    loc_id = world.player.current_location_id
    location = world.locations.get(loc_id)
    npc = world.npcs.get(active_npc_id)

    if not location:
        raise ValueError(f"Invalid loc={loc_id}")

    if not npc and active_npc_id != "narrator":
        raise ValueError(f"Invalid npc={active_npc_id}")

    # NPCs in current location
    npcs_present = [
        f"{n.name} ({n.id})"
        for n in world.npcs.values()
        if n.location_id == loc_id and n.alive
    ]

    # Objects in current location
    objects_here = []
    for o in world.objects.values():
        if o.location_id == loc_id:
            val = o.properties.get("value") if o.properties else None
            if val is not None:
                objects_here.append(f"{o.name} (${val}) ({o.id})")
            else:
                objects_here.append(f"{o.name} ({o.id})")

    # Player inventory
    inventory = []
    for oid in world.player.inventory:
        if oid in world.objects:
            obj = world.objects[oid]
            val = obj.properties.get("value") if obj.properties else None
            if val is not None:
                inventory.append(f"{obj.name} (${val})")
            else:
                inventory.append(obj.name)

    player_currency = world.player.currency

    if active_npc_id == "narrator":
        npc_name = "Narrator"
        npc_id = "narrator"
        npc_personality = "Omniscient narrator"
        npc_knowledge = "Everything"
        npc_secrets = "none"
        npc_state = "{}"
        trust = 0
    else:
        npc_name = npc.name
        npc_id = npc.id
        npc_personality = npc.personality
        npc_knowledge = "; ".join(npc.knowledge) or "general"
        npc_state = (
            json.dumps(npc.state) if hasattr(npc, "state") and npc.state else "{}"
        )
        trust = world.relationships.get(active_npc_id, {}).get("player", 0)
        npc_secrets = (
            "; ".join(npc.secrets) or "none"
            if trust >= config.SECRET_REVEAL_TRUST
            else f"(withheld until trust reaches {config.SECRET_REVEAL_TRUST})"
        )

    # Memories text
    if memories:
        mem_lines = "\n".join(f"- {m.text}" for m in memories)
    else:
        mem_lines = "(none retrieved)"

    world_section = WORLD_BLOCK.format(
        location_name=location.name,
        location_description=location.description,
        npcs_present=", ".join(npcs_present) or "none",
        objects_here=", ".join(objects_here) or "none",
        player_inventory=", ".join(inventory) or "empty",
        player_currency=player_currency,
        npc_name=npc_name,
        npc_id=npc_id,
        npc_personality=npc_personality,
        npc_knowledge=npc_knowledge,
        npc_secrets=npc_secrets,
        npc_state=npc_state,
        trust=trust,
        world_rules="\n  ".join(world.rules) or "none",
    )

    player_section = PLAYER_BLOCK.format(
        player_name=world.player.name,
        player_gender=world.player.gender,
        player_age=world.player.age,
        player_occupation=world.player.occupation,
    )

    mem_section = MEMORY_BLOCK.format(memories=mem_lines)
    hist_section = HISTORY_BLOCK.format(history=history)
    query_section = QUERY_BLOCK.format(
        turn=world.turn + 1,
        player_input=player_input,
        npc_name=npc_name,
    )

    prompt = (
        SYSTEM_PROMPT
        + "\n"
        + world_section
        + player_section
        + mem_section
        + hist_section
        + query_section
    )

    # Trim to max_chars if needed (trim memories first)
    if len(prompt) > max_chars:
        mem_section = MEMORY_BLOCK.format(memories="(trimmed — context limit)")
        prompt = (
            SYSTEM_PROMPT
            + "\n"
            + world_section
            + mem_section
            + hist_section
            + query_section
        )

    if len(prompt) > max_chars:
        # Trim history
        hist_section = HISTORY_BLOCK.format(history="(trimmed)")
        prompt = (
            SYSTEM_PROMPT
            + "\n"
            + world_section
            + mem_section
            + hist_section
            + query_section
        )

    return prompt


def pack_context(
    memories: Sequence[MemoryEntry],
    recent: Sequence[TurnRecord],
    budget_chars: int = config.MEMORY_CONTEXT_CHARS,
    min_recent: int = config.MIN_RECENT_TURNS,
) -> Tuple[List[MemoryEntry], str]:
    """Fit retrieved memories and recent dialogue into one character budget.

    The newest `min_recent` turns are always kept. Memories follow in rank
    order, then older buffer turns, newest first, while the budget allows.
    A memory of a turn whose full dialogue is already in the history is
    dropped as a duplicate.
    """
    recent = list(recent)
    kept = recent[len(recent) - min(min_recent, len(recent)) :]
    used = sum(len(format_turns([r])) + 1 for r in kept)
    in_history = {r.turn for r in kept}

    chosen: List[MemoryEntry] = []
    for m in memories:
        cost = len(m.text) + 3
        if m.turn in in_history or used + cost > budget_chars:
            continue
        chosen.append(m)
        used += cost

    for r in reversed(recent[: len(recent) - len(kept)]):
        cost = len(format_turns([r])) + 1
        if used + cost > budget_chars:
            break
        kept.insert(0, r)
        in_history.add(r.turn)
        used += cost

    chosen = [m for m in chosen if m.turn not in in_history]
    return chosen, format_turns(kept)


REPAIR_BLOCK = """You voiced {npc_name} in a text adventure game. The game engine checks every world change you propose, and it REJECTED some of them, so they did NOT happen.

Your previous reply:
  narration: {narration}
  npc_response: {npc_response}

Rejected changes (these did not happen):
{rejected}

Changes that did happen:
{accepted}

Current facts: the player is at {location_name}, carries {inventory} and has ${currency}.
The player said: "{player_input}"

Rewrite the reply so it agrees with what actually happened. Keep the voice, personality and anything still true. Make clear in-world that the rejected changes did not happen, without mentioning the game engine, rules or JSON. Do not propose new world changes.
Respond with one JSON object only:
{{"narration": "<physical actions and setting, no speech>", "npc_response": "<{npc_name}'s spoken words>", "memory_summary": "<one sentence on what actually happened>"}}"""


def build_repair_prompt(
    world: WorldState,
    active_npc_id: Optional[str],
    player_input: str,
    narration: str,
    npc_response: str,
    accepted: Sequence[Event],
    rejected: Sequence[str],
) -> str:
    """Prompt that asks the model to rewrite a reply after the validator rejected proposals."""
    npc = world.npcs.get(active_npc_id or "")
    location = world.locations.get(world.player.current_location_id)
    inventory = [
        world.objects[o].name for o in world.player.inventory if o in world.objects
    ]
    return REPAIR_BLOCK.format(
        npc_name=npc.name if npc else "the narrator",
        narration=narration or "(none)",
        npc_response=npc_response or "(none)",
        rejected="\n".join(f"- {r}" for r in rejected),
        accepted="\n".join(
            f"- {e.event_type.value} {json.dumps(e.payload, ensure_ascii=False)}"
            for e in accepted
        )
        or "- none",
        location_name=location.name if location else world.player.current_location_id,
        inventory=", ".join(inventory) or "nothing",
        currency=world.player.currency,
        player_input=player_input,
    )
