from __future__ import annotations

from typing import Any
import concurrent.futures

from research_agent.agents.agent import ResearchAgent
from research_agent.agents.personas import AGENT_PERSONAS
from research_agent.config.settings import Settings
from research_agent.json_utils import compact_json
from research_agent.models import ResearchSession
from research_agent.openrouter import OpenRouterClient
from research_agent.source_tools import check_source_urls, collect_urls


class ResearchOrchestrator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = OpenRouterClient(settings)
        self.agents = [ResearchAgent(persona, self.client) for persona in AGENT_PERSONAS]
        if len(self.agents) != 4:
            raise RuntimeError("The system must launch exactly four research agents.")

    def run(self, problem: dict[str, Any]) -> ResearchSession:
        independent = self._run_parallel("independent research", lambda agent: agent.independent_research(problem))
        cross_exams = self._run_parallel(
            "cross examination",
            lambda agent: agent.cross_examine(problem, independent),
        )
        debate_rounds = self._run_debate(problem, independent, cross_exams)
        source_checks = self._check_sources(independent, cross_exams, debate_rounds)
        verification = self._verify_evidence(problem, independent, cross_exams, debate_rounds, source_checks)
        consensus = self._build_consensus(problem, independent, cross_exams, debate_rounds, verification)
        paper = self._synthesize_paper(problem, independent, cross_exams, debate_rounds, verification, consensus)
        questions = self._generate_questions(problem, independent, cross_exams, debate_rounds, consensus, paper)
        quality = self._quality_control(problem, paper, questions, independent, cross_exams, debate_rounds, verification, consensus)

        if not quality.get("ready_to_publish", False):
            revision = self._revise_outputs(problem, paper, questions, quality, verification, consensus)
            paper = str(revision.get("research_paper", paper)).strip()
            revised_questions = revision.get("questions_json")
            if isinstance(revised_questions, dict) and isinstance(revised_questions.get("questions"), list):
                questions = revised_questions
            quality = self._quality_control(problem, paper, questions, independent, cross_exams, debate_rounds, verification, consensus)

        return ResearchSession(
            problem=problem,
            independent_research=independent,
            cross_examinations=cross_exams,
            debate_rounds=debate_rounds,
            verification=verification,
            consensus=consensus,
            paper=paper,
            questions=questions,
            quality_control=quality,
        )

    def _run_parallel(self, phase: str, task: Any) -> dict[str, dict[str, Any]]:
        results: dict[str, dict[str, Any]] = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(task, agent): agent for agent in self.agents}
            for future in concurrent.futures.as_completed(futures):
                agent = futures[future]
                try:
                    results[agent.persona.key] = future.result()
                except Exception as exc:
                    results[agent.persona.key] = self._fallback_agent_result(agent, phase, exc)
        return results

    def _fallback_agent_result(self, agent: ResearchAgent, phase: str, exc: Exception) -> dict[str, Any]:
        return {
            "agent": agent.persona.name,
            "phase": phase,
            "status": "partial_failure",
            "error": str(exc),
            "key_findings": [],
            "evidence": [],
            "sources": [],
            "assumptions": [],
            "claims": [],
            "risks": ["This agent failed after configured retries; synthesis must not treat its missing output as agreement."],
            "questions": [],
            "uncertainties": ["Agent output unavailable because of API or response parsing failure."],
        }

    def _run_debate(
        self,
        problem: dict[str, Any],
        independent: dict[str, dict[str, Any]],
        cross_exams: dict[str, dict[str, Any]],
    ) -> list[dict[str, Any]]:
        transcript: list[dict[str, Any]] = []
        instructions = [
            ("lead_researcher", "Present the research foundation and the strongest evidence-backed findings."),
            ("skeptic", "Attack weak claims, unsupported assumptions, contradictions, and optimistic conclusions."),
            ("domain_expert", "Evaluate technical feasibility, production constraints, architecture, security, reliability, and cost."),
            ("contrarian", "Propose alternative interpretations, unconventional approaches, and overlooked opportunities."),
            ("all", "Respond to the strongest criticisms and revise any weak prior claims."),
            ("all", "Attempt a research consensus while preserving unresolved disagreements."),
        ]
        shared_context = {"independent_research": independent, "cross_examinations": cross_exams}
        for round_number, (target, instruction) in enumerate(instructions[: self.settings.debate_rounds], start=1):
            participants = self.agents if target == "all" else [agent for agent in self.agents if agent.persona.key == target]
            for agent in participants:
                try:
                    response = agent.debate(problem, round_number, instruction, transcript, shared_context)
                except Exception as exc:
                    response = self._fallback_agent_result(agent, f"debate round {round_number}", exc)
                entry = {"round": round_number, "agent": agent.persona.key, "instruction": instruction, "response": response}
                transcript.append(entry)
        return transcript

    def _verify_evidence(
        self,
        problem: dict[str, Any],
        independent: dict[str, dict[str, Any]],
        cross_exams: dict[str, dict[str, Any]],
        debate_rounds: list[dict[str, Any]],
        source_checks: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return self.client.complete_json(
            [
                {"role": "system", "content": VERIFIER_PROMPT},
                {
                    "role": "user",
                    "content": (
                        "Evaluate evidence quality. Return only JSON with keys: verified_facts, strongly_supported_claims, "
                        "reasonable_assumptions, opinions, speculation, unknowns, unsupported_claims, contradictions, "
                        "source_quality_notes, corroboration_needed, safe_final_claims. Do not upgrade claims without evidence.\n\n"
                        f"Problem:\n{compact_json(problem)}\n\nIndependent research:\n{compact_json(independent)}\n\n"
                        f"Cross examinations:\n{compact_json(cross_exams)}\n\nDebate:\n{compact_json(debate_rounds)}\n\n"
                        f"Source URL availability checks:\n{compact_json(source_checks)}"
                    ),
                },
            ],
            max_tokens=7500,
        )

    def _check_sources(
        self,
        independent: dict[str, dict[str, Any]],
        cross_exams: dict[str, dict[str, Any]],
        debate_rounds: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        urls = collect_urls(
            {"independent": independent, "cross_exams": cross_exams, "debate_rounds": debate_rounds},
            limit=40,
        )
        return check_source_urls(urls[:25])

    def _build_consensus(
        self,
        problem: dict[str, Any],
        independent: dict[str, dict[str, Any]],
        cross_exams: dict[str, dict[str, Any]],
        debate_rounds: list[dict[str, Any]],
        verification: dict[str, Any],
    ) -> dict[str, Any]:
        return self.client.complete_json(
            [
                {"role": "system", "content": CONSENSUS_PROMPT},
                {
                    "role": "user",
                    "content": (
                        "Produce a consensus and disagreement map. Return only JSON with keys: consensus_points, unresolved_disagreements, "
                        "rejected_claims, strongest_proposed_approaches, implementation_priorities, research_gaps, feasibility_summary, "
                        "security_privacy_summary, scalability_summary, cost_summary.\n\n"
                        f"Problem:\n{compact_json(problem)}\n\nIndependent research:\n{compact_json(independent)}\n\nCross examinations:\n"
                        f"{compact_json(cross_exams)}\n\nDebate:\n{compact_json(debate_rounds)}\n\nVerification:\n{compact_json(verification)}"
                    ),
                },
            ],
            max_tokens=7000,
        )

    def _synthesize_paper(
        self,
        problem: dict[str, Any],
        independent: dict[str, dict[str, Any]],
        cross_exams: dict[str, dict[str, Any]],
        debate_rounds: list[dict[str, Any]],
        verification: dict[str, Any],
        consensus: dict[str, Any],
    ) -> str:
        return self.client.complete(
            [
                {"role": "system", "content": SYNTHESIS_PROMPT},
                {
                    "role": "user",
                    "content": (
                        "Write the final research paper for research.txt. Include only the paper. Use a natural human academic style. "
                        "Adapt sections to the actual problem instead of blindly including every possible heading. Avoid fake citations and "
                        "avoid internal agent conversation. References must only include sources present in the research artifacts or clearly "
                        "identified institutional/documentation categories when exact bibliographic details are unavailable.\n\n"
                        f"Problem:\n{compact_json(problem)}\n\nIndependent research:\n{compact_json(independent)}\n\n"
                        f"Cross examinations:\n{compact_json(cross_exams)}\n\nDebate:\n{compact_json(debate_rounds)}\n\n"
                        f"Verification:\n{compact_json(verification)}\n\nConsensus:\n{compact_json(consensus)}"
                    ),
                },
            ],
            temperature=0.45,
            max_tokens=12000,
        )

    def _generate_questions(
        self,
        problem: dict[str, Any],
        independent: dict[str, dict[str, Any]],
        cross_exams: dict[str, dict[str, Any]],
        debate_rounds: list[dict[str, Any]],
        consensus: dict[str, Any],
        paper: str,
    ) -> dict[str, Any]:
        response = self.client.complete_json(
            [
                {"role": "system", "content": QUESTION_PROMPT},
                {
                    "role": "user",
                    "content": (
                        "Generate questions.json. Return only JSON with a top-level questions array. Each item must contain question, "
                        "category, and difficulty. Generate at least 75 questions unless the topic truly cannot support that many. "
                        "Include easy, medium, hard, and expert-level questions. Questions must be specific to this problem, including "
                        "adversarial and viva-style questions.\n\n"
                        f"Problem:\n{compact_json(problem)}\n\nResearch paper:\n{paper}\n\nConsensus:\n{compact_json(consensus)}\n\n"
                        f"Research artifacts:\n{compact_json({'independent': independent, 'cross_exams': cross_exams, 'debate': debate_rounds})}"
                    ),
                },
            ],
            max_tokens=9000,
        )
        questions = response.get("questions")
        if not isinstance(questions, list) or not questions:
            raise ValueError("Question generation did not return a non-empty questions array.")
        if len(questions) < 30:
            raise ValueError("Question generation returned too few questions for a comprehensive bank.")
        return response

    def _quality_control(
        self,
        problem: dict[str, Any],
        paper: str,
        questions: dict[str, Any],
        independent: dict[str, dict[str, Any]],
        cross_exams: dict[str, dict[str, Any]],
        debate_rounds: list[dict[str, Any]],
        verification: dict[str, Any],
        consensus: dict[str, Any],
    ) -> dict[str, Any]:
        return self.client.complete_json(
            [
                {"role": "system", "content": QUALITY_PROMPT},
                {
                    "role": "user",
                    "content": (
                        "Perform final quality control. Return only JSON with keys: ready_to_publish, research_quality, technical_quality, "
                        "writing_quality, question_quality, required_revisions, residual_risks. Be strict.\n\n"
                        f"Problem:\n{compact_json(problem)}\n\nPaper:\n{paper}\n\nQuestions:\n{compact_json(questions)}\n\n"
                        f"Verification:\n{compact_json(verification)}\n\nConsensus:\n{compact_json(consensus)}\n\nDebate:\n{compact_json(debate_rounds)}\n\n"
                        f"Independent research:\n{compact_json(independent)}\n\nCross examinations:\n{compact_json(cross_exams)}"
                    ),
                },
            ],
            max_tokens=7000,
        )

    def _revise_outputs(
        self,
        problem: dict[str, Any],
        paper: str,
        questions: dict[str, Any],
        quality: dict[str, Any],
        verification: dict[str, Any],
        consensus: dict[str, Any],
    ) -> dict[str, Any]:
        return self.client.complete_json(
            [
                {"role": "system", "content": REVISION_PROMPT},
                {
                    "role": "user",
                    "content": (
                        "Revise the outputs according to the quality-control findings. Return only JSON with keys research_paper and "
                        "questions_json. questions_json must have top-level questions array.\n\n"
                        f"Problem:\n{compact_json(problem)}\n\nCurrent paper:\n{paper}\n\nCurrent questions:\n{compact_json(questions)}\n\n"
                        f"Quality control:\n{compact_json(quality)}\n\nVerification:\n{compact_json(verification)}\n\nConsensus:\n{compact_json(consensus)}"
                    ),
                },
            ],
            temperature=0.35,
            max_tokens=13000,
        )


VERIFIER_PROMPT = (
    "You are an evidence verification analyst. Your task is to classify claims into verified facts, strongly supported claims, "
    "reasonable assumptions, opinions, speculation, and unknowns. Important factual claims need corroboration when possible. "
    "Never invent sources or treat speculation as fact."
)

CONSENSUS_PROMPT = (
    "You are a research chair synthesizing a debate. Preserve legitimate disagreement. Separate consensus, contested claims, "
    "rejected claims, and unknowns. Focus on research quality, feasibility, security, scalability, cost, and gaps."
)

SYNTHESIS_PROMPT = (
    "You are a senior academic research writer. Write in a clear human academic style with precise qualification. Avoid filler, "
    "repetitive AI phrasing, obvious template language, excessive bullets, unsupported statistics, fake citations, and dramatic language. "
    "Use only supportable claims. Internal debate artifacts inform the paper but must not appear as transcript."
)

QUESTION_PROMPT = (
    "You create comprehensive, topic-specific examination and research-defense question banks. Include General Understanding, Problem "
    "Statement, Background, Existing Solutions, Technology, AI/ML, Architecture, Implementation, Data, GIS, Security, Scalability, Cost, "
    "Feasibility, Limitations, Risks, Government/Policy, Real-world Deployment, Innovation, Future Scope, Critical Thinking, Defense / Viva, "
    "and Adversarial Questions where relevant."
)

QUALITY_PROMPT = (
    "You are a strict final quality-control reviewer. Check research quality, technical quality, writing quality, and question quality. "
    "Flag unsupported claims, weak sources, contradictions, missing counterarguments, unrealistic implementation assumptions, security gaps, "
    "scalability gaps, repetition, fake citations, generic questions, and missing difficulty coverage."
)

REVISION_PROMPT = (
    "You revise research deliverables based on quality-control findings. Remove or qualify unsupported claims. Improve coherence, source "
    "discipline, technical realism, and question coverage. Preserve a natural academic style."
)
