from __future__ import annotations

import sys
import argparse
from dotenv import load_dotenv

from research_agent.config.settings import Settings
from research_agent.io import read_problem_statement, write_json, write_text
from research_agent.research.orchestrator import ResearchOrchestrator

load_dotenv()

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a four-agent adversarial research system over problem_statement.json."
    )
    parser.add_argument(
        "--problem",
        default=None,
        help="Path to problem_statement.json. Defaults to PROBLEM_STATEMENT_PATH or ./problem_statement.json.",
    )
    parser.add_argument(
        "--research-output",
        default=None,
        help="Path for the final research paper. Defaults to RESEARCH_OUTPUT_PATH or ./research.txt.",
    )
    parser.add_argument(
        "--questions-output",
        default=None,
        help="Path for the generated question bank. Defaults to QUESTIONS_OUTPUT_PATH or ./questions.json.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        settings = Settings.from_env(
            problem_path=args.problem,
            research_output_path=args.research_output,
            questions_output_path=args.questions_output,
        )
        problem = read_problem_statement(settings.problem_path)
        print(f"Loaded problem statement from {settings.problem_path}")
        print(f"Using OpenRouter model: {settings.model}")

        orchestrator = ResearchOrchestrator(settings)
        session = orchestrator.run(problem)

        write_text(settings.research_output_path, session.paper)
        write_json(settings.questions_output_path, session.questions)

        print(f"Wrote research paper to {settings.research_output_path}")
        print(f"Wrote question bank to {settings.questions_output_path}")
        if not session.quality_control.get("ready_to_publish", False):
            print("Quality control still reported residual issues; see model output quality notes in memory/logs.")
        return 0
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
