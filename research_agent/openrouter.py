from __future__ import annotations

import json
import time
import random
import urllib.error
import urllib.request
from typing import Any

from research_agent.config.settings import Settings
from research_agent.json_utils import extract_json_object


class OpenRouterError(RuntimeError):
    pass


class OpenRouterClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def complete(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float | None = None,
        expect_json: bool = False,
        max_tokens: int = 6000,
    ) -> str:
        payload: dict[str, Any] = {
            "model": self.settings.model,
            "messages": messages,
            "temperature": self.settings.temperature if temperature is None else temperature,
            "max_tokens": max_tokens,
        }
        if expect_json:
            payload["response_format"] = {"type": "json_object"}

        raw = self._post_json("/chat/completions", payload)
        try:
            content = raw["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise OpenRouterError(f"Unexpected OpenRouter response shape: {raw}") from exc
        if not isinstance(content, str) or not content.strip():
            raise OpenRouterError("OpenRouter returned an empty response.")
        return content.strip()

    def complete_json(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float | None = None,
        max_tokens: int = 6000,
    ) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(1, self.settings.max_retries + 1):
            try:
                return extract_json_object(
                    self.complete(
                        messages,
                        temperature=temperature,
                        expect_json=True,
                        max_tokens=max_tokens,
                    )
                )
            except Exception as exc:
                last_error = exc
                if attempt == self.settings.max_retries:
                    break
                self._sleep(attempt)
        raise OpenRouterError(f"Could not obtain valid JSON after retries: {last_error}") from last_error

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self.settings.base_url + path,
            data=data,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.settings.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": self.settings.site_url,
                "X-Title": self.settings.app_name,
            },
        )

        last_error: Exception | None = None
        for attempt in range(1, self.settings.max_retries + 1):
            try:
                with urllib.request.urlopen(request, timeout=self.settings.timeout_seconds) as response:
                    body = response.read().decode("utf-8")
                parsed = json.loads(body)
                if not isinstance(parsed, dict):
                    raise OpenRouterError("OpenRouter response was not a JSON object.")
                return parsed
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")
                last_error = OpenRouterError(f"HTTP {exc.code}: {body[:1000]}")
                if exc.code not in {408, 409, 425, 429, 500, 502, 503, 504}:
                    break
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OpenRouterError) as exc:
                last_error = exc
            if attempt < self.settings.max_retries:
                self._sleep(attempt)
        raise OpenRouterError(f"OpenRouter request failed: {last_error}") from last_error

    @staticmethod
    def _sleep(attempt: int) -> None:
        delay = min(30.0, (2**attempt) + random.uniform(0, 1.5))
        time.sleep(delay)
