from __future__ import annotations

import json
from typing import Any
from pathlib import Path


def read_problem_statement(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Problem statement file not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed problem statement JSON in {path}: {exc}") from exc
    if not isinstance(data, dict) or not data:
        raise ValueError("problem_statement.json must contain a non-empty JSON object.")
    return data


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def write_json(path: Path, content: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
