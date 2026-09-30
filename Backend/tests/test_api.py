"""HTTP API characterisation tests with the embedder, LLM, and graph stubbed."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from log_config import request_id_var, session_id_var  # noqa: E402

MANAGER_MODULE = "session.manager"


class _StubEmbedder:
    def __init__(self, *args, **kwargs):
        pass

    def embed(self, text):
        return None

    def close(self):
        pass


class _StubClient:
    def __init__(self, *args, **kwargs):
        pass

    def ping(self):
        return True


class _StubGraph:
    seen_context = None

    def invoke(self, state):
        _StubGraph.seen_context = (request_id_var.get(), session_id_var.get())
        world = state["world"]
        world.turn += 1
        return {
            **state,
            "world": world,
            "narration": " The fire crackles. ",
            "npc_dialogue": " Welcome. ",
        }


class ApiTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(self._tmp.cleanup)
        patches = [
            mock.patch.object(config, "DATA_DIR", Path(self._tmp.name)),
            mock.patch(f"{MANAGER_MODULE}.Embedder", _StubEmbedder),
            mock.patch(f"{MANAGER_MODULE}.GroqClient", _StubClient),
            mock.patch(f"{MANAGER_MODULE}.build_graph", lambda *a, **k: _StubGraph()),
        ]
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)

        from api.app import create_app

        self.client = TestClient(create_app())
        self.client.__enter__()
        self.addCleanup(self.client.__exit__, None, None, None)

    def _create(self):
        response = self.client.post(
            "/api/game/session",
            json={"name": "Ada", "gender": "female", "age": 30, "occupation": "clerk"},
        )
        self.assertEqual(200, response.status_code, response.text)
        return response.json()["session_id"]

    def test_health_and_metadata(self):
        self.assertEqual(
            {"status": "ok", "ready": True}, self.client.get("/health").json()
        )
        health = self.client.get("/api/game/health").json()
        self.assertTrue(health["llm_reachable"])
        self.assertEqual(0, health["active_sessions"])
        self.assertTrue(self.client.get("/api/game/metadata").json()["title"])

    def test_session_lifecycle(self):
        session_id = self._create()
        state = self.client.get(f"/api/game/state/{session_id}").json()
        self.assertEqual(session_id, state["session_id"])
        loaded = self.client.post(f"/api/game/load/{session_id}:auto").json()
        self.assertEqual("Ada", loaded["player_name"])

        self.assertEqual(
            {"status": "saved"}, self.client.post(f"/api/game/save/{session_id}").json()
        )
        saves = self.client.get("/api/game/sessions").json()
        self.assertEqual(
            {f"{session_id}:manual", f"{session_id}:auto"},
            {save["session_id"] for save in saves},
        )

        self.assertEqual(
            200, self.client.delete(f"/api/game/session/{session_id}").status_code
        )
        self.assertEqual(
            404, self.client.get(f"/api/game/state/{session_id}").status_code
        )
        self.assertEqual(404, self.client.post("/api/game/save/missing").status_code)

    def test_action_appends_dialogue(self):
        session_id = self._create()
        before = len(
            self.client.get(f"/api/game/state/{session_id}").json()["dialogue_history"]
        )
        result = self.client.post(
            f"/api/game/action/{session_id}", json={"content": " look around "}
        ).json()
        self.assertEqual("Welcome.", result["npc_dialogue"])
        self.assertEqual("The fire crackles.", result["narration"])
        self.assertEqual(1, result["turn"])

        history = self.client.get(f"/api/game/state/{session_id}").json()[
            "dialogue_history"
        ]
        added = history[before:]
        self.assertEqual("player", added[0]["type"])
        self.assertEqual("look around", added[0]["content"])
        self.assertEqual("narration", added[1]["type"])

    def test_move_and_objects(self):
        session_id = self._create()
        state = self.client.get(f"/api/game/state/{session_id}").json()
        location = state["location"]

        bad = self.client.post(
            f"/api/game/move/{session_id}", json={"location_id": "nowhere"}
        )
        self.assertEqual(400, bad.status_code)

        if location["objects_here"]:
            object_id = location["objects_here"][0]["id"]
            picked = self.client.post(
                f"/api/game/pickup/{session_id}/{object_id}"
            ).json()
            self.assertIn(object_id, [o["id"] for o in picked["player"]["inventory"]])
            again = self.client.post(f"/api/game/pickup/{session_id}/{object_id}")
            self.assertEqual(400, again.status_code)
            dropped = self.client.post(
                f"/api/game/drop/{session_id}/{object_id}"
            ).json()
            self.assertNotIn(
                object_id, [o["id"] for o in dropped["player"]["inventory"]]
            )

        if location["connected_to"]:
            target = location["connected_to"][0]
            moved = self.client.post(
                f"/api/game/move/{session_id}", json={"location_id": target}
            ).json()
            self.assertEqual(target, moved["location"]["id"])
            self.assertEqual(state["turn"] + 1, moved["turn"])

        self.assertEqual(
            400,
            self.client.post(
                f"/api/game/clue/link/{session_id}", json={"id1": "x", "id2": "y"}
            ).status_code,
        )

    def test_npcs_and_websocket(self):
        session_id = self._create()
        npcs = self.client.get(
            f"/api/game/npcs/{session_id}?location_only=false"
        ).json()
        self.assertIn("npcs", npcs)
        self.assertEqual(
            404, self.client.post(f"/api/game/npc/{session_id}/ghost").status_code
        )

        with self.client.websocket_connect(f"/ws/game/{session_id}") as ws:
            self.assertEqual("connected", ws.receive_json()["type"])
            ws.send_json({"type": "ping"})
            self.assertEqual("pong", ws.receive_json()["type"])
            ws.send_json({"type": "action", "payload": {"content": "hello"}})
            message = ws.receive_json()
            self.assertEqual("npc_response", message["type"])
            self.assertEqual("Welcome.", message["payload"]["npc_dialogue"])

    def test_request_id_reaches_response_and_turn_pipeline(self):
        session_id = self._create()
        response = self.client.post(
            f"/api/game/action/{session_id}",
            json={"content": "hello"},
            headers={"X-Request-ID": "trace-1"},
        )
        self.assertEqual("trace-1", response.headers["X-Request-ID"])
        self.assertEqual(("trace-1", session_id), _StubGraph.seen_context)
        self.assertRegex(
            self.client.get("/health").headers["X-Request-ID"], r"^[0-9a-f]{8}$"
        )

    def test_unhandled_error_returns_generic_500(self):
        manager = self.client.app.state.session_manager
        with mock.patch.object(
            manager, "list_sessions", side_effect=RuntimeError("disk gone")
        ), self.assertLogs("api.app", "ERROR") as logs:
            response = self.client.get("/api/game/sessions")
        self.assertEqual(500, response.status_code)
        self.assertEqual({"error": "Internal server error"}, response.json())
        self.assertIn("X-Request-ID", response.headers)
        self.assertIn("unhandled error", logs.output[0])


if __name__ == "__main__":
    unittest.main()
