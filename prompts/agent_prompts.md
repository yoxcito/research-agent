# Agent Prompt Design

The implementation constructs prompts programmatically from the fixed personas in
`research_agent/agents/personas.py`. This file documents the intended behavior.

## Shared Rules

- Treat `problem_statement.json` as the single source of truth for the research topic.
- Separate verified facts, strongly supported claims, reasonable assumptions, opinions,
  speculation, and unknowns.
- Prefer official government sources, academic papers, peer-reviewed research, official
  documentation, reputable institutions, industry reports, and high-quality journalism.
- Do not fabricate source titles, URLs, citations, statistics, or consensus.
- Preserve evidence-backed disagreement.

## Phase 1: Independent Research

Each of the four agents receives only the problem statement. The expected output is
structured JSON containing findings, evidence, sources, assumptions, claims, solutions,
risks, questions, uncertainties, existing solutions, research gaps, feasibility issues,
and possible improvements.

## Phase 2: Cross Examination

Each agent receives the other agents' research and must classify claims using:

- AGREE
- DISAGREE
- UNSUPPORTED
- MISSING
- CONTRADICTORY
- NEEDS_VERIFICATION

## Phase 3: Debate

The debate is sequenced as:

1. Lead Researcher presents the foundation.
2. Skeptic attacks weak claims.
3. Domain Expert evaluates technical feasibility.
4. Contrarian proposes alternatives.
5. All agents respond to the strongest criticisms.
6. All agents attempt consensus without forcing agreement.

## Final Stages

The verifier classifies evidence. The consensus process preserves disagreements. The
synthesis process writes only the final paper. The question generator writes only
topic-specific questions. The QC process checks research, technical, writing, and question
quality and triggers revision when needed.
