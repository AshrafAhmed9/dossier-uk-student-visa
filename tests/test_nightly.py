import json
from datetime import date

from engine.gaps import CaseFacts
from jobs.nightly import briefing_for, run


def test_briefing_names_the_earliest_date_when_balance_is_sufficient():
    briefing = briefing_for(CaseFacts(
        study_in_london=False,
        course_months=1,
        outstanding_course_fees_gbp=0,
        bank_balance_gbp=1171,
        funds_held_since=date(2026, 8, 1),
        evidence_closing_date=date(2026, 8, 20),
    ), as_of=date(2026, 8, 20))
    assert briefing["assessment"]["earliest_apply_date"] == "2026-08-28"
    assert "2026-08-28" in briefing["summary"]


def test_nightly_run_writes_a_replaceable_briefing(tmp_path):
    case_path = tmp_path / "case.json"
    briefing_path = tmp_path / "briefing.json"
    case_path.write_text(json.dumps({
        "study_in_london": False, "course_months": 1,
        "outstanding_course_fees_gbp": 0, "bank_balance_gbp": 1171,
        "funds_held_since": "2026-08-01", "evidence_closing_date": "2026-08-28",
    }))
    result = run(case_path, briefing_path, date(2026, 8, 28))
    assert result["assessment"]["eligible_now"] is True
    assert json.loads(briefing_path.read_text())["generated_on"] == "2026-08-28"
