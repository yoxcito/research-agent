from __future__ import annotations

from typing import Any

from research_agent.json_utils import compact_json
from research_agent.models import AgentMemory, AgentPersona
from research_agent.openrouter import OpenRouterClient


class ResearchAgent:
    def __init__(self, persona: AgentPersona, client: OpenRouterClient) -> None:
        self.persona = persona
        self.client = client
        self.memory = AgentMemory(persona_key=persona.key)

    def independent_research(self, problem: dict[str, Any]) -> dict[str, Any]:
        response = self.client.complete_json(
            [
                {"role": "system", "content": self._system_prompt()},
                {
                    "role": "user",
                    "content": (
                        "Phase 1: independently research the problem statement. Do not infer that other agents agree with you. "
                        "Return only JSON with these keys: key_findings, evidence, sources, assumptions, claims, proposed_solutions, "
                        "risks, questions, uncertainties, existing_solutions, research_gaps, feasibility_issues, potential_improvements. "
                        "Classify important claims as verified_fact, strongly_supported_claim, reasonable_assumption, opinion, "
                        "speculation, or unknown. Never invent citations. Problem statement JSON:\n"
                        f"{compact_json(problem)}"
                    ),
                },
            ],
            max_tokens=7000,
        )
        self.memory.independent_research = response
        return response

    def cross_examine(
        self,
        problem: dict[str, Any],
        all_research: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        others = {key: value for key, value in all_research.items() if key != self.persona.key}
        response = self.client.complete_json(
            [
                {"role": "system", "content": self._system_prompt()},
                {
                    "role": "user",
                    "content": (
                        "Phase 2: cross-examine the other agents' findings. Return only JSON. "
                        "Use the labels AGREE, DISAGREE, UNSUPPORTED, MISSING, CONTRADICTORY, NEEDS_VERIFICATION exactly. "
                        "For each reviewed agent, identify challenged claims, reasons, evidence status, and what would verify or falsify it. "
                        "Also state which of your own initial claims need revision. Problem statement:\n"
                        f"{compact_json(problem)}\n\nOther agents' findings:\n{compact_json(others)}"
                    ),
                },
            ],
            max_tokens=7000,
        )
        self.memory.cross_examination = response
        return response

    def debate(
        self,
        problem: dict[str, Any],
        round_number: int,
        instruction: str,
        transcript: list[dict[str, Any]],
        shared_context: dict[str, Any],
    ) -> dict[str, Any]:
        response = self.client.complete_json(
            [
                {"role": "system", "content": self._system_prompt()},
                {
                    "role": "user",
                    "content": (
                        f"Phase 3 debate, round {round_number}. {instruction} "
                        "Respond to the live transcript and shared findings. Return only JSON with keys: position, strongest_arguments, "
                        "criticisms, concessions, unresolved_disagreements, evidence_needed, updates_to_prior_claims, consensus_recommendation. "
                        "Preserve justified disagreement; do not force consensus.\n\nProblem:\n"
                        f"{compact_json(problem)}\n\nShared context:\n{compact_json(shared_context)}\n\nTranscript so far:\n{compact_json(transcript)}"
                    ),
                },
            ],
            max_tokens=6500,
        )
        self.memory.debate_notes.append(response)
        return response

    def _system_prompt(self) -> str:
        responsibilities = "\n".join(f"- {item}" for item in self.persona.responsibilities)
        return (
            f"You are {self.persona.name}.\n"
            f"Alter ego: {self.persona.alter_ego}\n"
            f"Role: {self.persona.role}\n"
            f"Personality: {self.persona.personality}\n"
            f"Expertise: {self.persona.expertise}\n"
            f"Research bias: {self.persona.research_bias}\n"
            f"Responsibilities:\n{responsibilities}\n\n"
            "You are part of a four-agent adversarial research team. Be specific, evidence-aware, and rigorous. "
            "Separate verified facts from assumptions, opinion, speculation, and unknowns. Prefer official government sources, "
            "academic papers, peer-reviewed research, official documentation, reputable institutions, industry reports, and high-quality journalism. "
            "Do not fabricate source titles, URLs, statistics, or citations."
        )
