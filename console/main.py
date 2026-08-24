"""A deliberately small two-screen interface for building and reading a case.

Forms record user-confirmed facts only. The engine, not this UI or a model,
calculates all requirement statuses.
"""
from __future__ import annotations

import html
import json
import os
from datetime import date
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from agents.interviewer import choose_next_question
from agents.notebook import NoteKind, Notebook
from engine.gaps import CaseFacts, assess
from jobs.nightly import briefing_for, facts_from_raw, load_case, run
from rulebook.graph import load_graph
from storage import CaseStore


app = FastAPI(title="Dossier")
store = CaseStore()


def _case_dict(facts: CaseFacts) -> dict[str, Any]:
    values = {
        "study_in_london": facts.study_in_london,
        "course_months": facts.course_months,
        "outstanding_course_fees_gbp": facts.outstanding_course_fees_gbp,
        "sponsor_accommodation_paid_gbp": facts.sponsor_accommodation_paid_gbp,
        "bank_balance_gbp": facts.bank_balance_gbp,
        "funds_held_since": facts.funds_held_since.isoformat() if facts.funds_held_since else None,
        "evidence_closing_date": facts.evidence_closing_date.isoformat() if facts.evidence_closing_date else None,
        "months_in_uk_with_permission": facts.months_in_uk_with_permission,
        "applying_permission_to_stay": facts.applying_permission_to_stay,
    }
    return {key: value for key, value in values.items() if value is not None}


def _load_facts() -> CaseFacts:
    return facts_from_raw(store.load("case"))


def _question_style() -> str:
    return store.load("preferences").get("question_style", "clear and direct")


def _integer_or_none(value: str, label: str) -> int | None:
    if not value:
        return None
    try:
        parsed = int(value)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"{label} must be a whole number.") from exc
    if parsed < 0:
        raise HTTPException(status_code=422, detail=f"{label} cannot be negative.")
    return parsed


def _date_or_none(value: str, label: str) -> str | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"{label} must be a valid date.") from exc


def _input(name: str, value: Any, label: str, kind: str = "text") -> str:
    rendered = "" if value is None else html.escape(str(value))
    return f'<label>{label}<input type="{kind}" name="{name}" value="{rendered}"></label>'


def _layout(title: str, body: str) -> HTMLResponse:
    return HTMLResponse(f"""<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>{html.escape(title)} · Dossier</title><style>
body{{font-family:ui-sans-serif,system-ui,sans-serif;max-width:1050px;margin:2rem auto;padding:0 1rem;color:#17201c;background:#f8faf8}}a{{color:#0d5b42}}nav{{display:flex;gap:1rem;border-bottom:1px solid #cdd7d1;padding-bottom:1rem}}main{{margin-top:2rem}}.grid{{display:grid;grid-template-columns:2fr 1fr;gap:1.5rem}}@media(max-width:720px){{.grid{{grid-template-columns:1fr}}}}section,aside{{background:white;border:1px solid #d8e1dc;border-radius:8px;padding:1.25rem}}label{{display:block;margin:.7rem 0;font-weight:600}}input,select{{display:block;width:100%;box-sizing:border-box;margin-top:.25rem;padding:.5rem;border:1px solid #9dacA4;border-radius:4px}}button{{background:#0d5b42;color:white;border:0;border-radius:4px;padding:.65rem 1rem;font-weight:700;cursor:pointer}}.note{{padding:.7rem;border-left:3px solid #0d5b42;background:#edf5f0}}.warning{{padding:.7rem;border-left:3px solid #a56b00;background:#fff8e6}}.status{{text-transform:uppercase;font-size:.8rem;font-weight:700}}table{{width:100%;border-collapse:collapse}}th,td{{text-align:left;padding:.65rem;border-bottom:1px solid #e2e7e4;vertical-align:top}}</style></head><body><nav><strong>Dossier</strong><a href=\"/\">Interview</a><a href=\"/dossier\">Dossier</a></nav><main>{body}</main></body></html>""")


@app.get("/", response_class=HTMLResponse)
def interview() -> HTMLResponse:
    facts = _load_facts()
    notebook = Notebook()
    for key, value in _case_dict(facts).items():
        notebook.set(key, value, NoteKind.FACT, "user-confirmed")
    notebook.set("question_style", _question_style(), NoteKind.PREFERENCE, "user preference")
    next_question = choose_next_question(notebook)
    question = next_question.question if next_question else "All core facts are recorded. Review the Dossier."
    body = f"""
<div class=\"grid\"><section><h1>Build your case</h1><p class=\"warning\">Dossier assembles evidence and checks cited rules. It is not legal advice and does not submit an application.</p><p class=\"note\"><strong>Next question:</strong> {html.escape(question)}</p>
<form method=\"post\" action=\"/case\">
{_input("course_months", facts.course_months, "Course length (months)", "number")}
{_input("outstanding_course_fees_gbp", facts.outstanding_course_fees_gbp, "Outstanding course fees (£)", "number")}
{_input("sponsor_accommodation_paid_gbp", facts.sponsor_accommodation_paid_gbp, "Accommodation paid to your student sponsor (£, maximum offset £1,529)", "number")}
{_input("bank_balance_gbp", facts.bank_balance_gbp, "Available balance (£)", "number")}
{_input("funds_held_since", facts.funds_held_since, "Funds held at or above required amount since", "date")}
{_input("evidence_closing_date", facts.evidence_closing_date, "Most recent evidence closing date", "date")}
{_input("months_in_uk_with_permission", facts.months_in_uk_with_permission, "Months in the UK with permission", "number")}
<label>Course location<select name=\"study_in_london\"><option value=\"\">Select</option><option value=\"true\" {'selected' if facts.study_in_london else ''}>London</option><option value=\"false\" {'selected' if facts.study_in_london is False else ''}>Outside London</option></select></label>
<label><input type=\"checkbox\" name=\"applying_permission_to_stay\" {'checked' if facts.applying_permission_to_stay else ''}> I am applying from inside the UK for permission to stay</label>
<button>Save confirmed facts and recalculate</button></form></section>
<aside><h2>Notebook</h2><p>Facts are marked user-confirmed. Editing a fact reruns the assessment.</p><ul>{''.join(f'<li><strong>{html.escape(note.key)}</strong>: {html.escape(str(note.value))}</li>' for note in notebook.notes.values() if note.kind == NoteKind.FACT) or '<li>No facts recorded.</li>'}</ul>
<h2>How should Dossier ask?</h2><form method=\"post\" action=\"/preference\"><label>Question style<select name=\"question_style\"><option {'selected' if _question_style() == 'clear and direct' else ''}>clear and direct</option><option {'selected' if _question_style() == 'gentle and reassuring' else ''}>gentle and reassuring</option><option {'selected' if _question_style() == 'brief and checklist-like' else ''}>brief and checklist-like</option></select></label><button>Update preference</button></form><p>Changing this preference changes only phrasing, never the eligibility result.</p></aside></div>"""
    return _layout("Interview", body)


@app.post("/case")
def save_case(
    course_months: str = Form(""), outstanding_course_fees_gbp: str = Form(""), sponsor_accommodation_paid_gbp: str = Form(""), bank_balance_gbp: str = Form(""),
    funds_held_since: str = Form(""), evidence_closing_date: str = Form(""), months_in_uk_with_permission: str = Form(""),
    study_in_london: str = Form(""), applying_permission_to_stay: bool = Form(False),
) -> RedirectResponse:
    raw = {
        "course_months": _integer_or_none(course_months, "Course length"),
        "outstanding_course_fees_gbp": _integer_or_none(outstanding_course_fees_gbp, "Outstanding course fees"),
        "sponsor_accommodation_paid_gbp": _integer_or_none(sponsor_accommodation_paid_gbp, "Accommodation payment"),
        "bank_balance_gbp": _integer_or_none(bank_balance_gbp, "Available balance"),
        "funds_held_since": _date_or_none(funds_held_since, "Funds-held date"),
        "evidence_closing_date": _date_or_none(evidence_closing_date, "Evidence closing date"),
        "months_in_uk_with_permission": _integer_or_none(months_in_uk_with_permission, "Months in the UK"),
        "study_in_london": {"true": True, "false": False}.get(study_in_london),
        "applying_permission_to_stay": applying_permission_to_stay,
    }
    store.save("case", raw)
    return RedirectResponse("/dossier", status_code=303)


@app.post("/preference")
def save_preference(question_style: str = Form("clear and direct")) -> RedirectResponse:
    # Preferences are intentionally not mixed into CaseFacts or the legal engine.
    store.save("preferences", {"question_style": question_style})
    return RedirectResponse("/", status_code=303)


@app.post("/internal/nightly")
def scheduled_nightly(request: Request) -> JSONResponse:
    """Cloud Scheduler invokes this with an OIDC token; local calls stay simple."""
    if os.environ.get("K_SERVICE"):
        from google.auth.transport import requests
        from google.oauth2 import id_token
        authorization = request.headers.get("authorization", "")
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Scheduler authentication is required.")
        try:
            audience = os.environ.get("SCHEDULER_AUDIENCE", request.base_url._url.rstrip("/"))
            id_token.verify_oauth2_token(authorization.removeprefix("Bearer "), requests.Request(), audience=audience)
        except ValueError as exc:
            raise HTTPException(status_code=401, detail="Invalid scheduler identity.") from exc
    return JSONResponse(run())


@app.get("/dossier", response_class=HTMLResponse)
def dossier() -> HTMLResponse:
    facts = _load_facts()
    graph = load_graph()
    result = assess(graph, facts, date.today())
    briefing = briefing_for(facts)
    window = "Not available until the missing or unmet facts are resolved."
    if result.earliest_apply_date:
        end = result.latest_apply_date.isoformat() if result.latest_apply_date else "confirm with new evidence"
        window = f"{result.earliest_apply_date.isoformat()} to {end}"
    rows = "".join(f'<tr><td><a href="{html.escape(node.source_url)}">{html.escape(node.citation)}</a></td><td class="status">{html.escape(node.status)}</td><td>{html.escape(node.explanation)}</td></tr>' for node in result.nodes)
    body = f"""<section><h1>Your financial-requirement dossier</h1><p class=\"warning\">This is evidence assembly and gap-checking, not legal advice. It currently assesses the cash-evidence route, not student loans or official sponsorship. Confirm the cited rules and your evidence before applying.</p><h2>Apply-date window</h2><p class=\"note\"><strong>{html.escape(window)}</strong></p><h2>Funds calculation</h2><p>{'£' + format(result.required_funds_gbp, ',') if result.required_funds_gbp is not None else 'Awaiting course or location details.'}</p><h2>Morning briefing</h2><p>{html.escape(briefing['summary'])}</p><h2>Cited requirements</h2><table><thead><tr><th>Rule</th><th>Status</th><th>Assessment</th></tr></thead><tbody>{rows}</tbody></table><p>Rule graph review status: <strong>{html.escape(graph.review_status)}</strong>. {html.escape(graph.review_note)}</p></section>"""
    return _layout("Dossier", body)
