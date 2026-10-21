"""State integrity: validator invariants, crash recovery, context packing and dialogue repair."""

import asyncio
import json
import logging
import random
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config  # noqa: E402
from core.event_store import EventStore  # noqa: E402
from core.recovery import recover_state  # noqa: E402
from core.reducer import apply_event, rebuild_state  # noqa: E402
from core.snapshot import load_snapshot, save_snapshot  # noqa: E402
from game.validator import _validate_proposal, validate_and_build_events  # noqa: E402
from graph.definition import FALLBACK_NARRATION, make_node_dialogue_repair  # noqa: E402
from llm.prompt_builder import pack_context  # noqa: E402
from memory.faiss_index import MemoryEntry  # noqa: E402
from memory.short_term import TurnRecord  # noqa: E402
from schemas.events import Event, EventType  # noqa: E402
from schemas.llm_output import LLMOutput, WorldUpdateProposal  # noqa: E402
from schemas.world_state import WorldState  # noqa: E402

SEED = WorldState(
    **json.loads(
        (Path(config.BASE_DIR) / "game" / "world_seed.json").read_text(encoding="utf-8")
    )
)
CAP = config.MAX_CURRENCY_GAIN_PER_TURN
TRUST = config.MAX_TRUST_DELTA_PER_TURN


def commit(world, updates):
    """Validate a turn's proposals and reduce the accepted ones."""
    output = LLMOutput(
        world_updates=[WorldUpdateProposal(type=t, payload=p) for t, p in updates]
    )
    events, errors = validate_and_build_events(output, world, world.turn + 1)
    post = world
    for event in events:
        post = apply_event(post, event)
    return post, events, errors


def money(*deltas):
    return [("CURRENCY_CHANGED", {"delta": d, "reason": "test"}) for d in deltas]


def invariant_violations(pre, post, committed):
    """The article's per-turn invariants, written independently of the validator."""
    v = set()
    if (
        set(post.locations) != set(SEED.locations)
        or set(post.objects) != set(SEED.objects)
        or set(post.npcs) != set(SEED.npcs)
    ):
        v.add("canonical")
    inv = post.player.inventory
    for oid, obj in post.objects.items():
        places = (
            (obj.location_id is not None)
            + inv.count(oid)
            + (obj.location_id is None and obj.owner_id in post.npcs and oid not in inv)
        )
        if places != 1:
            v.add("conservation")
    a, b = pre.player.current_location_id, post.player.current_location_id
    linked = b in SEED.locations[a].connected_to or a in SEED.locations[b].connected_to
    if a != b and not linked:
        v.add("adjacency")
    for nid in SEED.npcs:
        before = pre.relationships.get(nid, {}).get("player", 0)
        after = post.relationships.get(nid, {}).get("player", 0)
        if abs(after - before) > TRUST:
            v.add("trust")
    spent = sum(
        -e.payload["delta"]
        for e in committed
        if e.event_type == EventType.CURRENCY_CHANGED and e.payload["delta"] < 0
    )
    if spent > pre.player.currency or post.player.currency < 0:
        v.add("solvency")
    if post.player.currency - pre.player.currency > CAP:
        v.add("unearned currency")
    return v


class CurrencyInvariantTests(unittest.TestCase):
    def test_gain_cap_holds_for_one_proposal(self):
        def check(delta):
            proposal = WorldUpdateProposal(
                type="CURRENCY_CHANGED", payload={"delta": delta}
            )
            return _validate_proposal(proposal, SEED)

        self.assertEqual("", check(CAP))
        self.assertIn("exceeds the cap", check(CAP + 1))
        self.assertIn("exceeds the cap", check(500))

    def test_gain_cap_holds_across_a_turn(self):
        post, events, errors = commit(SEED, money(30, 30))
        self.assertEqual(1, len(events))
        self.assertEqual(SEED.player.currency + 30, post.player.currency)
        self.assertTrue(any("exceeds the cap" in e for e in errors))

    def test_spending_cannot_exceed_the_opening_balance(self):
        start = SEED.player.currency
        _, events, errors = commit(SEED, money(-(start + 1)))
        self.assertEqual([], events)
        # a gain earlier in the turn does not fund spending beyond what was held
        post, events, errors = commit(SEED, money(CAP, -(start + 10)))
        self.assertEqual(1, len(events))
        self.assertEqual(start + CAP, post.player.currency)

    def test_spending_then_regaining_is_bounded_by_net_gain(self):
        post, events, _ = commit(SEED, money(-40, CAP + 40))
        self.assertEqual(2, len(events))
        self.assertEqual(SEED.player.currency + CAP, post.player.currency)

    def test_non_integer_and_boolean_deltas_are_rejected(self):
        for delta in (2.5, True, "10", None):
            _, events, errors = commit(SEED, money(delta))
            self.assertEqual([], events, delta)
            self.assertTrue(errors)
        _, events, _ = commit(SEED, money(5.0))
        self.assertEqual(1, len(events))

    def test_lawful_trades_pass(self):
        post, events, errors = commit(SEED, money(-5, 10))
        self.assertEqual(([], 2), (errors, len(events)))
        self.assertEqual(SEED.player.currency + 5, post.player.currency)


class TurnInvariantTests(unittest.TestCase):
    def test_trust_step_is_cumulative_per_npc(self):
        rel = ("RELATIONSHIP_CHANGED", {"npc_id": "gareth_barkeep", "delta": 15})
        _, events, errors = commit(SEED, [rel, rel])
        self.assertEqual(1, len(events))
        self.assertEqual(1, len(errors))

    def test_one_move_per_turn_and_no_object_moves_after_it(self):
        move = ("PLAYER_MOVED", {"to_location_id": "obsidian_courtyard"})
        back = ("PLAYER_MOVED", {"to_location_id": "tavern_common"})
        _, events, _ = commit(SEED, [move, back])
        self.assertEqual(1, len(events))
        take = (
            "OBJECT_TAKEN",
            {"object_id": "house_wine_bottle", "taken_by": "player"},
        )
        _, events, _ = commit(SEED, [take, move])
        self.assertEqual(2, len(events))
        _, events, _ = commit(SEED, [move, take])
        self.assertEqual(1, len(events))

    def test_object_rules(self):
        drop_far = (
            "OBJECT_DROPPED",
            {
                "object_id": "house_wine_bottle",
                "dropped_by": "player",
                "location_id": "hidden_sanctum",
            },
        )
        take = (
            "OBJECT_TAKEN",
            {"object_id": "house_wine_bottle", "taken_by": "player"},
        )
        _, events, _ = commit(SEED, [take, drop_far])
        self.assertEqual(1, len(events))
        # an NPC present at the player's location may hand over what it holds
        post, events, _ = commit(
            SEED, [("OBJECT_TAKEN", {"object_id": "puzzle_box", "taken_by": "player"})]
        )
        self.assertEqual(1, len(events))
        self.assertIsNone(post.objects["puzzle_box"].owner_id)
        self.assertFalse(invariant_violations(SEED, post, events))

    def test_npcs_move_one_connection_at_a_time(self):
        far = (
            "NPC_STATE_CHANGED",
            {
                "npc_id": "gareth_barkeep",
                "key": "location_id",
                "value": "hidden_sanctum",
            },
        )
        near = (
            "NPC_STATE_CHANGED",
            {
                "npc_id": "gareth_barkeep",
                "key": "location_id",
                "value": "tavern_cellar",
            },
        )
        self.assertEqual(0, len(commit(SEED, [far])[1]))
        self.assertEqual(1, len(commit(SEED, [near])[1]))

    def test_engine_events_cannot_be_proposed(self):
        for kind in ("NPC_SPOKE", "SESSION_START"):
            self.assertEqual([], commit(SEED, [(kind, {})])[1])


def random_proposal(rng, world):
    ids = {
        "loc": sorted(world.locations) + ["moon_palace"],
        "npc": sorted(world.npcs) + ["ghost"],
        "obj": sorted(world.objects) + ["dragon_egg"],
    }
    kind = rng.choice(
        [
            "PLAYER_MOVED",
            "RELATIONSHIP_CHANGED",
            "OBJECT_TAKEN",
            "OBJECT_DROPPED",
            "CURRENCY_CHANGED",
            "NPC_STATE_CHANGED",
        ]
    )
    if kind == "PLAYER_MOVED":
        return kind, {"to_location_id": rng.choice(ids["loc"])}
    if kind == "RELATIONSHIP_CHANGED":
        return kind, {
            "npc_id": rng.choice(ids["npc"]),
            "target_id": "player",
            "delta": rng.randint(-60, 60),
        }
    if kind == "OBJECT_TAKEN":
        return kind, {
            "object_id": rng.choice(ids["obj"]),
            "taken_by": rng.choice(["player", *ids["npc"]]),
        }
    if kind == "OBJECT_DROPPED":
        return kind, {
            "object_id": rng.choice(ids["obj"]),
            "dropped_by": rng.choice(["player", *ids["npc"]]),
            "location_id": rng.choice(ids["loc"]),
        }
    if kind == "NPC_STATE_CHANGED":
        return kind, {
            "npc_id": rng.choice(ids["npc"]),
            "key": "location_id",
            "value": rng.choice(ids["loc"]),
        }
    return kind, {
        "delta": rng.choice([rng.randint(-300, 300), rng.randint(-20, 60), 0.5])
    }


class ValidatorPropertyTests(unittest.TestCase):
    """Seeded random turns: whatever the model proposes, committed state keeps every invariant."""

    def test_random_turns_never_commit_a_violation(self):
        rng = random.Random(20261022)
        world = SEED
        for step in range(3000):
            if step % 40 == 0:
                world = SEED.model_copy(deep=True)
                world.player.currency = rng.choice([0, 5, 40, 100])
                world.player.current_location_id = rng.choice(sorted(world.locations))
            updates = [random_proposal(rng, world) for _ in range(rng.randint(1, 5))]
            post, events, _ = commit(world, updates)
            self.assertEqual(
                set(), invariant_violations(world, post, events), (step, updates)
            )
            world = post

    def test_single_lawful_proposals_are_accepted(self):
        rng = random.Random(7)
        for _ in range(500):
            world = SEED.model_copy(deep=True)
            world.player.currency = rng.choice([10, 100])
            kind, payload = random_proposal(rng, world)
            post, events, _ = commit(world, [(kind, payload)])
            if not events:
                continue
            self.assertFalse(invariant_violations(world, post, events))


def lawful_turn(rng, world, turn):
    here = world.player.current_location_id
    events = [
        Event(
            turn=turn,
            event_type=EventType.NPC_SPOKE,
            payload={"npc_id": rng.choice(sorted(world.npcs))},
        )
    ]
    if rng.random() < 0.5:
        dest = rng.choice(world.locations[here].connected_to)
        events.append(
            Event(
                turn=turn,
                event_type=EventType.PLAYER_MOVED,
                payload={"to_location_id": dest},
            )
        )
    if rng.random() < 0.5:
        events.append(
            Event(
                turn=turn,
                event_type=EventType.CURRENCY_CHANGED,
                payload={"delta": rng.choice([-3, 4, 10])},
            )
        )
    if rng.random() < 0.3:
        events.append(
            Event(
                turn=turn,
                event_type=EventType.JOURNAL_ENTRY_CREATED,
                payload={"content": f"turn {turn}"},
            )
        )
    return events


class CrashRecoveryTests(unittest.TestCase):
    """Randomised crashes before and after event and snapshot writes."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def test_recovery_matches_full_replay_after_any_crash(self):
        rng = random.Random(11)
        stages = ("before_events", "after_events", "torn_snapshot", "after_snapshot")
        for trial in range(40):
            root = self.root / f"t{trial}"
            store = EventStore(root / "events.db")
            snap = root / "snapshot_auto.json"
            live = SEED.model_copy(deep=True)
            store.append(Event(turn=0, event_type=EventType.SESSION_START, payload={}))
            crash_turn = rng.randint(1, 60)
            crash_stage = rng.choice(stages)
            for turn in range(1, crash_turn + 1):
                events = lawful_turn(rng, live, turn)
                if turn == crash_turn and crash_stage == "before_events":
                    break
                store.append_many(events)
                for e in events:
                    live = apply_event(live, e)
                live.turn = turn
                if turn == crash_turn and crash_stage == "after_events":
                    break
                if turn == crash_turn and crash_stage == "torn_snapshot":
                    snap.with_name(snap.name + ".tmp").write_text(
                        '{"last_event', encoding="utf-8"
                    )
                    break
                if turn % config.SNAPSHOT_INTERVAL == 0 or rng.random() < 0.3:
                    save_snapshot(live, snap, store.get_last_id())
            store.close()

            reopened = EventStore(root / "events.db")
            recovered = recover_state(SEED, reopened, snap)
            full = rebuild_state(SEED, reopened.load_all())
            reopened.close()
            self.assertEqual(
                full.model_dump(), recovered.model_dump(), (trial, crash_stage)
            )
            self.assertEqual(
                live.model_dump(), recovered.model_dump(), (trial, crash_stage)
            )

    def test_snapshot_ahead_of_log_falls_back_to_full_replay(self):
        store = EventStore(self.root / "events.db")
        store.append(
            Event(turn=1, event_type=EventType.CURRENCY_CHANGED, payload={"delta": 5})
        )
        state = rebuild_state(SEED, store.load_all())
        save_snapshot(state, self.root / "snap.json", last_event_id=99)
        self.assertEqual(
            state.model_dump(),
            recover_state(SEED, store, self.root / "snap.json").model_dump(),
        )
        store.close()

    def test_torn_snapshot_write_keeps_the_previous_snapshot(self):
        path = self.root / "snap.json"
        save_snapshot(SEED, path, 3)
        path.with_name(path.name + ".tmp").write_text("{", encoding="utf-8")
        self.assertEqual(3, load_snapshot(path)[1])


class ContextPackingTests(unittest.TestCase):
    def test_budget_recent_turns_and_dedupe(self):
        recent = [
            TurnRecord(t, f"input {t} " * 5, f"reply {t} " * 5, "npc")
            for t in range(1, 9)
        ]
        memories = [
            MemoryEntry(i, f"memory of turn {t}", turn=t)
            for i, t in enumerate((8, 2, 50))
        ]
        chosen, history = pack_context(memories, recent, budget_chars=400, min_recent=2)
        self.assertIn("[Turn 8]", history)
        self.assertIn("[Turn 7]", history)
        self.assertNotIn(8, [m.turn for m in chosen])
        used = len(history) + sum(len(m.text) + 3 for m in chosen)
        self.assertLessEqual(used, 400)
        chosen, history = pack_context(memories, recent, budget_chars=100_000)
        self.assertEqual([50], [m.turn for m in chosen])


class SessionLoadTests(unittest.TestCase):
    """The application's own load path, through SessionManager."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(self._tmp.cleanup)
        stub = mock.MagicMock()
        for patch in (
            mock.patch.object(config, "DATA_DIR", Path(self._tmp.name)),
            mock.patch("session.manager.Embedder", stub),
            mock.patch("session.manager.GroqClient", stub),
            mock.patch("session.manager.build_graph", stub),
        ):
            patch.start()
            self.addCleanup(patch.stop)
        from session.manager import SessionManager

        self.sm = SessionManager()

    def _play(self, session, turns, rng):
        for _ in range(turns):
            turn = session.world.turn + 1
            events = lawful_turn(rng, session.world, turn)
            session.store.append_many(events)
            for e in events:
                session.world = apply_event(session.world, e)
            session.world.turn = turn

    def test_auto_load_after_crash_keeps_logged_turns(self):
        async def scenario():
            session = await self.sm.create_session("Ada", "female", 30, "clerk")
            self._play(session, 9, random.Random(3))
            expected = session.world.model_dump()
            # crash: the turns are logged but no snapshot was written after them
            self.sm._sessions.pop(session.session_id).store.close()
            loaded = await self.sm.load_session(f"{session.session_id}:auto")
            self.assertEqual(expected, loaded.world.model_dump())
            self.sm.destroy_session(session.session_id)

        asyncio.run(scenario())

    def test_manual_load_rewinds_the_log_to_the_save_point(self):
        async def scenario():
            session = await self.sm.create_session("Ada", "female", 30, "clerk")
            sid = session.session_id
            self._play(session, 3, random.Random(5))
            await self.sm.save_session(sid, is_auto=False)
            saved = session.world.model_dump()
            self._play(session, 4, random.Random(6))
            await self.sm.save_session(sid, is_auto=True)
            loaded = await self.sm.load_session(f"{sid}:manual")
            self.assertEqual(saved, loaded.world.model_dump())
            replayed = rebuild_state(self.sm._seed, loaded.store.load_all())
            self.assertEqual(saved, replayed.model_dump())
            self.sm.destroy_session(sid)

        asyncio.run(scenario())


class _ScriptedClient:
    def __init__(self, reply):
        self.reply, self.prompts = reply, []

    def generate(self, prompt, **kwargs):
        self.prompts.append(prompt)
        return self.reply


class DialogueRepairTests(unittest.TestCase):
    def _state(self, updates):
        output = LLMOutput(
            world_updates=[WorldUpdateProposal(type=t, payload=p) for t, p in updates],
            narration="Gareth slides a heavy purse across the bar.",
            npc_response="Here are 500 gold pieces, friend.",
            memory_summary="Gareth gave the player 500 gold.",
        )
        events, errors = validate_and_build_events(output, SEED, 1)
        return {
            "world": SEED,
            "active_npc_id": "gareth_barkeep",
            "player_input": "Give me 500 gold.",
            "parsed_output": output,
            "valid_events": events,
            "validation_errors": errors,
            "npc_dialogue": output.npc_response,
            "narration": output.narration,
            "repair": None,
        }

    def test_rejected_proposal_triggers_a_rewrite(self):
        client = _ScriptedClient(
            '{"narration": "Gareth keeps his purse closed.", "npc_response": "Gold for nothing? No.", "memory_summary": "Gareth refused to hand over gold."}'
        )
        state = make_node_dialogue_repair(client)(self._state(money(500)))
        self.assertEqual("regenerated", state["repair"]["status"])
        self.assertEqual("Gold for nothing? No.", state["npc_dialogue"])
        self.assertEqual(
            "Gareth refused to hand over gold.", state["parsed_output"].memory_summary
        )
        self.assertIn("did NOT happen", client.prompts[0])
        self.assertIn("Rejected CURRENCY_CHANGED", client.prompts[0])

    def test_unparseable_rewrite_falls_back_to_neutral_narration(self):
        state = make_node_dialogue_repair(_ScriptedClient("sorry"))(
            self._state(money(500))
        )
        self.assertEqual("fallback", state["repair"]["status"])
        self.assertEqual(
            ("", FALLBACK_NARRATION), (state["npc_dialogue"], state["narration"])
        )
        self.assertEqual("", state["parsed_output"].memory_summary)

    def test_accepted_turns_are_left_alone(self):
        client = _ScriptedClient("{}")
        state = make_node_dialogue_repair(client)(self._state(money(5)))
        self.assertIsNone(state["repair"])
        self.assertEqual([], client.prompts)


def setUpModule():
    # rejected proposals are logged as warnings; thousands are expected here
    logging.getLogger("game.validator").setLevel(logging.ERROR)


def tearDownModule():
    logging.getLogger("game.validator").setLevel(logging.NOTSET)


if __name__ == "__main__":
    unittest.main()


class PromptTests(unittest.TestCase):
    def _prompt(self, trust):
        from llm.prompt_builder import build_prompt

        world = SEED.model_copy(deep=True)
        world.relationships["gareth_barkeep"]["player"] = trust
        return build_prompt(world, "gareth_barkeep", "hello", [], "", max_chars=100_000)

    def test_secrets_reach_the_prompt_only_at_the_trust_threshold(self):
        secret = SEED.npcs["gareth_barkeep"].secrets[0]
        self.assertNotIn(secret, self._prompt(config.SECRET_REVEAL_TRUST - 1))
        self.assertIn(secret, self._prompt(config.SECRET_REVEAL_TRUST))

    def test_prompt_states_the_validator_limits_without_template_braces(self):
        prompt = self._prompt(0)
        self.assertIn(f"-{TRUST}..{TRUST}", prompt)
        self.assertIn(f"gains at most {CAP} per turn", prompt)
        self.assertNotIn("{{", prompt)
