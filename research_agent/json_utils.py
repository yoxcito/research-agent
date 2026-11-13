from __future__ import annotations

import re
import json
from typing import Any


_FENCED_JSON_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def extract_json_object(text: str) -> dict[str, Any]:
    parsed = _parse_json(text)
    if isinstance(parsed, dict):
        return parsed

    for match in _FENCED_JSON_RE.findall(text):
        parsed = _parse_json(match)
        if isinstance(parsed, dict):
            return parsed

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        parsed = _parse_json(text[start : end + 1])
        if isinstance(parsed, dict):
            return parsed

    raise ValueError("Model response did not contain a valid JSON object.")


def _parse_json(value: str) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return None


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
