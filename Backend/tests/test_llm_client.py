import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from groq import AuthenticationError, RateLimitError  # noqa: E402
from llm.groq_client import GroqClient, LLMError  # noqa: E402

REQUEST = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")


def _status_error(cls, status):
    body = {"error": {"message": f"status {status}"}}
    response = httpx.Response(status, request=REQUEST, json=body)
    return cls(f"Error code: {status}", response=response, body=body)


def _reply(text):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=text))]
    )


class GenerateRetryTests(unittest.TestCase):
    def setUp(self):
        self.client = GroqClient(model="test", api_key="test")
        patcher = mock.patch("llm.groq_client.time.sleep")
        self.sleep = patcher.start()
        self.addCleanup(patcher.stop)

    def test_auth_error_fails_fast_with_concise_message(self):
        error = _status_error(AuthenticationError, 401)
        with mock.patch.object(self.client, "_complete", side_effect=error) as call:
            with self.assertRaises(LLMError) as raised:
                self.client.generate("hi")
        self.assertEqual(1, call.call_count)
        self.assertEqual("HTTP 401: status 401", str(raised.exception))
        self.sleep.assert_not_called()

    def test_rate_limit_retries_with_backoff(self):
        error = _status_error(RateLimitError, 429)
        with mock.patch.object(
            self.client, "_complete", side_effect=[error, error, _reply("ok")]
        ), self.assertLogs("llm.groq_client", "WARNING") as logs:
            self.assertEqual("ok", self.client.generate("hi", max_retries=3))
        self.assertEqual(2, len(logs.output))
        self.assertEqual([1.0, 2.0], [c.args[0] for c in self.sleep.call_args_list])

    def test_gives_up_after_max_retries(self):
        error = _status_error(RateLimitError, 429)
        with mock.patch.object(self.client, "_complete", side_effect=error) as call:
            with self.assertRaises(LLMError), self.assertLogs("llm.groq_client"):
                self.client.generate("hi", max_retries=2)
        self.assertEqual(3, call.call_count)


class ExtractJsonTests(unittest.TestCase):
    def test_returns_object(self):
        self.assertEqual({"a": 1}, GroqClient.extract_json('Sure: {"a": 1}'))

    def test_repairs_truncated_object(self):
        self.assertEqual({"a": "b"}, GroqClient.extract_json('{"a": "b'))

    def test_non_object_json_is_rejected(self):
        for raw in ('"Hello there', "[1, 2]", "42", '"quoted reply"'):
            self.assertIsNone(GroqClient.extract_json(raw), raw)


if __name__ == "__main__":
    unittest.main()
