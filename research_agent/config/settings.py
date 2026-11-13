from __future__ import annotations

import os
from pathlib import Path
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    api_key: str
    model: str
    base_url: str
    app_name: str
    site_url: str
    problem_path: Path
    research_output_path: Path
    questions_output_path: Path
    max_retries: int
    timeout_seconds: float
    debate_rounds: int
    temperature: float

    @classmethod
    def from_env(
        cls,
        problem_path: str | None = None,
        research_output_path: str | None = None,
        questions_output_path: str | None = None,
    ) -> "Settings":
        api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is not set. Export it before running the research system."
            )

        return cls(
            api_key=api_key,
            model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini").strip(),
            base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/"),
            app_name=os.getenv("OPENROUTER_APP_NAME", "multi-agent-research-system"),
            site_url=os.getenv("OPENROUTER_SITE_URL", "http://localhost"),
            problem_path=Path(problem_path or os.getenv("PROBLEM_STATEMENT_PATH", "problem_statement.json")),
            research_output_path=Path(research_output_path or os.getenv("RESEARCH_OUTPUT_PATH", "research.txt")),
            questions_output_path=Path(questions_output_path or os.getenv("QUESTIONS_OUTPUT_PATH", "questions.json")),
            max_retries=max(1, int(os.getenv("OPENROUTER_MAX_RETRIES", "4"))),
            timeout_seconds=float(os.getenv("OPENROUTER_TIMEOUT_SECONDS", "120")),
            debate_rounds=max(1, int(os.getenv("DEBATE_ROUNDS", "6"))),
            temperature=float(os.getenv("OPENROUTER_TEMPERATURE", "0.35")),
        )
