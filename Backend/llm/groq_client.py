"""Groq LLM client wrapper."""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Optional

import config
from groq import Groq

log = logging.getLogger(__name__)

_JSON_FENCE = re.compile(r"```(?:json)?\s*(\{.*?})\s*```", re.DOTALL)
_JSON_RAW = re.compile(r"(\{.*})", re.DOTALL)


class GroqClient:
    def __init__(self, model: str, api_key: Optional[str] = None, timeout: int = 30):
        self.model = model
        self.client = Groq(api_key=api_key, timeout=timeout)

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
            log.error("Groq unreachable or error: %s", exc)
            return False

    def generate(
        self,
        prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.35,
        stream: bool = False,
        max_retries: int = config.LLM_MAX_RETRIES,
    ) -> str:
        """Return full response text with retry handling for rate limits."""
        retries = 0
        backoff = config.LLM_RETRY_BACKOFF

        while retries <= max_retries:
            try:
                if stream:
                    return self._stream_generate(prompt, max_tokens, temperature)

                response = self._complete(prompt, max_tokens, temperature=temperature)
                return response.choices[0].message.content or ""
            except Exception as exc:
                exc_str = str(exc).lower()
                is_rate_limit = (
                    "429" in exc_str
                    or "rate_limit" in exc_str
                    or "too_many_requests" in exc_str
                )

                if is_rate_limit and retries < max_retries:
                    log.warning(
                        "Rate limited by Groq. Retrying in %ss. Attempt %d/%d",
                        backoff,
                        retries + 1,
                        max_retries,
                    )
                    time.sleep(backoff)
                    retries += 1
                    backoff *= 2
                    continue

                log.error("Groq generation error. Attempt %d: %s", retries + 1, exc)
                if retries >= max_retries:
                    raise

                retries += 1
                time.sleep(1)

        return ""

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
