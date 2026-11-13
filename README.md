# Multi-Agent Research & Debate System

This project runs a four-agent adversarial research workflow over `problem_statement.json`
and writes:

- `research.txt`: final human-readable research paper
- `questions.json`: comprehensive topic-specific question bank

The system uses an OpenAI-compatible API through OpenRouter. The model and API key are
configured by environment variables, not hardcoded.

## Workflow

1. Load `problem_statement.json`
2. Launch exactly four independent agents:
   - Lead Researcher
   - Skeptic
   - Domain Expert
   - Contrarian / Innovation Strategist
3. Run isolated independent research
4. Run cross examination with explicit labels:
   - `AGREE`
   - `DISAGREE`
   - `UNSUPPORTED`
   - `MISSING`
   - `CONTRADICTORY`
   - `NEEDS_VERIFICATION`
5. Run structured multi-round debate
6. Verify evidence and classify claims
7. Build consensus and preserve disagreements
8. Synthesize the final paper
9. Generate `questions.json`
10. Run final quality control and revise outputs if needed

## Setup

Requires Python 3.13 or newer. This repository includes `.python-version` with
`3.13`; `uv` is the easiest way to run the matching interpreter locally.

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

Configure OpenRouter:

```bash
export OPENROUTER_API_KEY="your_key_here"
export OPENROUTER_MODEL="openai/gpt-4o-mini"
```

Optional settings:

```bash
export OPENROUTER_TIMEOUT_SECONDS=120
export OPENROUTER_MAX_RETRIES=4
export DEBATE_ROUNDS=6
export RESEARCH_OUTPUT_PATH=research.txt
export QUESTIONS_OUTPUT_PATH=questions.json
```

## Run

```bash
uv run main.py
```

Custom paths:

```bash
uv run python main.py \
  --problem problem_statement.json \
  --research-output research.txt \
  --questions-output questions.json
```

## Input

The application reads `problem_statement.json` as the single source of truth. Replace that
file to research a different topic. Do not hardcode the topic in source code.

## Output

`research.txt` contains only the final paper. Internal agent conversations are not written
to that file.

`questions.json` uses this shape:

```json
{
  "questions": [
    {
      "question": "What operational problem is the platform trying to solve in remote NER districts?",
      "category": "Problem Statement",
      "difficulty": "Easy"
    }
  ]
}
```

## Notes

The system asks agents to prioritize official, academic, institutional, and reputable
sources and to avoid fabricated citations. Since OpenRouter chat models may not have live
web access, the verifier classifies claims conservatively when exact corroboration is not
available in the model output.