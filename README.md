# Dossier

Dossier is a case-preparation assistant for the cash-evidence financial-requirement portion of a UK Student visa application. It turns a small set of confirmed case facts into a cited, deterministic assessment and makes uncertainty visible for human review.

It is not legal advice and does not submit an application or make an immigration decision.

## What is implemented

- A versioned rule graph for the relevant Student and Finance Rules paragraphs.
- A pure-Python assessment engine for maintenance funds, the 28-day holding period, evidence recency, and the limited in-country exemption.
- The ST 12.4 sponsor-accommodation offset, capped at £1,529.
- A structured interview and correction-ready case notebook.
- Boundary tests for the financial rules and a guard that keeps the decision engine independent of agent code.

The committed cash-evidence graph was reviewed against the live official pages on 24 August 2026. Immigration rules can change, so confirm the cited sources before relying on an assessment.

This version does not assess the distinct student-loan or official-sponsorship routes.

## Run the tests

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest tests/ -v
```

## Run locally

```bash
.venv/bin/uvicorn console.main:app --reload
```

Open `http://127.0.0.1:8000`. The Interview screen saves only confirmed facts;
the Dossier screen recalculates the cited result and displays the latest local
morning briefing. Local case data stays in `data/` and is not committed.

## Project layout

```text
rulebook/  cited rule graph and graph loader
engine/    deterministic financial assessment
agents/    interview, evidence extraction, and shared case notebook
jobs/      idempotent nightly recheck and morning briefing
console/   two-screen FastAPI interface
tests/     boundary and architecture tests
data/      local runtime data (not committed)
```

## Rule sources

- [Immigration Rules: Appendix Student](https://www.gov.uk/guidance/immigration-rules/appendix-student)
- [Immigration Rules: Appendix Finance](https://www.gov.uk/guidance/immigration-rules/immigration-rules-appendix-finance)

The [guidance audit](docs/GUIDANCE_AUDIT.md) recorded four current and two
outdated public guidance pages on 24 August 2026. It reports the aggregate
result only; no organisation is named or contacted automatically.

## Cost guardrail

The associated Google Cloud project currently has billing disabled. The deterministic engine and tests run locally without cloud services. Any future cloud or model integration must remain disabled until a verified free credit or billing arrangement is deliberately enabled.
