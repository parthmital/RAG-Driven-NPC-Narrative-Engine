"""Groq LLM client wrapper."""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Optional

import config
from groq import APIConnectionError, APIError, APIStatusError, Groq

log = logging.getLogger(__name__)

_JSON_FENCE = re.compile(r"```(?:json)?\s*(\{.*?})\s*```", re.DOTALL)
_JSON_RAW = re.compile(r"(\{.*})", re.DOTALL)


class LLMError(RuntimeError):
    """An LLM request failed permanently; the message is safe to log."""


def _is_transient(exc: APIError) -> bool:
    if isinstance(exc, APIStatusError):
        return exc.status_code == 429 or exc.status_code >= 500
    return isinstance(exc, APIConnectionError)


def _describe(exc: Exception) -> str:
    """One-line summary of a Groq error without the raw response body."""
    if isinstance(exc, APIStatusError):
        body = exc.body if isinstance(exc.body, dict) else {}
        error = body.get("error", body)
        message = error.get("message") if isinstance(error, dict) else None
        return f"HTTP {exc.status_code}: {message or exc.message}"
    return f"{type(exc).__name__}: {exc}"


class GroqClient:
    def __init__(self, model: str, api_key: Optional[str] = None, timeout: int = 30):
        self.model = model
        # Retries are handled in generate(), so the SDK must not add its own.
        self.client = Groq(api_key=api_key, timeout=timeout, max_retries=0)

    def _complete(self, prompt: str, max_tokens: int, **kwargs):
        return self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
            max_tokens=max_tokens,
            **kwargs,
        )

    def ping(self) -> bool:
        try:
            self._complete("ping", max_tokens=1)
            return True
        except Exception as exc:
            log.warning("llm unreachable", extra={"error": _describe(exc)})
            return False

    def generate(
        self,
        prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.35,
        stream: bool = False,
        max_retries: int = config.LLM_MAX_RETRIES,
    ) -> str:
        """Return full response text, retrying rate limits and transient failures."""
        backoff = config.LLM_RETRY_BACKOFF
        for attempt in range(1, max_retries + 2):
            try:
                if stream:
                    return self._stream_generate(prompt, max_tokens, temperature)
                response = self._complete(prompt, max_tokens, temperature=temperature)
                return response.choices[0].message.content or ""
            except APIError as exc:
                if not _is_transient(exc) or attempt > max_retries:
                    raise LLMError(_describe(exc)) from exc
                log.warning(
                    "llm request failed; retrying",
                    extra={
                        "attempt": f"{attempt}/{max_retries}",
                        "wait_s": backoff,
                        "error": _describe(exc),
                    },
                )
                time.sleep(backoff)
                backoff *= 2
        raise AssertionError("unreachable")

    def _stream_generate(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Stream tokens from Groq and return the full text."""
        full_text = []
        stream = self._complete(
            prompt, max_tokens, temperature=temperature, stream=True
        )

        for chunk in stream:
            token = chunk.choices[0].delta.content or ""
            if token:
                full_text.append(token)

        return "".join(full_text)

    @staticmethod
    def extract_json(raw: Optional[str]) -> Optional[dict]:
        """Extract a JSON object from raw LLM output."""
        if not raw:
            return None

        def _try_parse(text: str) -> Optional[dict]:
            text = text.strip()
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass

            attempts = [
                text + '"',
                text + "}",
                text + '"}',
                text + '"]}',
                text + "}]}",
            ]
            for candidate in attempts:
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    continue
            return None

        for pattern in (_JSON_FENCE, _JSON_RAW):
            match = pattern.search(raw)
            if match:
                result = _try_parse(match.group(1))
                if result:
                    return result

        return _try_parse(raw)
