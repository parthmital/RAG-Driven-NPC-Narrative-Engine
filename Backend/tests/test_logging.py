import json
import logging
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from log_config import (  # noqa: E402
    JsonFormatter,
    TextFormatter,
    request_id_var,
    session_id_var,
)
from schemas.events import EventType  # noqa: E402


def _record(msg="turn complete", **extra):
    record = logging.makeLogRecord(
        {"name": "graph.definition", "levelname": "INFO", "msg": msg}
    )
    record.__dict__.update(extra)
    return record


class FormatterTests(unittest.TestCase):
    def setUp(self):
        for var, value in ((request_id_var, "ab12cd34"), (session_id_var, "s-1")):
            self.addCleanup(var.reset, var.set(value))

    def test_text_renders_fields_then_context(self):
        line = TextFormatter().format(
            _record(turn=3, npc="elara", reason="not here", type=EventType.PLAYER_MOVED)
        )
        self.assertRegex(line, r"^\d{2}:\d{2}:\d{2}\.\d{3} INFO +graph\.definition +")
        self.assertTrue(
            line.endswith(
                'turn complete  turn=3 npc=elara reason="not here" '
                "type=PLAYER_MOVED req=ab12cd34 session=s-1"
            ),
            line,
        )

    def test_json_is_one_parseable_object(self):
        entry = json.loads(JsonFormatter().format(_record(turn=3)))
        self.assertEqual("turn complete", entry["msg"])
        self.assertEqual(3, entry["turn"])
        self.assertEqual("ab12cd34", entry["req"])
        self.assertEqual("s-1", entry["session"])

    def test_explicit_session_field_wins_over_context(self):
        line = TextFormatter().format(_record("session closed", session="s-2"))
        self.assertIn("session=s-2", line)
        self.assertNotIn("session=s-1", line)


if __name__ == "__main__":
    unittest.main()
