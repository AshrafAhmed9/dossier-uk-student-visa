"""Recheck a saved case without any model or cloud dependency.

Cloud Scheduler can invoke this module later. Keeping the computation local and
idempotent makes the scheduled behaviour testable while billing is disabled.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date
from pathlib import Path

from engine.gaps import CaseFacts, assess
from rulebook.graph import load_graph


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
CASE_PATH = DATA_DIR / "case.json"
BRIEFING_PATH = DATA_DIR / "morning_briefing.json"


def _date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def load_case(path: Path = CASE_PATH) -> CaseFacts:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return CaseFacts(
        study_in_london=raw.get("study_in_london"),
        course_months=raw.get("course_months"),
        outstanding_course_fees_gbp=raw.get("outstanding_course_fees_gbp"),
        sponsor_accommodation_paid_gbp=raw.get("sponsor_accommodation_paid_gbp"),
        bank_balance_gbp=raw.get("bank_balance_gbp"),
        funds_held_since=_date(raw.get("funds_held_since")),
        evidence_closing_date=_date(raw.get("evidence_closing_date")),
        months_in_uk_with_permission=raw.get("months_in_uk_with_permission"),
        applying_permission_to_stay=raw.get("applying_permission_to_stay", False),
    )


def briefing_for(facts: CaseFacts, as_of: date | None = None) -> dict:
    as_of = as_of or date.today()
    assessment = assess(load_graph(), facts, as_of)
    if assessment.eligible_now:
        summary = "The recorded facts meet the assessed financial requirements today. Check the cited rules and evidence before applying."
    elif assessment.earliest_apply_date:
        summary = f"The earliest recorded date for the 28-day condition is {assessment.earliest_apply_date.isoformat()}."
    else:
        summary = "The case is not ready yet; see the cited requirement statuses for the missing or unmet facts."
    return {
        "generated_on": as_of.isoformat(),
        "summary": summary,
        "assessment": {
            "required_funds_gbp": assessment.required_funds_gbp,
            "earliest_apply_date": assessment.earliest_apply_date.isoformat() if assessment.earliest_apply_date else None,
            "latest_apply_date": assessment.latest_apply_date.isoformat() if assessment.latest_apply_date else None,
            "eligible_now": assessment.eligible_now,
            "nodes": [
                {**asdict(node), "status": node.status, "blocked_until": node.blocked_until.isoformat() if node.blocked_until else None}
                for node in assessment.nodes
            ],
        },
    }


def run(case_path: Path = CASE_PATH, briefing_path: Path = BRIEFING_PATH, as_of: date | None = None) -> dict:
    """Recompute and atomically replace the latest briefing for one local case."""
    briefing = briefing_for(load_case(case_path), as_of)
    briefing_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = briefing_path.with_suffix(".tmp")
    temporary.write_text(json.dumps(briefing, indent=2) + "\n", encoding="utf-8")
    temporary.replace(briefing_path)
    return briefing


if __name__ == "__main__":
    if not CASE_PATH.exists():
        raise SystemExit("No local case found. Create data/case.json through the console first.")
    print(json.dumps(run(), indent=2))
