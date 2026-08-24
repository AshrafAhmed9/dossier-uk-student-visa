# Dossier

Dossier is a case-preparation assistant for the financial-requirement portion of a UK Student visa application. It turns a small set of confirmed case facts into a cited, deterministic assessment and makes uncertainty visible for human review.

It is not legal advice and does not submit an application or make an immigration decision.

## What is implemented

- A versioned rule graph for the relevant Student and Finance Rules paragraphs.
- A pure-Python assessment engine for maintenance funds, the 28-day holding period, evidence recency, and the limited in-country exemption.
- A structured interview and correction-ready case notebook.
- Boundary tests for the financial rules and a guard that keeps the decision engine independent of agent code.

The rule graph is marked `REQUIRES_HUMAN_REVIEW`: sources and values must be checked against the official rules before relying on an assessment.

## Run the tests

```bash
python3 -m pytest tests/ -v
```

## Project layout

```text
rulebook/  cited rule graph and graph loader
engine/    deterministic financial assessment
agents/    interview, evidence extraction, and shared case notebook
tests/     boundary and architecture tests
data/      local runtime data (not committed)
```

## Rule sources

- [Immigration Rules: Appendix Student](https://www.gov.uk/guidance/immigration-rules/appendix-student)
- [Immigration Rules: Appendix Finance](https://www.gov.uk/guidance/immigration-rules/immigration-rules-appendix-finance)

## Cost guardrail

The associated Google Cloud project currently has billing disabled. The deterministic engine and tests run locally without cloud services. Any future cloud or model integration must remain disabled until a verified free credit or billing arrangement is deliberately enabled.
