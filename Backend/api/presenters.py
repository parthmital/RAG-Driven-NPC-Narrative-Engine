"""Presentation mappers for API response models."""

from __future__ import annotations

from typing import Any, Optional

from api.schemas import (
    ClueInfo,
    GameStateResponse,
    LocationInfo,
    NPCInfo,
    ObjectInfo,
    PlayerInfo,
    SessionInfo,
    TrustThreshold,
)

EMOTION_LABELS = {
    "neutral": "Composed",
    "suspicious": "Suspicious",
    "fearful": "Fearful",
    "angry": "Hostile",
    "melancholic": "Melancholic",
    "guarded": "Guarded",
    "trusting": "Trusting",
    "desperate": "Desperate",
    "hostile": "Hostile",
    "playful": "Playful",
}


def build_session_info(session: Any) -> SessionInfo:
    return SessionInfo(
        session_id=session.session_id,
        player_name=session.world.player.name,
        turn=session.world.turn,
        active_npc_id=session.active_npc_id,
        current_location_id=session.world.player.current_location_id,
        created_at=session.created_at,
    )


def build_object_info(obj: Any) -> ObjectInfo:
    return ObjectInfo(
        id=obj.id,
        name=obj.name,
        description=obj.description,
        location_id=obj.location_id,
        properties=obj.properties,
    )


def build_npc_info(session: Any, npc: Any) -> NPCInfo:
    trust = session.world.relationships.get(npc.id, {}).get("player", 0)

    if trust > 60:
        emotional_state = "trusting"
    elif trust > 30:
        emotional_state = "neutral"
    elif trust < -20:
        emotional_state = "hostile"
    else:
        emotional_state = "guarded"

    if trust > 60:
        relationship_tier = "confidant"
    elif trust > 30:
        relationship_tier = "acquaintance"
    else:
        relationship_tier = "stranger"

    trust_thresholds = [
        TrustThreshold(value=-50, label="Wary", unlocked=trust >= -50),
        TrustThreshold(value=0, label="Neutral", unlocked=trust >= 0),
        TrustThreshold(value=50, label="Friendly", unlocked=trust >= 50),
    ]

    return NPCInfo(
        id=npc.id,
        name=npc.name,
        description=npc.description,
        personality=npc.personality,
        location_id=npc.location_id,
        alive=npc.alive,
        trust=trust,
        title=npc.personality.split(".")[0] if npc.personality else None,
        emotional_state=emotional_state,
        emotional_label=EMOTION_LABELS.get(emotional_state, "Composed"),
        relationship_tier=relationship_tier,
        trust_thresholds=trust_thresholds,
        suspicion=max(0, -trust),
        trust_percent=((trust + 100) / 200) * 100,
    )


def build_location_info(
    session: Any, location_id: Optional[str] = None
) -> Optional[LocationInfo]:
    world = session.world
    loc_id = location_id or world.player.current_location_id
    loc = world.locations.get(loc_id)
    if not loc:
        return None

    npcs_present = [
        build_npc_info(session, npc)
        for npc in world.npcs.values()
        if npc.location_id == loc.id and npc.alive
    ]
    objects_here = [
        build_object_info(obj)
        for obj in world.objects.values()
        if obj.location_id == loc.id
    ]

    return LocationInfo(
        id=loc.id,
        name=loc.name,
        description=loc.description,
        connected_to=loc.connected_to,
        npcs_present=npcs_present,
        objects_here=objects_here,
        state=loc.state,
    )


def build_player_info(session: Any) -> PlayerInfo:
    world = session.world
    inventory = [
        build_object_info(world.objects[object_id])
        for object_id in world.player.inventory
        if object_id in world.objects
    ]

    return PlayerInfo(
        current_location_id=world.player.current_location_id,
        inventory=inventory,
        flags=world.player.flags,
        moral_alignment=world.player.moral_alignment,
        currency=world.player.currency,
    )


def build_game_state_response(session: Any) -> GameStateResponse:
    active_npc_obj = session.world.npcs.get(session.active_npc_id)
    active_npc = build_npc_info(session, active_npc_obj) if active_npc_obj else None

    return GameStateResponse(
        session_id=session.session_id,
        turn=session.world.turn,
        active_npc_id=session.active_npc_id,
        active_npc=active_npc,
        location=build_location_info(session),
        player=build_player_info(session),
        relationships=session.world.relationships,
        journal=[
            {
                "id": entry.id,
                "turn": entry.turn,
                "content": entry.content,
                "timestamp": entry.timestamp * 1000,
                "tags": [],
            }
            for entry in session.world.journal
        ],
        clues=[
            ClueInfo(
                id=clue.id,
                title=clue.title,
                description=clue.description,
                linked_clues=clue.linked_clues,
                npc_id=clue.npc_id,
                tension=clue.tension,
                discovered=clue.discovered,
            )
            for clue in session.world.clues.values()
        ],
        dialogue_history=session.dialogue_history,
    )
