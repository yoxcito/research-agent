from __future__ import annotations

from typing import Any
from dataclasses import dataclass, field


@dataclass(frozen=True)
class AgentPersona:
    key: str
    name: str
    alter_ego: str
    role: str
    personality: str
    expertise: str
    research_bias: str
    responsibilities: tuple[str, ...]


@dataclass
class AgentMemory:
    persona_key: str
    independent_research: dict[str, Any] | None = None
    cross_examination: dict[str, Any] | None = None
    debate_notes: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ResearchSession:
    problem: dict[str, Any]
    independent_research: dict[str, dict[str, Any]]
    cross_examinations: dict[str, dict[str, Any]]
    debate_rounds: list[dict[str, Any]]
    verification: dict[str, Any]
    consensus: dict[str, Any]
    paper: str
    questions: dict[str, Any]
    quality_control: dict[str, Any]
