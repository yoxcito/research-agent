## Multi-Agent Research & Debate System

I want you to build a **fully functional multi-agent research system** that performs deep, adversarial research on a given problem statement and produces a human-readable research paper along with a comprehensive question bank.

### 1. Core Requirements

The system must:

1. Read the research/problem statement from:
   `problem_statement.json`
2. Use an **OpenAI-compatible API through OpenRouter**.
3. Launch exactly **4 independent AI research agents**.
4. Give each agent a distinct **alter ego, personality, expertise, and research bias**.
5. Make the four agents independently research the problem and then **communicate, challenge, criticize, and debate each other's findings**.
6. Force agents to identify:

   * Unsupported claims
   * Weak assumptions
   * Missing information
   * Contradictions
   * Technical limitations
   * Existing solutions
   * Research gaps
   * Feasibility issues
   * Potential improvements
7. After the debate, have the system synthesize the strongest verified findings into a coherent research paper.
8. Generate a comprehensive `questions.json` containing questions that could reasonably be asked about the topic.
9. The final research paper must be written in a **natural human academic style**, avoiding repetitive AI-generated phrasing, unnecessary headings, filler, and obvious LLM patterns.

---

# 2. Problem Statement Input

The application must read:

```text
problem_statement.json
```

The JSON will contain the complete problem statement and relevant context.

The agents must treat this file as the **single source of truth for understanding the actual problem being researched**.

Do not hardcode the problem statement into the application.

The system should be able to work with a completely different problem statement simply by replacing `problem_statement.json`.

---

# 3. Four Research Agents

Create exactly four agents.

Each agent must have a strong and clearly differentiated alter ego.

### Agent 1 — The Lead Researcher

Role:

* Academic researcher
* Evidence-focused
* Methodical and neutral
* Focuses on understanding the problem deeply

Responsibilities:

* Research the background and context
* Identify existing research
* Find relevant technologies and methodologies
* Identify important facts and statistics
* Establish the current state of the field
* Build the initial research foundation

Personality:
Calm, analytical, methodical, evidence-driven.

---

### Agent 2 — The Skeptic

Role:

* Aggressive critical researcher
* Devil's advocate
* Assumes that claims may be incorrect until proven

Responsibilities:

* Attack Agent 1's findings
* Identify unsupported claims
* Challenge assumptions
* Search for contradictory evidence
* Find limitations and edge cases
* Identify reasons why proposed approaches may fail
* Look for overlooked risks

Personality:
Confrontational, skeptical, brutally logical.

The Skeptic should actively disagree with the other agents when there is legitimate evidence to do so.

---

### Agent 3 — The Domain Expert

Role:

* Specialist in the technical/domain aspects of the problem

Responsibilities:

* Analyze technical feasibility
* Examine architecture and implementation possibilities
* Compare existing technologies and solutions
* Identify industry-standard approaches
* Investigate real-world constraints
* Evaluate scalability, reliability, security, cost, and deployment challenges

Personality:
Highly technical, experienced, pragmatic, occasionally arrogant.

The Domain Expert should challenge unrealistic ideas and explain what would actually work in production.

---

### Agent 4 — The Contrarian / Innovation Strategist

Role:

* Independent thinker
* Innovation researcher
* Strategic analyst

Responsibilities:

* Search for unconventional approaches
* Identify alternative solutions
* Compare competing approaches
* Find overlooked opportunities
* Identify research gaps
* Explore future possibilities
* Challenge the consensus of the other three agents

Personality:
Creative, provocative, contrarian, strategic.

The Contrarian should deliberately challenge the group's consensus when a better alternative exists.

---

# 4. Multi-Agent Debate

Do NOT simply run four agents independently and merge their responses.

The agents must actually **interact with each other**.

Implement a structured debate.

### Phase 1 — Independent Research

All four agents independently analyze:

```text
problem_statement.json
```

They should not see the other agents' conclusions during this phase.

Each agent should produce:

* Key findings
* Evidence
* Sources
* Assumptions
* Claims
* Proposed solutions
* Risks
* Questions
* Uncertainties

---

### Phase 2 — Cross Examination

Share the research outputs between the agents.

Each agent must review the other agents' findings.

They should explicitly identify:

```text
AGREE
DISAGREE
UNSUPPORTED
MISSING
CONTRADICTORY
NEEDS_VERIFICATION
```

Agents must provide reasoning for disagreements.

---

### Phase 3 — Debate

Run multiple rounds of discussion.

Example:

```text
Round 1:
Agent 1 presents findings.

Round 2:
Agent 2 attacks Agent 1's findings.

Round 3:
Agent 3 evaluates the technical arguments.

Round 4:
Agent 4 proposes alternative interpretations.

Round 5:
All agents respond to the strongest criticisms.

Round 6:
Agents attempt to reach a research consensus.
```

Do not force consensus.

If agents disagree after reviewing the evidence, preserve the disagreement and explain it in the final research.

The goal is **truth and research quality, not agreement**.

---

# 5. Evidence Verification

The system must distinguish between:

* Verified facts
* Strongly supported claims
* Reasonable assumptions
* Agent opinions
* Speculation
* Unknown information

Never present speculation as fact.

When possible, prioritize:

1. Official government sources
2. Academic papers
3. Peer-reviewed research
4. Official technical documentation
5. Reputable institutions
6. Industry reports
7. High-quality journalism

Avoid relying on a single source for important claims.

For important factual claims, attempt to obtain corroboration.

---

# 6. Research Synthesis

After the debate, create a final synthesis agent/process.

The synthesis must analyze the complete debate and produce the final research paper.

The paper should contain, where applicable:

1. Title
2. Abstract
3. Introduction
4. Problem Background
5. Problem Analysis
6. Existing Solutions / Related Work
7. Current Technology Landscape
8. Proposed Approaches
9. Comparative Analysis
10. Technical Feasibility
11. Architecture / System Design
12. Data Requirements
13. AI/ML Components
14. Implementation Strategy
15. Challenges and Limitations
16. Security and Privacy Considerations
17. Scalability
18. Cost Considerations
19. Research Gaps
20. Future Scope
21. Conclusion
22. References

Do not blindly include every section.

The structure should adapt to the actual problem.

The paper should read like it was written by a competent human researcher.

Avoid:

* Excessive bullet points
* Repetitive conclusions
* Generic AI phrases
* Fake citations
* Unsupported statistics
* Overly dramatic language
* Unnecessary verbosity

---

# 7. Research Paper Output

Write the final research paper to:

```text
research.txt
```

The file must contain only the final research paper.

It should be:

* Human-readable
* Academically structured
* Factually grounded
* Clear
* Precise
* Well argued
* Properly referenced

Do not include internal agent conversations in `research.txt`.

---

# 8. Question Generation

Generate:

```text
questions.json
```

This file should contain a comprehensive set of questions that someone could reasonably ask about the research topic.

Cover multiple categories:

```json
{
  "questions": [
    {
      "question": "...",
      "category": "General",
      "difficulty": "Easy"
    }
  ]
}
```

Generate questions across categories such as:

* General Understanding
* Problem Statement
* Background
* Existing Solutions
* Technology
* AI/ML
* Architecture
* Implementation
* Data
* GIS
* Security
* Scalability
* Cost
* Feasibility
* Limitations
* Risks
* Government/Policy
* Real-world Deployment
* Innovation
* Future Scope
* Critical Thinking
* Defense / Viva
* Adversarial Questions

Include both straightforward and extremely difficult questions.

The questions should be specific to the actual problem statement rather than generic questions.

---

# 9. Quality-Control Agent

Before writing the final files, perform a final quality-control pass.

The quality-control process must check:

### Research Quality

* Are important claims supported?
* Are sources credible?
* Are there contradictions?
* Were major counterarguments considered?
* Were existing solutions investigated?
* Were research gaps identified?

### Technical Quality

* Is the proposed approach technically feasible?
* Are implementation assumptions realistic?
* Are scalability and security considered?
* Are limitations acknowledged?

### Writing Quality

* Does the paper sound human?
* Is the reasoning coherent?
* Is unnecessary repetition removed?
* Are claims appropriately qualified?
* Are citations/reference entries consistent?

### Question Quality

* Are the questions specific to the problem?
* Are multiple difficulty levels covered?
* Are adversarial/viva questions included?
* Are important areas missing?

If the quality check identifies problems, revise the research before writing the final output.

---

# 10. Configuration

Do not hardcode API keys.

Use environment variables:

```env
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=your_model_here
```

Use the OpenAI-compatible API interface provided by OpenRouter.

The model should be configurable without changing the source code.

For example:

```text
OPENROUTER_MODEL=openai/gpt-...
```

The application should gracefully handle:

* API failures
* Rate limits
* Timeouts
* Invalid responses
* Malformed JSON
* Empty responses
* Partial agent failures

If one agent fails, the system should retry intelligently rather than immediately terminating the entire research process.

---

# 11. Project Architecture

Design the application as a clean, modular system.

Suggested structure:

```text
research-agent/
│
├── agents/
│   ├── lead_researcher
│   ├── skeptic
│   ├── domain_expert
│   └── contrarian
│
├── research/
│   ├── researcher
│   ├── debate
│   ├── verification
│   └── synthesis
│
├── config/
│   └── settings
│
├── input/
│   └── problem_statement.json
│
├── output/
│   ├── research.txt
│   └── questions.json
│
├── prompts/
│   └── agent_prompts
│
├── main
├── requirements
└── README
```

You may modify this architecture if you have a cleaner approach.

---

# 12. Important Design Principle

This is NOT supposed to be four chatbots generating four essays.

It should behave like a **virtual research team**.

The workflow should resemble:

```text
Problem Statement
       ↓
┌─────────────────────────────┐
│     Independent Research    │
├─────────┬─────────┬─────────┤
│ Agent 1 │ Agent 2 │ Agent 3 │ Agent 4
└─────────┴─────────┴─────────┘
       ↓
Cross Examination
       ↓
Adversarial Debate
       ↓
Evidence Verification
       ↓
Consensus / Disagreement Analysis
       ↓
Research Synthesis
       ↓
Quality Control
       ↓
┌───────────────────┬──────────────────┐
│   research.txt    │  questions.json  │
└───────────────────┴──────────────────┘
```

The agents should have **memory of the current research session**, allowing them to refer to previous arguments and evidence during the debate.

Keep the implementation extensible so that additional agents, research phases, models, or output formats can be added later.

---

# 13. Final Requirement

Build the complete working implementation, not a prototype or pseudocode.

Do not leave major components as TODOs.

Include:

* Complete source code
* Agent prompts
* API integration
* Configuration
* Error handling
* Debate orchestration
* Research synthesis
* Question generation
* Output generation
* README with setup and execution instructions
* Example `problem_statement.json`

The final system should be runnable locally with a single clear command after installing dependencies and configuring the OpenRouter API key.
